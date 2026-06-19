import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User 
from werkzeug.utils import secure_filename
from app.schemas import UserPrivateSchema, UserUpdateSchema 
from marshmallow import ValidationError
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
users_bp = Blueprint("users", __name__, url_prefix="/users")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_document(file, user_id_prefix, doc_type):
    """
    """
    if not file or file.filename == '':
        return None, "No file provided"
    if not allowed_file(file.filename):
        return None, "Invalid file type"
        
    upload_root = os.path.join(current_app.root_path, "uploads")
    doc_dir = os.path.join(upload_root, f"{doc_type}s")
    os.makedirs(doc_dir, exist_ok=True)
    
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{user_id_prefix}_{doc_type}_{uuid.uuid4().hex[:8]}.{ext}"
    
    file_path = os.path.join(doc_dir, unique_filename)
    file.save(file_path)
    
    db_path = f"uploads/{doc_type}s/{unique_filename}"
    return db_path, None


# ==========================================================
# ==========================================================
@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return UserPrivateSchema().jsonify(user), 200

# ==========================================================
# ==========================================================
@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "No JSON data provided"}), 400

    if 'email' in data:
        return jsonify({"msg": "Email cannot be changed from this endpoint."}), 400

    try:
        schema = UserUpdateSchema()
        schema.load_instance = False  
        updated_data = schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"msg": "Invalid data provided", "errors": err.messages}), 400

    for key, value in updated_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        db.session.commit()
        return jsonify({"msg": "Profile updated successfully", "user": UserPrivateSchema().dump(user)}), 200
        
    except IntegrityError:
        db.session.rollback() 
        return jsonify({
            "msg": "Data conflict error", 
            "errors": {"phone": ["This phone number is already registered to another account."]}
        }), 400
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile: {e}")
        return jsonify({"msg": "An unexpected error occurred while updating the profile."}), 500

# ==========================================================
# ==========================================================
@users_bp.route("/upload-documents", methods=["POST"])
@jwt_required()
def upload_documents():
    if request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds limit (10MB)"}), 413
        
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if not request.files:
         return jsonify({"msg": "No files were uploaded in the request"}), 400

    id_image_file = request.files.get("id_image")
    license_image_file = request.files.get("license_image")
    passport_image_file = request.files.get("passport_image")
    residence_proof_file = request.files.get("residence_proof_image")
    job_proof_file = request.files.get("job_proof_image")
    selfie_file = request.files.get("selfie_image")

    errors = {}
    files_uploaded_count = 0
    user_id_prefix = f"user_{user.id}"

    
    if id_image_file:
        path, err = save_document(id_image_file, user_id_prefix, "id_image")
        if err: errors["id_image"] = err
        else:
            user.id_image = path
            user.id_updated_at = datetime.now(timezone.utc)
            files_uploaded_count += 1

    if license_image_file:
        path, err = save_document(license_image_file, user_id_prefix, "license_image")
        if err: errors["license_image"] = err
        else:
            user.license_image = path
            user.license_updated_at = datetime.now(timezone.utc)
            files_uploaded_count += 1

    if passport_image_file:
        path, err = save_document(passport_image_file, user_id_prefix, "passport_image")
        if err: errors["passport_image"] = err
        else:
            user.passport_image = path
            files_uploaded_count += 1

    if residence_proof_file:
        path, err = save_document(residence_proof_file, user_id_prefix, "residence_proof")
        if err: errors["residence_proof_image"] = err
        else:
            user.residence_proof_image = path
            files_uploaded_count += 1

    if job_proof_file:
        path, err = save_document(job_proof_file, user_id_prefix, "job_proof")
        if err: errors["job_proof_image"] = err
        else:
            user.job_proof_image = path
            files_uploaded_count += 1

    if selfie_file:
        path, err = save_document(selfie_file, user_id_prefix, "selfie_image")
        if err: errors["selfie_image"] = err
        else:
            user.selfie_image = path
            files_uploaded_count += 1
        
    if errors:
        return jsonify({"msg": "Error processing one or more files", "errors": errors}), 400
    
    if files_uploaded_count == 0:
        return jsonify({"msg": "No valid files were uploaded"}), 400

    user.approval_status = "pending"
    db.session.commit()

    return jsonify({
        "msg": "Documents uploaded successfully. Waiting for admin approval.",
        "user": UserPrivateSchema().dump(user)
    }), 200


# ==========================================================
# Profile Picture Upload
# ==========================================================
@users_bp.route("/profile/photo", methods=["POST"])
@jwt_required()
def upload_profile_photo():
    if request.content_length and request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds limit (10MB)"}), 413

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    photo = request.files.get("profile_image")
    if not photo or photo.filename == '':
        return jsonify({"msg": "No photo provided"}), 400

    if not allowed_file(photo.filename):
        return jsonify({"msg": "Invalid file type. Allowed: png, jpg, jpeg, pdf"}), 400

    path, err = save_document(photo, f"user_{user.id}", "profile")
    if err:
        return jsonify({"msg": err}), 400

    user.profile_image = path
    db.session.commit()

    return jsonify({
        "msg": "Profile photo updated successfully",
        "profile_image": path
    }), 200
