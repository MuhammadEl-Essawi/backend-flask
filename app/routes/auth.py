import os
import re
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import or_
from datetime import datetime, timezone

from ..extensions import db, mail, limiter
from ..models import User, OTP
from ..utils.otp_utils import (
    generate_numeric_otp, hash_otp, otp_expiry_datetime, verify_otp_hash
)
from ..utils.mail_utils import send_otp_email
from ..schemas import UserRegisterSchema, UserPublicSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def validate_password(password: str) -> str | None:
    """Returns an error message if the password is weak, or None if valid."""
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    return None

@auth_bp.route("/register", methods=["POST"])

@limiter.limit("5 per minute")

def register():

    data = request.get_json()

    if not data:

        return jsonify({"error": "No JSON data provided"}), 400



    if "email" in data and isinstance(data["email"], str):

        data["email"] = data["email"].strip().lower()



    requested_role = data.get("role", "renter")

    if isinstance(requested_role, str):

        requested_role = requested_role.strip().lower()

    

    if requested_role not in ["owner", "renter"]:

        return jsonify({"error": "Invalid role. Only 'owner' or 'renter' are allowed."}), 400

    

    data["role"] = requested_role



    # Validate password strength BEFORE schema loading

    password = data.get("password")

    if not password:

        return jsonify({"error": "Password is required"}), 400

    password_error = validate_password(password)

    if password_error:

        return jsonify({"error": password_error}), 400



    try:

        schema = UserRegisterSchema()

        new_user_data = schema.load(data)

    except ValidationError as err:

        return jsonify({"errors": err.messages}), 400

    except Exception as e:

        current_app.logger.exception(f"Schema load error: {e}")

        return jsonify({"error": "Invalid data provided"}), 400



    if User.query.filter_by(email=new_user_data.email).first():

        return jsonify({"error": "Email already registered"}), 400

    if User.query.filter_by(phone=new_user_data.phone).first():

        return jsonify({"error": "Phone number already registered"}), 400



    user = new_user_data

    user.set_password(password)

    

    user.is_active = False

    user.approval_status = "pending"



    # if user.role not in ["owner", "renter"]:

    #     user.role = "renter"



    try:

        db.session.add(user)

        db.session.commit()

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(f"Registration DB error: {e}")

        return jsonify({"error": "Registration failed"}), 400



    otp_plain = generate_numeric_otp()

    otp_hashed = hash_otp(otp_plain)

    otp_entry = OTP(

        user_id=user.id,

        otp_hash=otp_hashed,

        expires_at=otp_expiry_datetime()

    )

    db.session.add(otp_entry)

    db.session.commit()



    try:

        send_otp_email(user.email, otp_plain)

    except Exception as e:

        current_app.logger.exception(f"Failed to send OTP: {e}")

        return jsonify({"error": "Failed to send verification code"}), 500



    return jsonify({

        "message": "User created successfully. Verification code sent.",

        "user_id": user.id

    }), 201
@auth_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("10 per hour")
def verify_otp():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    otp_code = data.get("otp")

    if not user_id or not otp_code:
        return jsonify({"error": "user_id and otp are required"}), 400

    try:
        otp_entry = OTP.query.filter_by(user_id=user_id).order_by(OTP.created_at.desc()).first()
    except Exception:
        return jsonify({"error": "Invalid user_id"}), 400
    
    if not otp_entry:
        return jsonify({"error": "No OTP found for user"}), 404

    # Compare as naive datetimes to avoid MSSQL timezone issues
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = otp_entry.expires_at.replace(tzinfo=None) if otp_entry.expires_at.tzinfo else otp_entry.expires_at

    if expires_at < now_utc:
        return jsonify({"error": "OTP expired"}), 400
    
    if otp_entry.attempts >= 5:
        return jsonify({"error": "Too many attempts"}), 403

    if not verify_otp_hash(otp_entry.otp_hash, otp_code):
        otp_entry.attempts += 1
        db.session.commit()
        return jsonify({"error": "Invalid OTP"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = True
    db.session.delete(otp_entry)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "message": "Verified. Account activated.",
        "access_token": access_token,
        "user": UserPublicSchema().dump(user)
    }), 200

@auth_bp.route("/resend-otp", methods=["POST"])
@limiter.limit("3 per hour")
def resend_otp():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.is_active:
        return jsonify({"error": "Account already active"}), 400

    OTP.query.filter_by(user_id=user_id).delete()

    otp_plain = generate_numeric_otp()
    otp_hashed = hash_otp(otp_plain)
    otp_entry = OTP(
        user_id=user.id,
        otp_hash=otp_hashed,
        expires_at=otp_expiry_datetime()
    )
    db.session.add(otp_entry)
    db.session.commit()

    try:
        send_otp_email(user.email, otp_plain)
    except Exception as e:
        current_app.logger.exception(f"Failed to resend OTP: {e}")
        return jsonify({"error": "Failed to send verification code"}), 500

    return jsonify({"message": "Verification code resent."}), 200

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    
    identifier = data.get("identifier") or data.get("email")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"error": "Email/Phone and password required"}), 400

    user = User.query.filter(
        or_(User.email == identifier, User.phone == identifier)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account not verified. Please verify OTP first."}), 403

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": UserPublicSchema().dump(user)
    }), 200

@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Return generic message to prevent user enumeration
        return jsonify({"message": "If an account with that email exists, a verification code has been sent."}), 200

    otp_plain = generate_numeric_otp()
    otp_hashed = hash_otp(otp_plain)
    otp_entry = OTP(
        user_id=user.id,
        otp_hash=otp_hashed,
        expires_at=otp_expiry_datetime()
    )
    db.session.add(otp_entry)
    db.session.commit()

    try:
        send_otp_email(user.email, otp_plain)
    except Exception as e:
        current_app.logger.exception(f"Failed to send reset password OTP: {e}")
        return jsonify({"error": "Failed to send verification code"}), 500

    return jsonify({"message": "Verification code sent to your email."}), 200

@auth_bp.route("/verify-reset-code", methods=["POST"])
@limiter.limit("5 per hour")
def verify_reset_code():
    data = request.get_json() or {}
    email = data.get("email")
    otp_code = data.get("otp")

    if not email or not otp_code:
        return jsonify({"error": "Email and OTP are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_entry = OTP.query.filter_by(user_id=user.id).order_by(OTP.created_at.desc()).first()
    
    if not otp_entry:
        return jsonify({"error": "Invalid or expired code"}), 400

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = otp_entry.expires_at.replace(tzinfo=None) if otp_entry.expires_at.tzinfo else otp_entry.expires_at
    if expires_at < now_utc:
        return jsonify({"error": "Invalid or expired code"}), 400

    if not verify_otp_hash(otp_entry.otp_hash, otp_code):
        otp_entry.attempts += 1
        db.session.commit()
        return jsonify({"error": "Invalid code"}), 400

    return jsonify({"message": "Code verified successfully."}), 200

@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("3 per hour")
def reset_password():
    data = request.get_json() or {}
    email = data.get("email")
    otp_code = data.get("otp")
    new_password = data.get("new_password")

    if not all([email, otp_code, new_password]):
        return jsonify({"error": "Email, OTP, and new password are required"}), 400

    password_error = validate_password(new_password)
    if password_error:
        return jsonify({"error": password_error}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_entry = OTP.query.filter_by(user_id=user.id).order_by(OTP.created_at.desc()).first()
    
    if not otp_entry:
        return jsonify({"error": "Invalid or expired code"}), 400

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    expires_at = otp_entry.expires_at.replace(tzinfo=None) if otp_entry.expires_at.tzinfo else otp_entry.expires_at
    if expires_at < now_utc or not verify_otp_hash(otp_entry.otp_hash, otp_code):
        return jsonify({"error": "Invalid or expired code"}), 400

    user.set_password(new_password)
    
    db.session.delete(otp_entry)
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully. Please login."}), 200

@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
@limiter.limit("5 per hour")
def change_password():
    data = request.get_json() or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    password_error = validate_password(new_password)
    if password_error:
        return jsonify({"error": password_error}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200

