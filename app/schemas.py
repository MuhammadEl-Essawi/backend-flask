from app.extensions import ma
from app.models import User, Car, Booking, Payment


# 🔹 User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password",)  # نخفي الباسورد من الـ response


# 🔹 Car Schema
class CarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Car
        load_instance = True
        include_fk = True


# 🔹 Booking Schema
class BookingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True
        include_fk = True


# 🔹 Payment Schema
class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        include_fk = True
