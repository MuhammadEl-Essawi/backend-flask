from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from app.extensions import db, mail
from app.models import Payment, Booking, Car, OTP, User
from app.schemas import PaymentSchema
from app.utils.otp_utils import generate_numeric_otp, hash_otp, otp_expiry_datetime, verify_otp_hash
from flask_mail import Message

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

# --------------------------
# إرسال OTP عبر الإيميل
# --------------------------
def send_otp_email(recipient_email, otp_code):
    if not recipient_email:
        current_app.logger.warning("No recipient email provided for OTP")
        return

    msg = Message(
        subject="Your OTP Code",
        recipients=[recipient_email],
        body=f"Your OTP code is: {otp_code}"
    )
    try:
        mail.send(msg)
        current_app.logger.info(f"OTP sent to {recipient_email}")
    except Exception as e:
        current_app.logger.exception(f"Failed to send OTP email to {recipient_email}: {e}")

# --------------------------
# 1️⃣ إنشاء عملية الدفع + إرسال OTP
# --------------------------
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

    # تحديد طريقة الدفع (افتراضي card)
    method = data.get("method", "card")

    # إنشاء دفعة جديدة بحالة pending_otp
    payment = Payment(
        booking_id=booking.id,
        amount=data["amount"],
        method=method,
        payment_date=datetime.utcnow(),
        status="pending_otp"
    )
    db.session.add(payment)
    db.session.commit()

    # إنشاء OTP
    otp_plain = generate_numeric_otp()
    otp_hashed = hash_otp(otp_plain)
    otp_entry = OTP(user_id=renter_id, otp_hash=otp_hashed, expires_at=otp_expiry_datetime())
    db.session.add(otp_entry)
    db.session.commit()

    # إرسال OTP للمستخدم
    user = User.query.get(renter_id)
    try:
        if current_app.config.get("MAIL_USERNAME"):
            send_otp_email(user.email, otp_plain)
        else:
            current_app.logger.info(f"[DEV OTP] payment_id={payment.id}, user_email={user.email}, otp={otp_plain}")
    except Exception:
        current_app.logger.exception("Failed to send OTP for payment")
        return jsonify({"msg": "Failed to send OTP"}), 500

    return jsonify({
        "msg": "Payment created. Please verify OTP to continue.",
        "payment_id": payment.id
    }), 201

# --------------------------
# 2️⃣ تأكيد الدفع باستخدام OTP
# --------------------------
@payments_bp.route("/verify-otp", methods=["POST"])
@jwt_required()
def verify_payment_otp():
    data = request.get_json() or {}
    payment_id = data.get("payment_id")
    otp_code = data.get("otp")

    if not payment_id or not otp_code:
        return jsonify({"msg": "payment_id and otp are required"}), 400

    try:
        renter_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"msg": "Payment not found"}), 404

    booking = Booking.query.get(payment.booking_id)
    if not booking or booking.renter_id != renter_id:
        return jsonify({"msg": "Unauthorized payment access"}), 403

    otp_entry = OTP.query.filter_by(user_id=renter_id).order_by(OTP.created_at.desc()).first()
    if not otp_entry:
        return jsonify({"msg": "No OTP found"}), 404

    if otp_entry.expires_at < datetime.utcnow():
        return jsonify({"msg": "OTP expired"}), 400

    if not verify_otp_hash(otp_entry.otp_hash, otp_code):
        otp_entry.attempts += 1
        db.session.commit()
        return jsonify({"msg": "Invalid OTP"}), 401

    # ✅ لو صح
    db.session.delete(otp_entry)
    payment.status = "pending"  # دلوقتي جاهز للموافقة من الـ owner
    db.session.commit()

    return jsonify({"msg": "Payment verified successfully", "payment_id": payment.id}), 200

# --------------------------
# 3️⃣ تحديث حالة الدفع (للأونر)
# --------------------------
@payments_bp.route("/<int:payment_id>", methods=["PUT"])
@jwt_required()
def update_payment(payment_id):
    claims = get_jwt()
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

# --------------------------
# 4️⃣ عرض المدفوعات
# --------------------------
@payments_bp.route("", methods=["GET"])
@jwt_required()
def list_payments():
    claims = get_jwt()
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"msg": "Invalid token identity"}), 400

    if claims.get("role") == "owner":
        owner_cars = Car.query.filter_by(owner_id=user_id).all()
        car_ids = [c.id for c in owner_cars]
        bookings = Booking.query.filter(Booking.car_id.in_(car_ids)).all()
        booking_ids = [b.id for b in bookings]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).all()
    else:
        bookings = Booking.query.filter_by(renter_id=user_id).all()
        booking_ids = [b.id for b in bookings]
        payments = Payment.query.filter(Payment.booking_id.in_(booking_ids)).all()

    return PaymentSchema(many=True).jsonify(payments), 200
