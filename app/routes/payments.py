from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Payment, Booking, Car
from app.schemas import PaymentSchema

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


@payments_bp.route("", methods=["POST"])
@jwt_required()
def create_payment():
    data = request.get_json() or {}
    if "booking_id" not in data or "amount" not in data:
        return jsonify({"msg": "booking_id and amount are required"}), 400

    try:
        renter_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    booking = Booking.query.get(data["booking_id"])
    if not booking or booking.renter_id != renter_id:
        return jsonify({"msg": "Booking not found or not owned by you"}), 404

    payment = Payment(
        booking_id=booking.id,
        amount=data["amount"],
        status="pending"
    )

    db.session.add(payment)
    db.session.commit()

    return PaymentSchema().jsonify(payment), 201


@payments_bp.route("/<int:payment_id>", methods=["PUT"])
@jwt_required()
def update_payment(payment_id):
    claims = get_jwt()
    # only owners can update payment status
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can update payment status"}), 403

    try:
        owner_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"msg": "Payment not found"}), 404

    booking = Booking.query.get(payment.booking_id)
    if not booking:
        return jsonify({"msg": "Linked booking not found"}), 404

    car = Car.query.get(booking.car_id)
    if not car or car.owner_id != owner_id:
        return jsonify({"msg": "You are not the owner of this car/booking"}), 403

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ("approved", "rejected"):
        return jsonify({"msg": "Invalid status. Allowed: approved, rejected"}), 400

    payment.status = new_status
    db.session.commit()
    return PaymentSchema().jsonify(payment), 200


@payments_bp.route("", methods=["GET"])
@jwt_required()
def list_payments():
    claims = get_jwt()
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    if claims.get("role") == "owner":
        # owner sees payments for bookings of their cars
        owner_cars = Car.query.filter_by(owner_id=user_id).all()
        car_ids = [c.id for c in owner_cars]
        bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all()
        booking_ids = [b.id for b in bookings]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).all()
    else:
        # renter sees payments for their bookings
        bookings = Booking.query.filter_by(renter_id=user_id).all()
        booking_ids = [b.id for b in bookings]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).all()

    return PaymentSchema(many=True).jsonify(payments), 200
