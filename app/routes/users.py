from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
import os
import uuid
from datetime import datetime

users_bp = Blueprint("users", __name__, url_prefix="/users")

# ==========================================================
# ✅ 1. عرض البروفايل
# ==========================================================
@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.to_dict()), 200


# ==========================================================
# ✅ 2. تعديل البروفايل
# ==========================================================
@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.form or request.json
    if not data:
        return jsonify({"msg": "No data provided"}), 400

    # تحديث البيانات
    user.name = data.get("name", user.name)
    user.city = data.get("city", user.city)
    user.phone = data.get("phone", user.phone)
    user.email = data.get("email", user.email)

    db.session.commit()
    return jsonify({"msg": "Profile updated successfully", "user": user.to_dict()}), 200


# ==========================================================
# ✅ 3. تبديل الدور (renter ↔ owner)
# ==========================================================
@users_bp.route("/switch-role", methods=["POST"])
@jwt_required()
def switch_role():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role == "renter":
        # التحويل إلى owner
        user.role = "owner"
        user.approval_status = "pending"
        user.is_active = False
        msg = "Switched to owner. Pending admin approval."
    else:
        # التحويل إلى renter
        user.role = "renter"
        user.approval_status = "approved"
        user.is_active = True
        msg = "Switched back to renter."

    db.session.commit()
    return jsonify({"msg": msg, "user": user.to_dict()}), 200


# ==========================================================
# ✅ 4. رفع مستندات جديدة (لو المستخدم بقى owner)
# ==========================================================
@users_bp.route("/upload-documents", methods=["POST"])
@jwt_required()
def upload_documents():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != "owner":
        return jsonify({"msg": "Only owners can upload documents"}), 403

    license_file = request.files.get("license")
    id_file = request.files.get("id_card")

    if not license_file or not id_file:
        return jsonify({"msg": "Both license and ID card are required"}), 400

    # حفظ الملفات
    upload_folder = os.path.join(current_app.root_path, "uploads", "documents")
    os.makedirs(upload_folder, exist_ok=True)

    license_filename = f"{uuid.uuid4().hex}_license_{license_file.filename}"
    id_filename = f"{uuid.uuid4().hex}_id_{id_file.filename}"

    license_path = os.path.join(upload_folder, license_filename)
    id_path = os.path.join(upload_folder, id_filename)

    license_file.save(license_path)
    id_file.save(id_path)

    # تحديث بيانات المستخدم
    user.license_image = license_filename
    user.id_card_image = id_filename
    user.approval_status = "pending"
    user.is_active = False

    db.session.commit()

    return jsonify({
        "msg": "Documents uploaded successfully. Waiting for admin approval.",
        "user": user.to_dict()
    }), 200
