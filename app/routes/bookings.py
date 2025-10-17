from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from app.extensions import db
from app.models import Booking, Car, User
from app.schemas import BookingSchema

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")


# 🟢 إنشاء حجز جديد
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

    try:
        start_date = datetime.fromisoformat(data["start_date"])
        end_date = datetime.fromisoformat(data["end_date"])
    except ValueError:
        return jsonify({"msg": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

    booking = Booking(
        car_id=car.id,
        renter_id=renter_id,
        start_date=start_date,
        end_date=end_date,
        status="pending"
    )

    car.available = False
    db.session.add(booking)
    db.session.commit()

    return BookingSchema().jsonify(booking), 201


# 🟡 عرض الحجوزات الخاصة بالمستخدم أو المالك
@bookings_bp.route("", methods=["GET"])
@jwt_required()
def list_bookings():
    claims = get_jwt()
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    if claims.get("role") == "owner":
        owner_cars = Car.query.filter_by(owner_id=user_id).all()
        car_ids = [c.id for c in owner_cars]
        bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all()
    else:
        bookings = Booking.query.filter_by(renter_id=user_id).all()

    return BookingSchema(many=True).jsonify(bookings), 200


# 🔵 عرض تفاصيل حجز واحد
@bookings_bp.route("/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
    return BookingSchema().jsonify(booking), 200


# 🗓️ Endpoint لعرض الحجوزات على شكل تقويم
@bookings_bp.route("/calendar", methods=["GET"])
@jwt_required()
def get_bookings_calendar():
    """إرجاع كل الحجوزات بتواريخها لاستخدامها في Calendar View"""
    bookings = Booking.query.all()
    events = [
        {
            "title": f"Car #{b.car_id}",
            "start": b.start_date.isoformat(),
            "end": b.end_date.isoformat(),
            "status": b.status
        }
        for b in bookings
    ]
    return jsonify(events), 200


# ✅ موافقة المالك على الحجز
@bookings_bp.route("/<int:booking_id>/approve", methods=["POST"])
@jwt_required()
def approve_booking(booking_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can approve bookings"}), 403

    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    # تحقق أن العربية دي فعلاً ملك الشخص اللي بيوافق
    car = Car.query.get(booking.car_id)
    if car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    booking.status = "approved"
    booking.approved_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"msg": "Booking approved successfully"}), 200


# ❌ رفض الحجز
@bookings_bp.route("/<int:booking_id>/reject", methods=["POST"])
@jwt_required()
def reject_booking(booking_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can reject bookings"}), 403

    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    car = Car.query.get(booking.car_id)
    if car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    booking.status = "rejected"
    car.available = True  # العربية تبقى متاحة تاني
    db.session.commit()

    return jsonify({"msg": "Booking rejected successfully"}), 200
# ❌ إلغاء الحجز من قبل المستأجر
@bookings_bp.route("/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)

    # تأكد إن اللي بيحاول يلغي هو فعلاً المستأجر
    if booking.renter_id != user_id:
        return jsonify({"msg": "You can only cancel your own bookings"}), 403

    # مينفعش يلغي لو الحالة مش pending
    if booking.status != "pending":
        return jsonify({"msg": "You can only cancel pending bookings"}), 400

    # خليه ملغي وخلي العربية متاحة تاني
    booking.status = "cancelled"
    car = Car.query.get(booking.car_id)
    if car:
        car.available = True

    db.session.commit()
    return jsonify({"msg": "Booking cancelled successfully"}), 200
