# app/routes/partner.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import PartnerApplication, User
from app.schemas import PartnerApplicationSchema

partner_bp = Blueprint("partner", __name__, url_prefix="/partner")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@partner_bp.route("/apply", methods=["POST"])
@jwt_required()
def apply_partner():
    """
    Rently Partner Program — user applies to become a car owner/partner.
    """
    user_id = int(get_jwt_identity())

    # Check if user already has a pending application
    existing = PartnerApplication.query.filter_by(
        user_id=user_id, status="pending"
    ).first()
    if existing:
        return jsonify({"msg": "You already have a pending partner application"}), 400

    data = request.form.to_dict()
    
    required_fields = ["full_name", "email", "contact", "driving_license_number", "car_brand", "car_model"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"msg": f"Missing required fields: {', '.join(missing)}"}), 400

    # Handle photo upload
    photo_path = None
    photo = request.files.get("photo")
    if photo and photo.filename != '' and allowed_file(photo.filename):
        upload_root = os.path.join(current_app.root_path, "uploads")
        partner_dir = os.path.join(upload_root, "partner")
        os.makedirs(partner_dir, exist_ok=True)
        
        filename = secure_filename(photo.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"partner_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        photo.save(os.path.join(partner_dir, unique_filename))
        photo_path = f"uploads/partner/{unique_filename}"

    application = PartnerApplication(
        user_id=user_id,
        full_name=data["full_name"],
        email=data["email"],
        contact=data["contact"],
        driving_license_number=data["driving_license_number"],
        car_brand=data["car_brand"],
        car_model=data["car_model"],
        photo=photo_path,
        status="pending"
    )

    db.session.add(application)
    db.session.commit()

    return jsonify({
        "msg": "Partner application submitted successfully. We will review it shortly.",
        "application": PartnerApplicationSchema().dump(application)
    }), 201


@partner_bp.route("/status", methods=["GET"])
@jwt_required()
def get_application_status():
    """
    Check the status of current user's partner application(s).
    """
    user_id = int(get_jwt_identity())

    applications = PartnerApplication.query.filter_by(user_id=user_id)\
        .order_by(PartnerApplication.created_at.desc()).all()

    return jsonify({
        "applications": PartnerApplicationSchema(many=True).dump(applications)
    }), 200
