from app.extensions import ma
from app.models import User, Car, Booking, Review, Message, Notification, CarImage, Favorite, CarUnavailableDate, SearchHistory, PartnerApplication
from marshmallow import fields, validate
import datetime

class UserRegisterSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(required=True, load_only=True)
    email = fields.Email(required=True)
    
    class Meta:
        model = User
        load_instance = True
        fields = ("first_name", "last_name", "email", "phone", "password", "role", "agreed_to_terms", "agreed_to_privacy", "nationality")

class UserPublicSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(dump_only=True)
    class Meta:
        model = User
        fields = ("id", "name", "role", "nationality", "id_image", "profile_image")

class UserPrivateSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(dump_only=True)
    class Meta:
        model = User
        fields = (
            "id", "name", "email", "phone", "role", "nationality", "is_active",
            "approval_status", "agreed_to_terms", "agreed_to_privacy", "created_at",
            "id_image", "id_updated_at", "license_image", "license_updated_at",
            "passport_image", "residence_proof_image", "job_proof_image", "selfie_image",
            "preferred_language", "license_number", "payout_method", "payout_details", 
            "billing_country", "zip_code", "theme", "profile_image"
        )

class UserUpdateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "nationality", "preferred_language", "theme", "license_number", "payout_method", "payout_details", "billing_country", "zip_code")

class CarUnavailableDateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarUnavailableDate
        fields = ("id", "start_date", "end_date", "reason")

class CarImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CarImage
        fields = ("id", "image_path")

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        fields = ("id", "title", "message", "type", "is_read", "created_at")

class FavoriteSchema(ma.SQLAlchemyAutoSchema):
    car = fields.Nested("CarSchema", only=("id", "brand", "brand_ar", "model", "model_ar", "price_per_day", "images"), dump_only=True)
    class Meta:
        model = Favorite
        fields = ("id", "car_id", "created_at", "car")

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    reviewer = fields.Nested(UserPublicSchema(), dump_only=True)
    class Meta:
        model = Review
        load_instance = True
        include_fk = True
        fields = ("id", "rating", "comment", "created_at", "reviewer", "renter_id", "car_id")

class CarSchema(ma.SQLAlchemyAutoSchema):
    owner = fields.Nested(UserPublicSchema(), dump_only=True)
    available = fields.Boolean(dump_only=True)
    reviews = fields.List(fields.Nested(ReviewSchema(only=("rating", "comment", "reviewer"))), dump_only=True)
    images = fields.List(fields.Nested(CarImageSchema), dump_only=True)
    owner_id = fields.Integer(dump_only=True) 
    reviews_count = fields.Method("get_reviews_count", dump_only=True)
    unavailable_dates = fields.List(fields.Nested(CarUnavailableDateSchema), dump_only=True)

    # Added Validations to fix Edge Cases 3 & 4
    current_year = datetime.datetime.now().year
    year = fields.Integer(
        required=True, 
        validate=validate.Range(min=2000, max=current_year, error=f"Year must be between 2000 and {current_year}")
    )
    price_per_day = fields.Float(
        required=True, 
        validate=validate.Range(min=1, error="Price must be greater than 0")
    )

    class Meta:
        model = Car
        load_instance = True
        include_fk = True
        fields = (
            "id", "brand", "brand_ar", "model", "model_ar", "year", "price_per_day", 
            "status", "available", "owner", "owner_id", 
            "insurance_details", "insurance_details_ar", "transmission", "color", 
            "location_city", "average_rating", "features", "description", "license_plate", "car_license_image",
            "images", "reviews", "reviews_count", "unavailable_dates"
        )

    def get_reviews_count(self, obj):
        if hasattr(obj, 'reviews'):
            return obj.reviews.count() if obj.reviews else 0
        return 0

class BookingSchema(ma.SQLAlchemyAutoSchema):
    car = fields.Nested(CarSchema(), dump_only=True)
    renter = fields.Nested(UserPublicSchema(), dump_only=True)

    class Meta:
        model = Booking
        load_instance = True
        include_fk = True
        fields = ("id", "start_date", "end_date", "status", "total_price", "service_fee",
                  "rental_type", "transaction_id", "payment_date",
                  "contact_name", "contact_email", "contact_phone", "pickup_location",
                  "car_id", "renter_id", "car", "renter")

class MessageSchema(ma.SQLAlchemyAutoSchema):
    sender = fields.Nested(UserPublicSchema(only=("id", "name", "id_image")), dump_only=True)
    receiver = fields.Nested(UserPublicSchema(only=("id", "name", "id_image")), dump_only=True)
    
    class Meta:
        model = Message
        load_instance = True
        include_fk = True
        fields = ("id", "sender_id", "receiver_id", "content", "timestamp", "is_read", "sender", "receiver")

class SearchHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SearchHistory
        fields = ("id", "query", "created_at")

class PartnerApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartnerApplication
        fields = ("id", "full_name", "email", "contact", "driving_license_number",
                  "car_brand", "car_model", "photo", "status", "created_at")