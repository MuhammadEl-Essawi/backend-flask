from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Booking, Car, User
from app.schemas import BookingSchema

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")


@bookings_bp.route("", methods=["POST"])
@jwt_required()
def create_booking():
    data = request.get_json() or {}
    needed = ("car_id", "start_date", "end_date")
    if not all(k in data for k in needed):
        return jsonify({"msg": f"Missing fields. Required: {needed}"}), 400

    try:
        renter_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    car = Car.query.get(data["car_id"])
    if not car:
        return jsonify({"msg": "Car not found"}), 404
    if not getattr(car, "available", True):
        return jsonify({"msg": "Car not available"}), 400

    booking = Booking(
        car_id=car.id,
        renter_id=renter_id,
        start_date=data["start_date"],
        end_date=data["end_date"],
        status="pending"
    )
    # mark car as unavailable (simple reservation)
    car.available = False

    db.session.add(booking)
    db.session.commit()

    return BookingSchema().jsonify(booking), 201


@bookings_bp.route("", methods=["GET"])
@jwt_required()
def list_bookings():
    claims = get_jwt()
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    if claims.get("role") == "owner":
        # owner sees bookings for their cars
        owner_cars = Car.query.filter_by(owner_id=user_id).all()
        car_ids = [c.id for c in owner_cars]
        bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all()
    else:
        # renters see only their bookings
        bookings = Booking.query.filter_by(renter_id=user_id).all()

    return BookingSchema(many=True).jsonify(bookings), 200


@bookings_bp.route("/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
    return BookingSchema().jsonify(booking), 200
