from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import User

admin_bp = Blueprint("admin_webhooks", __name__, url_prefix="/admin-webhooks")

@admin_bp.route("/update-user-status", methods=["POST"])
def update_user_status():
    """
    Endpoint سري جداً.
    """
    
    internal_key = current_app.config.get("INTERNAL_API_KEY")
    if not internal_key:
        current_app.logger.warning("INTERNAL_API_KEY is not configured. Denying webhook request.")
        return jsonify({"error": "Unauthorized access"}), 401

    api_key = request.headers.get("X-Internal-Api-Key")
    if api_key != internal_key:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.get_json()
    if not data or "user_id" not in data or "approval_status" not in data:
        return jsonify({"error": "Missing user_id or approval_status"}), 400

    user_id = data.get("user_id")
    new_status = data.get("approval_status") 
    if new_status not in ["approved", "rejected"]:
         return jsonify({"error": "Invalid status"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with id {user_id} not found in this system"}), 404

    user.approval_status = new_status
    db.session.commit()

    return jsonify({
        "message": "User status updated successfully",
        "user_id": user.id,
        "new_status": user.approval_status
    }), 200