# app/routes/rently_webhooks.py
"""
Receives webhook events from the .NET Management backend.
The .NET WebhookService signs every request with HMAC-SHA256.

Headers sent by .NET:
  X-Rently-Event:     event name  (e.g. "payment.updated")
  X-Rently-Signature: HMAC-SHA256 hex digest of the raw body
"""
import hmac
import hashlib
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Booking, User, Car

rently_webhooks_bp = Blueprint(
    "rently_webhooks", __name__, url_prefix="/webhook"
)


# ─── HMAC verification ───────────────────────────────────────────────
def _verify_signature(payload_bytes: bytes, signature: str) -> bool:
    secret = current_app.config.get("RENTLY_WEBHOOK_SECRET", "")
    if not secret:
        current_app.logger.warning("RENTLY_WEBHOOK_SECRET not configured")
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


# ─── Main endpoint ───────────────────────────────────────────────────
@rently_webhooks_bp.route("/rently", methods=["POST"])
def receive_webhook():
    """
    Single entry-point for all .NET → Flask events.
    """
    signature = request.headers.get("X-Rently-Signature", "")
    event_name = request.headers.get("X-Rently-Event", "")
    raw_body = request.get_data()  # bytes

    # 1) Verify HMAC
    if not signature or not _verify_signature(raw_body, signature):
        current_app.logger.warning(
            f"Webhook signature invalid for event: {event_name}"
        )
        return jsonify({"error": "Invalid signature"}), 401

    # 2) Parse JSON
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    event_data = data.get("data", {})
    current_app.logger.info(
        f"Webhook received: {event_name} | id={data.get('id')}"
    )

    # 3) Route to handler
    handler = EVENT_HANDLERS.get(event_name)
    if handler:
        try:
            result = handler(event_data)
            return jsonify({"status": "processed", "detail": result}), 200
        except Exception as e:
            current_app.logger.exception(f"Webhook handler error: {e}")
            return jsonify({"error": "Processing failed"}), 500
    else:
        # Unknown event — acknowledge so .NET doesn't retry
        current_app.logger.info(f"Unhandled webhook event: {event_name}")
        return jsonify({"status": "ignored", "event": event_name}), 200


# ─── Event handlers ──────────────────────────────────────────────────
def _handle_payment_updated(data: dict) -> str:
    """
    Paymob confirmed/denied payment → update booking status.
    data: { payment_id, booking_id, status, amount, currency }
    """
    booking_id = data.get("booking_id")
    status = data.get("status", "")

    if not booking_id:
        return "missing booking_id"

    booking = db.session.get(Booking, booking_id)
    if not booking:
        return f"booking {booking_id} not found"

    if status == "Succeeded" and booking.status == "pending":
        booking.status = "approved"
        db.session.commit()
        return f"booking {booking_id} → approved"
    elif status == "Failed" and booking.status == "pending":
        booking.status = "cancelled"
        db.session.commit()
        return f"booking {booking_id} → cancelled"

    return f"no action (booking status={booking.status}, payment status={status})"


def _handle_payment_created(data: dict) -> str:
    """
    .NET created a new Paymob payment — log it.
    data: { payment_id, booking_id, user_id, amount, currency, status, provider }
    """
    current_app.logger.info(
        f"Payment created: id={data.get('payment_id')} "
        f"booking={data.get('booking_id')} amount={data.get('amount')}"
    )
    return "acknowledged"


def _handle_payment_refund(data: dict) -> str:
    """
    Admin requested refund → update booking if needed.
    data: { payment_id, refund_amount, status }
    """
    current_app.logger.info(
        f"Refund requested: payment={data.get('payment_id')} "
        f"amount={data.get('refund_amount')}"
    )
    return "acknowledged"


def _handle_car_status_changed(data: dict) -> str:
    """
    Admin approved/rejected car listing.
    data: { car_id, status }
    """
    car_id = data.get("car_id")
    new_status = data.get("status")

    if not car_id or not new_status:
        return "missing car_id or status"

    car = db.session.get(Car, car_id)
    if not car:
        return f"car {car_id} not found"

    car.status = new_status
    db.session.commit()
    return f"car {car_id} → {new_status}"


def _handle_user_updated(data: dict) -> str:
    """
    Admin updated user info.
    data: { user_id, first_name, last_name, email }
    """
    user_id = data.get("user_id")
    if not user_id:
        return "missing user_id"

    user = db.session.get(User, user_id)
    if not user:
        return f"user {user_id} not found"

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    db.session.commit()

    return f"user {user_id} updated"


def _handle_noop(data: dict) -> str:
    """Acknowledge events that don't need Flask-side action."""
    return "acknowledged"


# ─── Event → handler mapping ─────────────────────────────────────────
EVENT_HANDLERS = {
    "payment.created": _handle_payment_created,
    "payment.updated": _handle_payment_updated,
    "payment.refund_requested": _handle_payment_refund,
    "user.created": _handle_noop,
    "user.updated": _handle_user_updated,
    "user.password_changed": _handle_noop,
    "car.created": _handle_noop,
    "car.updated": _handle_noop,
    "car.status_changed": _handle_car_status_changed,
}
