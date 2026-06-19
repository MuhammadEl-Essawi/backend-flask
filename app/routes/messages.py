# app/routes/messages.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Message, User
from app.schemas import MessageSchema
from sqlalchemy import or_, and_
from ..utils.notification_utils import notify_new_message

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")

MAX_MESSAGE_LENGTH = 5000

@messages_bp.route("", methods=["POST"])
@jwt_required()
def send_message():
    data = request.get_json() or {}
    sender_id = int(get_jwt_identity())
    
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"msg": "receiver_id and content are required"}), 400

    if len(content) > MAX_MESSAGE_LENGTH:
        return jsonify({"msg": f"Message is too long. Maximum {MAX_MESSAGE_LENGTH} characters."}), 400

    if sender_id == int(receiver_id):
        return jsonify({"msg": "You cannot send a message to yourself"}), 400

    if not User.query.get(receiver_id):
        return jsonify({"msg": "Receiver not found"}), 404

    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    
    db.session.add(message)

    # Auto-notify receiver
    sender = User.query.get(sender_id)
    notify_new_message(
        receiver_id=int(receiver_id),
        sender_name=sender.name if sender else "Someone"
    )

    db.session.commit()

    return MessageSchema().jsonify(message), 201


@messages_bp.route("/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_conversation(other_user_id):
    current_user_id = int(get_jwt_identity())
    messages_query = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user_id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user_id)
        )
    ).order_by(Message.timestamp.asc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    pagination = messages_query.paginate(page=page, per_page=per_page, error_out=False)

    for msg in pagination.items:
        if msg.receiver_id == current_user_id and not msg.is_read:
            msg.is_read = True
    db.session.commit()

    return jsonify({
        "messages": MessageSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page
    }), 200


@messages_bp.route("/inbox", methods=["GET"])
@jwt_required()
def get_inbox():
    """
    Returns chat list with last message and unread count per conversation.
    """
    current_user_id = int(get_jwt_identity())
    
    all_messages = Message.query.filter(
        or_(Message.sender_id == current_user_id, Message.receiver_id == current_user_id)
    ).order_by(Message.timestamp.desc()).all()

    chats = {}
    for msg in all_messages:
        other_id = msg.receiver_id if msg.sender_id == current_user_id else msg.sender_id
        
        if other_id not in chats:
            chats[other_id] = {
                "last_message": msg,
                "unread_count": 0
            }
        
        if msg.receiver_id == current_user_id and not msg.is_read:
            chats[other_id]["unread_count"] += 1

    inbox_list = []
    for other_id, chat_data in chats.items():
        other_user = User.query.get(other_id)
        msg_data = MessageSchema().dump(chat_data["last_message"])
        msg_data["unread_count"] = chat_data["unread_count"]
        msg_data["other_user"] = {
            "id": other_user.id,
            "name": other_user.name,
            "profile_image": other_user.profile_image
        } if other_user else None
        inbox_list.append(msg_data)

    return jsonify(inbox_list), 200
