# app/models.py
from datetime import datetime
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------
# User
# ---------------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # owner / renter / admin
    is_active = db.Column(db.Boolean, default=False)

    # Document uploads
    license_image = db.Column(db.String(255), nullable=True)
    id_image = db.Column(db.String(255), nullable=True)
    license_updated_at = db.Column(db.DateTime)
    id_updated_at = db.Column(db.DateTime)

    # Admin review
    approval_status = db.Column(db.String(20), default="pending")  # pending / approved / rejected
    approved_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)  # admin id
    approved_at = db.Column(db.DateTime)

    # User agreements
    agreed_to_terms = db.Column(db.Boolean, default=False)
    agreed_to_privacy = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cars = db.relationship(
        "Car",
        backref="owner",
        lazy="dynamic",
        foreign_keys="Car.owner_id"
    )

    bookings = db.relationship(
        "Booking",
        backref="renter",
        lazy="dynamic",
        foreign_keys="Booking.renter_id"
    )

    approved_users = db.relationship(
        "User",
        backref=db.backref("approved_by_admin", remote_side=[id]),
        lazy="dynamic",
        foreign_keys="User.approved_by"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "approval_status": self.approval_status,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "license_image": self.license_image,
            "id_image": self.id_image,
            "license_updated_at": self.license_updated_at.isoformat() if self.license_updated_at else None,
            "id_updated_at": self.id_updated_at.isoformat() if self.id_updated_at else None,
            "agreed_to_terms": self.agreed_to_terms,
            "agreed_to_privacy": self.agreed_to_privacy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------
# Car
# ---------------------------
class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default="available")  # available / booked / maintenance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship(
        "Booking",
        backref="car",
        lazy="dynamic",
        foreign_keys="Booking.car_id"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "price_per_day": self.price_per_day,
            "available": self.available,
            "status": self.status
        }


# ---------------------------
# Booking
# ---------------------------
class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "car_id": self.car_id,
            "renter_id": self.renter_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status
        }


# ---------------------------
# OTP
# ---------------------------
class OTP(db.Model):
    __tablename__ = "otp"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("otps", cascade="all,delete-orphan", lazy="dynamic"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "attempts": self.attempts
        }


# ---------------------------
# Payment
# ---------------------------
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="completed")

    booking = db.relationship("Booking", backref=db.backref("payments", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "method": self.method,
            "status": self.status,
        }
