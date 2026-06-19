# app/utils/notification_utils.py
"""
Utility to auto-create in-app notifications on events.
"""
from app.extensions import db
from app.models import Notification


def notify(user_id, title, message, notif_type="general"):
    """
    Creates an in-app notification for a user.
    
    notif_type: 'booking', 'payment', 'review', 'message', 'system', 'general'
    """
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        is_read=False
    )
    db.session.add(notif)
    # NOTE: caller must commit the session
    return notif


def notify_booking_created(owner_id, booking_id, car_name, renter_name):
    return notify(
        user_id=owner_id,
        title="New Booking Request",
        message=f"{renter_name} requested to book your {car_name} (#{booking_id}).",
        notif_type="booking"
    )


def notify_booking_approved(renter_id, booking_id, car_name):
    return notify(
        user_id=renter_id,
        title="Booking Approved! 🎉",
        message=f"Your booking #{booking_id} for {car_name} has been approved.",
        notif_type="booking"
    )


def notify_booking_rejected(renter_id, booking_id, car_name):
    return notify(
        user_id=renter_id,
        title="Booking Rejected",
        message=f"Your booking #{booking_id} for {car_name} has been rejected by the owner.",
        notif_type="booking"
    )


def notify_booking_cancelled(owner_id, booking_id, car_name, renter_name):
    return notify(
        user_id=owner_id,
        title="Booking Cancelled",
        message=f"{renter_name} cancelled booking #{booking_id} for your {car_name}.",
        notif_type="booking"
    )


def notify_new_review(owner_id, car_name, rating, reviewer_name):
    return notify(
        user_id=owner_id,
        title="New Review ⭐",
        message=f"{reviewer_name} gave your {car_name} a {rating}-star review.",
        notif_type="review"
    )


def notify_new_message(receiver_id, sender_name):
    return notify(
        user_id=receiver_id,
        title="New Message 💬",
        message=f"You have a new message from {sender_name}.",
        notif_type="message"
    )
