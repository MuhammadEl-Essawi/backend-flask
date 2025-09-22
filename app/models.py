from app.extensions import db

# 🟢 User Model
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # ✅ نخزن الباسورد هنا
    role = db.Column(db.String(20), nullable=False)  # admin, owner, renter

    # العلاقات
    cars = db.relationship("Car", backref="owner", lazy=True)  
    renter_bookings = db.relationship(
        "Booking", backref="renter", lazy=True, foreign_keys="Booking.renter_id"
    )


# 🟢 Car Model
class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="available")  # available, booked

    # العلاقات
    bookings = db.relationship("Booking", backref="car", lazy=True)


# 🟢 Booking Model
class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # ✅ رابط بالرنتـر
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled

    # العلاقات
    payments = db.relationship("Payment", backref="booking", lazy=True)


# 🟢 Payment Model
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="unpaid")  # unpaid, paid
