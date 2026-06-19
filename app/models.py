# app/models.py
from datetime import datetime, timezone
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.types import Numeric

def utcnow():
    return datetime.now(timezone.utc)

# ---------------------------
# ---------------------------
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=False)
    nationality = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    
    preferred_language = db.Column(db.String(10), default="en") 
    license_number = db.Column(db.String(50), nullable=True)
    
    theme = db.Column(db.String(10), default="light")

    id_image = db.Column(db.String(255), nullable=True)
    id_updated_at = db.Column(db.DateTime)
    license_image = db.Column(db.String(255), nullable=True)
    license_updated_at = db.Column(db.DateTime)
    passport_image = db.Column(db.String(255), nullable=True)
    residence_proof_image = db.Column(db.String(255), nullable=True)
    job_proof_image = db.Column(db.String(255), nullable=True)
    selfie_image = db.Column(db.String(255), nullable=True)

    approval_status = db.Column(db.String(20), default="pending", index=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    approved_at = db.Column(db.DateTime)
    
    payout_method = db.Column(db.String(50), nullable=True) # Bank, Wallet
    payout_details = db.Column(db.String(255), nullable=True) 
    billing_country = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)

    agreed_to_terms = db.Column(db.Boolean, default=False)
    agreed_to_privacy = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    cars = db.relationship("Car", backref="owner", lazy="dynamic", foreign_keys="Car.owner_id")
    bookings = db.relationship("Booking", backref="renter", lazy="dynamic", foreign_keys="Booking.renter_id")
    approved_users = db.relationship("User", backref=db.backref("approved_by_admin", remote_side=[id]), lazy="dynamic", foreign_keys="User.approved_by")
    reviews_written = db.relationship("Review", backref="reviewer", lazy="dynamic", foreign_keys="Review.renter_id")
    
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    sent_messages = db.relationship("Message", foreign_keys="Message.sender_id", backref="sender", lazy="dynamic")
    received_messages = db.relationship("Message", foreign_keys="Message.receiver_id", backref="receiver", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role
        }


# ---------------------------
# ---------------------------
class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    brand_ar = db.Column(db.Unicode(100), nullable=True)
    model = db.Column(db.String(100), nullable=False, index=True)
    model_ar = db.Column(db.Unicode(100), nullable=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    price_per_day = db.Column(Numeric(10, 2), nullable=False, index=True)
    status = db.Column(db.String(50), default="available", index=True)
    insurance_details = db.Column(db.String(255), nullable=True, default="Comprehensive Insurance")
    insurance_details_ar = db.Column(db.Unicode(255), nullable=True)

    transmission = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    location_city = db.Column(db.String(100), nullable=True)
    average_rating = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, nullable=True)
    
    license_plate = db.Column(db.String(20), nullable=True) 
    car_license_image = db.Column(db.String(255), nullable=True) 
    features = db.Column(db.String(500), nullable=True) 

    created_at = db.Column(db.DateTime, default=utcnow)

    bookings = db.relationship("Booking", backref="car", lazy="dynamic", foreign_keys="Booking.car_id")
    reviews = db.relationship("Review", backref="car", lazy="dynamic", cascade="all, delete-orphan", foreign_keys="Review.car_id")
    images = db.relationship("CarImage", backref="car", lazy="dynamic", cascade="all, delete-orphan")
    favorited_by = db.relationship("Favorite", backref="car", lazy="dynamic")
    unavailable_dates = db.relationship("CarUnavailableDate", backref="car", lazy="dynamic", cascade="all, delete-orphan")
    @property
    def available(self) -> bool:
        return self.status == "available"


class CarUnavailableDate(db.Model):
    __tablename__ = "car_unavailable_date"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    reason = db.Column(db.String(255), nullable=True) # e.g., "Maintenance", "Personal use"
    created_at = db.Column(db.DateTime, default=utcnow)
# ---------------------------
# ---------------------------
class CarImage(db.Model):
    __tablename__ = "car_image"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

# ---------------------------
# ---------------------------
class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default="general") 
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

# ---------------------------
# ---------------------------
class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow)

# ---------------------------
# ---------------------------
class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    renter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

# ---------------------------
# ---------------------------
class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    renter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    total_price = db.Column(Numeric(10, 2), nullable=True)
    service_fee = db.Column(Numeric(10, 2), default=0)
    rental_type = db.Column(db.String(20), default="day")  # day, week, month, year
    status = db.Column(db.String(50), default="pending", index=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    contact_name = db.Column(db.String(120), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    pickup_location = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)

# ---------------------------
# ---------------------------
class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)

# ---------------------------
# ---------------------------
class OTP(db.Model):
    __tablename__ = "otp"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True) 
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True) 
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship("User", backref=db.backref("otps", cascade="all,delete-orphan", lazy="dynamic"))

# ---------------------------
# ---------------------------
class SearchHistory(db.Model):
    __tablename__ = "search_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    query = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship("User", backref=db.backref("search_history", cascade="all,delete-orphan", lazy="dynamic"))

# ---------------------------
# ---------------------------
class PartnerApplication(db.Model):
    __tablename__ = "partner_application"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    driving_license_number = db.Column(db.String(50), nullable=False)
    car_brand = db.Column(db.String(100), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default="pending", index=True)  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship("User", backref=db.backref("partner_applications", cascade="all,delete-orphan", lazy="dynamic"))