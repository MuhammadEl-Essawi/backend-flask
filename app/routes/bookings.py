from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.models import Booking, Car, User
from app.schemas import BookingSchema
from sqlalchemy import or_
from ..utils.mail_utils import send_booking_approved_email
from ..utils.notification_utils import (
    notify_booking_created, notify_booking_approved,
    notify_booking_rejected, notify_booking_cancelled
)

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

    if car.owner_id == renter_id:
        return jsonify({"msg": "You cannot book your own car"}), 400

    try:
        start_date = datetime.fromisoformat(data["start_date"].replace('Z', '+00:00')).replace(tzinfo=None)
        end_date = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return jsonify({"msg": "Invalid date format. Use ISO format (e.g., YYYY-MM-DDTHH:MM:SSZ)"}), 400

    if start_date < datetime.now(timezone.utc).replace(tzinfo=None):
        return jsonify({"msg": "Start date must be in the future"}), 400
    if end_date <= start_date:
        return jsonify({"msg": "End date must be after start date"}), 400

    existing_booking = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status == 'approved',
        Booking.start_date < end_date,
        Booking.end_date > start_date
    ).first()

    if existing_booking:
        return jsonify({"msg": "Car is already booked for these dates"}), 409

    num_days = (end_date - start_date).days
    if num_days < 1:
        num_days = 1
    total_price = Decimal(str(car.price_per_day)) * num_days

    booking = Booking(
        car_id=car.id,
        renter_id=renter_id,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        service_fee=Decimal(str(data.get("service_fee", 0))),
        rental_type=data.get("rental_type", "day"),
        contact_name=data.get("contact_name"),
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        pickup_location=data.get("pickup_location"),
        status="pending"
    )

    db.session.add(booking)

    # Auto-notify owner
    renter = User.query.get(renter_id)
    notify_booking_created(
        owner_id=car.owner_id,
        booking_id=booking.id if booking.id else 0,
        car_name=f"{car.brand} {car.model}",
        renter_name=renter.name if renter else "Unknown"
    )

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

    # Fixed Access Control: Renter sees ONLY their bookings, Owner sees bookings on their cars
    if claims.get("role") == "owner":
        query = Booking.query.join(Car, Car.id == Booking.car_id)\
                             .filter(Car.owner_id == user_id)\
                             .order_by(Booking.start_date.desc())
    else:
        # Implicitly handles the renter case, restricting them to their own requested bookings
        query = Booking.query.filter_by(renter_id=user_id)\
                             .order_by(Booking.start_date.desc())

    # Filter by status (for Requests / My Bookings filtering)
    status = request.args.get('status', type=str)
    if status:
        query = query.filter(Booking.status == status)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "bookings": BookingSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }), 200

@bookings_bp.route("/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    booking = Booking.query.get_or_404(booking_id)
    car = Car.query.get(booking.car_id)

    is_renter = (booking.renter_id == user_id)
    is_owner = (car and car.owner_id == user_id)
    is_admin = (claims.get("role") == "admin")

    if not (is_renter or is_owner or is_admin):
        return jsonify({"msg": "You are not authorized to view this booking"}), 403

    return BookingSchema().jsonify(booking), 200

@bookings_bp.route("/calendar", methods=["GET"])
@jwt_required()
def get_bookings_calendar():
    claims = get_jwt()
    user_id = int(get_jwt_identity())

    if claims.get("role") == "owner":
        bookings = Booking.query.join(Car, Car.id == Booking.car_id)\
                                .filter(Car.owner_id == user_id)\
                                .all()
    else:
        bookings = Booking.query.filter_by(renter_id=user_id).all()

    events = [
        {
            "title": f"Booking #{b.id} - Car #{b.car_id}",
            "start": b.start_date.isoformat(),
            "end": b.end_date.isoformat(),
            "status": b.status,
            "color": "green" if b.status == "approved" else ("orange" if b.status == "pending" else "red")
        }
        for b in bookings
    ]
    return jsonify(events), 200

@bookings_bp.route("/<int:booking_id>/approve", methods=["POST"])
@jwt_required()
def approve_booking(booking_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can approve bookings"}), 403

    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    car = Car.query.get(booking.car_id)
    if not car or car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car or car not found"}), 403

    if booking.status != "pending":
         return jsonify({"msg": f"Booking is already {booking.status}, cannot approve."}), 400

    start_date = booking.start_date
    end_date = booking.end_date

    existing_approved_booking = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status == 'approved',
        Booking.id != booking_id,
        Booking.start_date < end_date,
        Booking.end_date > start_date
    ).first()

    if existing_approved_booking:
        return jsonify({"msg": "Cannot approve. This booking conflicts with another approved booking."}), 409

    booking.status = "approved"

    conflicting_pending_bookings = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status == 'pending',
        Booking.id != booking_id,
        Booking.start_date < end_date,
        Booking.end_date > start_date
    ).all()

    for b in conflicting_pending_bookings:
        b.status = "rejected"
        notify_booking_rejected(b.renter_id, b.id, f"{car.brand} {car.model}")

    # Notify renter of approval
    notify_booking_approved(booking.renter_id, booking.id, f"{car.brand} {car.model}")

    db.session.commit()

    try:
        renter = User.query.get(booking.renter_id)
        if renter and renter.email:
             send_booking_approved_email(
                 recipient_email=renter.email,
                 booking_id=booking.id,
                 car_model=f"{car.brand} {car.model}",
                 start_date=booking.start_date,
                 end_date=booking.end_date
             )
        else:
            current_app.logger.warning(f"Renter not found or has no email for booking {booking_id}")
    except Exception as e:
        current_app.logger.exception(f"Failed to send approval notification email for booking {booking_id}: {e}")

    return jsonify({"msg": "Booking approved successfully. Conflicting pending bookings (if any) were rejected."}), 200

@bookings_bp.route("/<int:booking_id>/reject", methods=["POST"])
@jwt_required()
def reject_booking(booking_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can reject bookings"}), 403

    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    car = Car.query.get(booking.car_id)

    if not car or car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car or car not found"}), 403

    if booking.status != "pending":
         return jsonify({"msg": f"Booking is already {booking.status}, cannot reject."}), 400

    booking.status = "rejected"

    # Notify renter
    notify_booking_rejected(booking.renter_id, booking.id, f"{car.brand} {car.model}")

    db.session.commit()

    return jsonify({"msg": "Booking rejected successfully"}), 200

@bookings_bp.route("/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    if booking.renter_id != user_id:
        return jsonify({"msg": "You can only cancel your own bookings"}), 403

    if booking.status not in ["pending", "approved"]:
        return jsonify({"msg": f"You can only cancel pending or approved bookings. Status is: {booking.status}"}), 400

    booking.status = "cancelled"

    # Notify owner
    car = Car.query.get(booking.car_id)
    renter = User.query.get(user_id)
    if car:
        notify_booking_cancelled(
            owner_id=car.owner_id,
            booking_id=booking.id,
            car_name=f"{car.brand} {car.model}",
            renter_name=renter.name if renter else "Unknown"
        )

    db.session.commit()

    return jsonify({"msg": "Booking cancelled successfully"}), 200