# app/routes/payment_webhooks.py
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Booking

payment_webhooks_bp = Blueprint("payment_webhooks", __name__, url_prefix="/payment-webhooks")

@payment_webhooks_bp.route("/confirm-booking", methods=["POST"])
def confirm_booking_payment():
    """
    Endpoint سري جداً.
    """
    
    internal_key = current_app.config.get("INTERNAL_API_KEY")
    if not internal_key:
        current_app.logger.warning("INTERNAL_API_KEY is not configured. Denying payment webhook request.")
        return jsonify({"error": "Unauthorized access"}), 401

    api_key = request.headers.get("X-Internal-Api-Key")
    if api_key != internal_key:
        current_app.logger.warning("Unauthorized webhook attempt (Payment)")
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.get_json()
    if not data or "booking_id" not in data or "payment_status" not in data:
        current_app.logger.error("Invalid webhook payload (Payment)")
        return jsonify({"error": "Missing booking_id or payment_status"}), 400

    booking_id = data.get("booking_id")
    payment_status = data.get("payment_status") 
    if payment_status != "completed":
         current_app.logger.info(f"Received non-completed payment status for booking {booking_id}: {payment_status}")
         return jsonify({"message": "Payment status not completed, no action taken."}), 200

    booking = Booking.query.get(booking_id)
    if not booking:
        current_app.logger.error(f"Booking {booking_id} not found for payment confirmation")
        return jsonify({"error": f"Booking with id {booking_id} not found"}), 404

    if booking.status == "pending": 
        booking.status = "approved" 
        db.session.commit()
        current_app.logger.info(f"Booking {booking_id} confirmed via payment webhook.")
        return jsonify({
            "message": "Booking status updated to approved successfully",
            "booking_id": booking.id,
            "new_status": booking.status
        }), 200
    else:
        current_app.logger.warning(f"Received payment confirmation for booking {booking_id} which is already in status {booking.status}")
        return jsonify({"message": f"Booking status was already {booking.status}, no action taken."}), 200