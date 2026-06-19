# app/routes/notifications.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Notification
from app.schemas import NotificationSchema

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id = int(get_jwt_identity())
    
    query = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.created_at.desc())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "notifications": NotificationSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page
    }), 200

@notifications_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def unread_count():
    user_id = int(get_jwt_identity())
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({"unread_count": count}), 200

@notifications_bp.route("/mark-read", methods=["POST"])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    
    Notification.query.filter_by(user_id=user_id, is_read=False)\
        .update({"is_read": True})
    
    db.session.commit()
    return jsonify({"msg": "All notifications marked as read"}), 200

@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@jwt_required()
def mark_one_read(notification_id):
    user_id = int(get_jwt_identity())
    notif = Notification.query.get_or_404(notification_id)
    
    if notif.user_id != user_id:
        return jsonify({"msg": "Not your notification"}), 403
    
    notif.is_read = True
    db.session.commit()
    return jsonify({"msg": "Notification marked as read"}), 200
