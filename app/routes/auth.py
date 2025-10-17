import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, mail, limiter
from ..models import User, OTP
from ..utils.otp_utils import (
    generate_numeric_otp,
    hash_otp,
    otp_expiry_datetime,
    verify_otp_hash
)
from ..utils.mail_utils import send_otp_email
from datetime import datetime
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------
# Register with OTP + Images + Terms
# ---------------------------
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role", "renter")
    phone = request.form.get("phone")
    city = request.form.get("city")
    agree_terms = request.form.get("agree_terms") == "true"
    agree_privacy = request.form.get("agree_privacy") == "true"

    id_card = request.files.get("id_card")
    license_img = request.files.get("license_img")

    # ✅ Validation
    if not all([name, email, password, phone, city]):
        return jsonify({"error": "Missing required fields (name, email, password, phone, city)"}), 400

    if not (agree_terms and agree_privacy):
        return jsonify({"error": "You must agree to Terms & Conditions and Privacy Policy"}), 400

    if role not in ["renter", "owner"]:
        return jsonify({"error": "Role must be either 'renter' or 'owner'"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # ✅ Create upload directories
    upload_root = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_root, exist_ok=True)
    id_dir = os.path.join(upload_root, "id_cards")
    license_dir = os.path.join(upload_root, "licenses")
    os.makedirs(id_dir, exist_ok=True)
    os.makedirs(license_dir, exist_ok=True)

    # ✅ Save images
    id_card_path, license_path = None, None
    if id_card:
        id_filename = f"id_{uuid.uuid4().hex}.jpg"
        id_path = os.path.join(id_dir, id_filename)
        id_card.save(id_path)
        id_card_path = f"uploads/id_cards/{id_filename}"

    if license_img:
        license_filename = f"license_{uuid.uuid4().hex}.jpg"
        license_path_full = os.path.join(license_dir, license_filename)
        license_img.save(license_path_full)
        license_path = f"uploads/licenses/{license_filename}"

    # ✅ Create inactive user
    user = User(
        name=name,
        email=email,
        role=role,
        phone=phone,
        city=city,
        is_active=False,
        agree_terms=agree_terms,
        agree_privacy=agree_privacy,
        id_card_path=id_card_path,
        license_path=license_path,
        id_card_approved=False,
        license_approved=False,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # ✅ Generate OTP
    otp_plain = generate_numeric_otp()
    otp_hashed = hash_otp(otp_plain)
    otp_entry = OTP(
        user_id=user.id,
        otp_hash=otp_hashed,
        expires_at=otp_expiry_datetime()
    )
    db.session.add(otp_entry)
    db.session.commit()

    # ✅ Send OTP
    try:
        send_otp_email(user.email, otp_plain)
    except Exception:
        current_app.logger.exception("Failed to send OTP")
        return jsonify({"error": "Failed to send verification code"}), 500

    return jsonify({
        "message": "User created successfully. Verification code sent.",
        "user_id": user.id
    }), 201


# ---------------------------
# Verify OTP
# ---------------------------
@auth_bp.route("/verify-otp", methods=["POST"])
@limiter.limit("10 per hour")
def verify_otp():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    otp_code = data.get("otp")

    if not user_id or not otp_code:
        return jsonify({"error": "user_id and otp are required"}), 400

    otp_entry = OTP.query.filter_by(user_id=user_id).order_by(OTP.created_at.desc()).first()
    if not otp_entry:
        return jsonify({"error": "No OTP found for user"}), 404

    if otp_entry.expires_at < datetime.utcnow():
        return jsonify({"error": "OTP expired"}), 400

    if otp_entry.attempts >= 5:
        return jsonify({"error": "Too many attempts"}), 403

    if verify_otp_hash(otp_entry.otp_hash, otp_code):
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
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "city": user.city,
                "role": user.role
            }
        }), 200

    otp_entry.attempts += 1
    db.session.commit()
    return jsonify({"error": "Invalid OTP"}), 401


# ---------------------------
# Resend OTP
# ---------------------------
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

    OTP.query.filter_by(user_id=user_id).delete()

    otp_plain = generate_numeric_otp()
    otp_hashed = hash_otp(otp_plain)
    otp_entry = OTP(
        user_id=user_id,
        otp_hash=otp_hashed,
        expires_at=otp_expiry_datetime()
    )
    db.session.add(otp_entry)
    db.session.commit()

    try:
        send_otp_email(user.email, otp_plain)
    except Exception:
        current_app.logger.exception("Failed to resend OTP")
        return jsonify({"error": "Failed to send verification code"}), 500

    return jsonify({"message": "Verification code resent."}), 200


# ---------------------------
# Login
# ---------------------------
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.is_active:
        return jsonify({"error": "Account not verified. Please verify OTP first."}), 403

    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "city": user.city,
            "role": user.role
        }
    }), 200

# ---------------------------
# Update ID/License (requires re-approval)
# ---------------------------
@auth_bp.route("/update-documents", methods=["POST"])
@limiter.limit("3 per hour")
def update_documents():
    user_id = request.form.get("user_id")
    id_card = request.files.get("id_card")
    license_img = request.files.get("license_img")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not (id_card or license_img):
        return jsonify({"error": "No files provided"}), 400

    upload_dir = os.path.join(current_app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    if id_card:
        id_filename = f"id_{uuid.uuid4().hex}.jpg"
        id_path = os.path.join(upload_dir, id_filename)
        id_card.save(id_path)
        user.id_card_path = id_filename
        user.id_card_updated_at = datetime.utcnow()

    if license_img:
        license_filename = f"license_{uuid.uuid4().hex}.jpg"
        license_path = os.path.join(upload_dir, license_filename)
        license_img.save(license_path)
        user.license_path = license_filename
        user.license_updated_at = datetime.utcnow()

    # revert to pending review
    user.approval_status = "pending"
    db.session.commit()

    return jsonify({
        "message": "Documents updated successfully. Awaiting admin approval.",
        "user": {
            "id": user.id,
            "approval_status": user.approval_status,
            "id_card_path": user.id_card_path,
            "license_path": user.license_path
        }
    }), 200
