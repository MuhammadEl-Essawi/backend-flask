# Chapter: Flask Backend – Rently Car Rental Platform

## 1. Introduction

The Rently Flask backend serves as the **mobile-facing RESTful API** for the Rently peer-to-peer car rental platform. It handles user authentication, car listings, booking management, messaging, notifications, reviews, and integrates with a .NET management dashboard via secure webhooks.

**Key Highlights:**
- Built with **Flask** using the Application Factory pattern
- **JWT-based** authentication with role-based access control (Owner / Renter)
- **OTP email verification** for account activation and password reset
- **HMAC-SHA256 signed webhooks** for secure .NET ↔ Flask communication
- **Rate limiting**, **caching**, and **pagination** on all list endpoints
- Containerized with **Docker** and served via **Gunicorn** in production

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Framework | Flask (Python 3.12) |
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Authentication | Flask-JWT-Extended |
| Serialization | Flask-Marshmallow + marshmallow-sqlalchemy |
| Email | Flask-Mail (SMTP / Gmail) |
| Rate Limiting | Flask-Limiter |
| Caching | Flask-Caching (SimpleCache) |
| CORS | Flask-CORS |
| SMS (Optional) | Twilio |
| Production Server | Gunicorn (4 workers) |
| Containerization | Docker (python:3.12-slim) |

---

## 3. Project Structure

```
car_rental_backend/
├── manage.py                  # Application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Production container
├── seed.py                    # Database seeder (1000 users, 300 cars, 3000 bookings)
├── app/
│   ├── __init__.py            # Application Factory (create_app)
│   ├── config.py              # Configuration from environment variables
│   ├── extensions.py          # Flask extension instances
│   ├── models.py              # SQLAlchemy data models (10 models)
│   ├── schemas.py             # Marshmallow serialization schemas
│   ├── routes/
│   │   ├── auth.py            # Registration, Login, OTP, Password Reset
│   │   ├── cars.py            # CRUD operations, filtering, availability
│   │   ├── bookings.py        # Create, approve, reject, cancel bookings
│   │   ├── users.py           # Profile management, document upload
│   │   ├── reviews.py         # Car reviews with rating aggregation
│   │   ├── messages.py        # User-to-user messaging, inbox
│   │   ├── notifications.py   # In-app notification system
│   │   ├── favorites.py       # Favorite cars (wishlist)
│   │   ├── search.py          # Search history management
│   │   ├── partner.py         # Partner program applications
│   │   ├── static_pages.py    # Privacy policy, Terms, Invite info
│   │   ├── admin_webhooks.py  # Internal admin status updates
│   │   ├── payment_webhooks.py# Payment confirmation webhook
│   │   └── rently_webhooks.py # HMAC-signed .NET webhook receiver
│   └── utils/
│       ├── otp_utils.py       # Secure OTP generation and hashing
│       ├── mail_utils.py      # Email sending (OTP, booking approval)
│       ├── notification_utils.py # Auto-notification helper functions
│       └── sms_utils.py       # Twilio SMS integration
```

---

## 4. Application Factory Pattern

The application uses Flask's **Application Factory** pattern, which allows creating multiple app instances for testing and modularity.

```python
# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, ma, jwt, cors, mail, limiter, migrate, cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(bookings_bp)
    # ... (13 blueprints total)

    return app
```

All Flask extensions are instantiated **without** an app in `extensions.py`, then bound inside the factory:

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()
mail = Mail()
migrate = Migrate()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
```

---

## 5. Configuration Management

All sensitive configuration is loaded from **environment variables** using `python-dotenv`. A helper function enforces that critical variables are present:

```python
# app/config.py
def get_env_variable(name: str) -> str:
    var = os.getenv(name)
    if not var:
        raise ValueError(f"CRITICAL: Environment variable '{name}' is not set.")
    return var

class Config:
    SECRET_KEY = get_env_variable("SECRET_KEY")
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = get_env_variable("DATABASE_URL")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # OTP, Mail, Cache, CORS, Upload, Webhook configurations...
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    RENTLY_WEBHOOK_SECRET = os.getenv("RENTLY_WEBHOOK_SECRET", "DEV_FLASK_WEBHOOK_SECRET")
```

---

## 6. Data Models

The application defines **10 SQLAlchemy models**. Below are the core models with their relationships:

### 6.1 User Model

```python
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # "owner" | "renter"
    is_active = db.Column(db.Boolean, default=False)
    approval_status = db.Column(db.String(20), default="pending", index=True)

    # KYC Document fields
    id_image = db.Column(db.String(255), nullable=True)
    license_image = db.Column(db.String(255), nullable=True)
    passport_image = db.Column(db.String(255), nullable=True)
    selfie_image = db.Column(db.String(255), nullable=True)

    # Relationships
    cars = db.relationship("Car", backref="owner", lazy="dynamic")
    bookings = db.relationship("Booking", backref="renter", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
```

### 6.2 Car Model

```python
class Car(db.Model):
    __tablename__ = "car"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    brand = db.Column(db.String(100), nullable=False, index=True)
    brand_ar = db.Column(db.Unicode(100), nullable=True)       # Arabic localization
    model = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    price_per_day = db.Column(Numeric(10, 2), nullable=False, index=True)
    status = db.Column(db.String(50), default="available", index=True)
    average_rating = db.Column(db.Float, default=0.0)

    # Relationships
    bookings = db.relationship("Booking", backref="car", lazy="dynamic")
    reviews = db.relationship("Review", backref="car", cascade="all, delete-orphan")
    images = db.relationship("CarImage", backref="car", cascade="all, delete-orphan")
    unavailable_dates = db.relationship("CarUnavailableDate", backref="car", cascade="all, delete-orphan")
```

### 6.3 Booking Model

```python
class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False, index=True)
    renter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    total_price = db.Column(Numeric(10, 2), nullable=True)
    status = db.Column(db.String(50), default="pending", index=True)
    # Status lifecycle: pending → approved / rejected / cancelled
```

### 6.4 Entity-Relationship Summary

| Model | Key Relationships |
|---|---|
| **User** | owns Cars, makes Bookings, writes Reviews, sends/receives Messages |
| **Car** | belongs to User (owner), has Images, Bookings, Reviews, UnavailableDates |
| **Booking** | links Car ↔ Renter, tracks rental period and payment |
| **Review** | links Renter ↔ Car, updates Car.average_rating |
| **Message** | links Sender ↔ Receiver for in-app chat |
| **Notification** | belongs to User, auto-created on events |
| **OTP** | belongs to User, hashed with Werkzeug, has expiry and attempt limit |
| **Favorite** | links User ↔ Car (wishlist) |
| **SearchHistory** | belongs to User, stores recent search queries |
| **PartnerApplication** | belongs to User, tracks partner program requests |

---

## 7. Serialization Schemas

Marshmallow schemas handle input **validation** and output **serialization** with role-based field exposure:

```python
# Public schema — safe to expose to other users
class UserPublicSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(dump_only=True)
    class Meta:
        model = User
        fields = ("id", "name", "role", "nationality", "profile_image")

# Private schema — only for the authenticated user themselves
class UserPrivateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = (
            "id", "name", "email", "phone", "role", "nationality", "is_active",
            "approval_status", "id_image", "license_image", "passport_image",
            "preferred_language", "payout_method", "theme", "profile_image"
        )

# Car schema with nested relationships and validation
class CarSchema(ma.SQLAlchemyAutoSchema):
    owner = fields.Nested(UserPublicSchema(), dump_only=True)
    reviews = fields.List(fields.Nested(ReviewSchema(...)), dump_only=True)
    images = fields.List(fields.Nested(CarImageSchema), dump_only=True)

    year = fields.Integer(
        required=True,
        validate=validate.Range(min=2000, max=current_year)
    )
    price_per_day = fields.Float(
        required=True,
        validate=validate.Range(min=1, error="Price must be greater than 0")
    )
```

---

## 8. API Endpoints

### 8.1 Authentication (`/auth`)

| Method | Endpoint | Description | Rate Limit |
|---|---|---|---|
| POST | `/auth/register` | Register new user + send OTP | 5/min |
| POST | `/auth/verify-otp` | Verify OTP and activate account | 10/hr |
| POST | `/auth/resend-otp` | Resend verification code | 3/hr |
| POST | `/auth/login` | Login with email/phone + password | 10/min |
| POST | `/auth/forgot-password` | Request password reset OTP | 3/hr |
| POST | `/auth/verify-reset-code` | Verify reset code | 5/hr |
| POST | `/auth/reset-password` | Reset password with OTP | 3/hr |
| POST | `/auth/change-password` | Change password (authenticated) | 5/hr |

**Registration Flow with OTP Verification:**

```python
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    # 1. Normalize email
    data["email"] = data["email"].strip().lower()

    # 2. Validate role (only "owner" or "renter")
    requested_role = data.get("role", "renter").strip().lower()
    if requested_role not in ["owner", "renter"]:
        return jsonify({"error": "Invalid role"}), 400

    # 3. Validate password strength
    password_error = validate_password(password)  # min 8 chars, upper, lower, digit
    if password_error:
        return jsonify({"error": password_error}), 400

    # 4. Schema validation + uniqueness check
    schema = UserRegisterSchema()
    new_user_data = schema.load(data)
    if User.query.filter_by(email=new_user_data.email).first():
        return jsonify({"error": "Email already registered"}), 400

    # 5. Create user (inactive) and send OTP
    user = new_user_data
    user.set_password(password)
    user.is_active = False
    db.session.add(user)
    db.session.commit()

    # 6. Generate and send OTP via email
    otp_plain = generate_numeric_otp()
    otp_entry = OTP(user_id=user.id, otp_hash=hash_otp(otp_plain),
                    expires_at=otp_expiry_datetime())
    db.session.add(otp_entry)
    db.session.commit()
    send_otp_email(user.email, otp_plain)

    return jsonify({"message": "User created. Verification code sent.",
                    "user_id": user.id}), 201
```

**Password Validation:**

```python
def validate_password(password: str) -> str | None:
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one digit"
    return None
```

---

### 8.2 Cars (`/cars`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/cars` | Add a new car (owner only) | Required |
| GET | `/cars` | List cars with filters + pagination | Optional |
| GET | `/cars/my-cars` | Owner's car listings | Required |
| GET | `/cars/<id>` | Car details | Optional |
| PUT | `/cars/<id>` | Update car (owner only) | Required |
| DELETE | `/cars/<id>` | Delete car (checks active bookings) | Required |
| GET | `/cars/<id>/availability` | Check date availability | Required |
| POST | `/cars/<id>/block-dates` | Block dates (owner only) | Required |

**Car Listing with Advanced Filtering and Caching:**

```python
@cars_bp.route("", methods=["GET"])
@jwt_required(optional=True)
@cache.cached(timeout=60, query_string=True)
def list_cars():
    # Filters: brand, model, year range, price range, color, transmission, location
    brand = request.args.get('brand', type=str)
    min_price = request.args.get('min_price', type=float)
    available_from_str = request.args.get('available_from', type=str)

    query = Car.query
    if brand:
        query = query.filter(func.lower(Car.brand).like(
            f"%{escape_like(brand.lower())}%"))

    # Date-based availability: exclude cars with conflicting bookings or blocked dates
    if available_from_str and available_to_str:
        conflicting_bookings = db.session.query(Booking.car_id).filter(
            Booking.status == 'approved',
            Booking.start_date < available_to,
            Booking.end_date > available_from
        ).distinct()

        conflicting_blocks = db.session.query(CarUnavailableDate.car_id).filter(
            CarUnavailableDate.start_date < available_to,
            CarUnavailableDate.end_date > available_from
        ).distinct()

        query = query.filter(
            Car.id.notin_(conflicting_bookings),
            Car.id.notin_(conflicting_blocks),
            Car.status == 'available'
        )

    # Paginated response
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "cars": CarSchema(many=True).dump(pagination.items),
        "total_cars": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page,
        "has_next": pagination.has_next
    }), 200
```

**LIKE Injection Prevention:**

```python
def escape_like(value: str) -> str:
    """Escape LIKE wildcards to prevent pattern manipulation."""
    return value.replace('%', '\\%').replace('_', '\\_')
```

---

### 8.3 Bookings (`/bookings`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/bookings` | Create booking request | Required |
| GET | `/bookings` | List bookings (role-based) | Required |
| GET | `/bookings/<id>` | Booking details | Required |
| GET | `/bookings/calendar` | Calendar events format | Required |
| POST | `/bookings/<id>/approve` | Approve booking (owner) | Required |
| POST | `/bookings/<id>/reject` | Reject booking (owner) | Required |
| POST | `/bookings/<id>/cancel` | Cancel booking (renter) | Required |

**Booking Approval with Conflict Resolution:**

```python
@bookings_bp.route("/<int:booking_id>/approve", methods=["POST"])
@jwt_required()
def approve_booking(booking_id):
    # Verify ownership
    car = Car.query.get(booking.car_id)
    if not car or car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    # Check for date conflicts with other approved bookings
    existing_approved = Booking.query.filter(
        Booking.car_id == car.id,
        Booking.status == 'approved',
        Booking.id != booking_id,
        Booking.start_date < end_date,
        Booking.end_date > start_date
    ).first()

    if existing_approved:
        return jsonify({"msg": "Conflicts with another approved booking."}), 409

    booking.status = "approved"

    # Auto-reject conflicting pending bookings
    conflicting_pending = Booking.query.filter(
        Booking.car_id == car.id, Booking.status == 'pending',
        Booking.id != booking_id,
        Booking.start_date < end_date, Booking.end_date > start_date
    ).all()
    for b in conflicting_pending:
        b.status = "rejected"
        notify_booking_rejected(b.renter_id, b.id, f"{car.brand} {car.model}")

    # Notify renter + send email
    notify_booking_approved(booking.renter_id, booking.id, f"{car.brand} {car.model}")
    db.session.commit()
    send_booking_approved_email(renter.email, booking.id, ...)
```

---

### 8.4 Users (`/users`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/profile` | Get authenticated user's profile |
| PUT | `/users/profile` | Update profile fields |
| POST | `/users/upload-documents` | Upload KYC documents (ID, license, etc.) |
| POST | `/users/profile/photo` | Upload profile picture |

---

### 8.5 Other Endpoints

| Blueprint | Prefix | Key Endpoints |
|---|---|---|
| **Reviews** | `/reviews` | POST (add), GET (list with pagination), DELETE |
| **Messages** | `/messages` | POST (send), GET `/<user_id>` (conversation), GET `/inbox` |
| **Notifications** | `/notifications` | GET (list), GET `/unread-count`, POST `/mark-read` |
| **Favorites** | `/favorites` | GET (list), POST `/<car_id>`, DELETE `/<car_id>` |
| **Search** | `/search` | GET/POST/DELETE `/history` |
| **Partner** | `/partner` | POST `/apply`, GET `/status` |
| **Static Pages** | `/pages` | GET `/privacy-policy`, `/terms`, `/invite-info` |

---

## 9. Security Implementation

### 9.1 Authentication & Authorization

- **JWT tokens** with 30-minute access expiry and 30-day refresh
- **Role-based access** enforced per-endpoint via `get_jwt()` claims
- **Password hashing** using Werkzeug's `generate_password_hash`
- **OTP hashing** — OTP codes are never stored in plaintext:

```python
# app/utils/otp_utils.py
def generate_numeric_otp(length=6) -> str:
    """Cryptographically secure OTP generation."""
    start = 10**(length - 1)
    end = (10**length) - 1
    return str(secrets.randbelow(end - start + 1) + start)

def hash_otp(otp_plain: str) -> str:
    return generate_password_hash(otp_plain)

def verify_otp_hash(hashed: str, otp_plain: str) -> bool:
    return check_password_hash(hashed, otp_plain)
```

### 9.2 Rate Limiting

Every sensitive endpoint is rate-limited to prevent brute-force attacks:

| Endpoint | Limit |
|---|---|
| Registration | 5 per minute |
| Login | 10 per minute |
| OTP Verification | 10 per hour |
| Password Reset | 3 per hour |
| OTP Resend | 3 per hour |

### 9.3 Webhook Security (HMAC-SHA256)

Communication from the .NET management backend is authenticated using HMAC-SHA256 signatures:

```python
# app/routes/rently_webhooks.py
def _verify_signature(payload_bytes: bytes, signature: str) -> bool:
    secret = current_app.config.get("RENTLY_WEBHOOK_SECRET", "")
    expected = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@rently_webhooks_bp.route("/rently", methods=["POST"])
def receive_webhook():
    signature = request.headers.get("X-Rently-Signature", "")
    event_name = request.headers.get("X-Rently-Event", "")
    raw_body = request.get_data()

    if not signature or not _verify_signature(raw_body, signature):
        return jsonify({"error": "Invalid signature"}), 401

    # Route to event-specific handler
    handler = EVENT_HANDLERS.get(event_name)
    result = handler(event_data)
    return jsonify({"status": "processed", "detail": result}), 200

# Supported events
EVENT_HANDLERS = {
    "payment.created":          _handle_payment_created,
    "payment.updated":          _handle_payment_updated,
    "payment.refund_requested": _handle_payment_refund,
    "user.updated":             _handle_user_updated,
    "car.status_changed":       _handle_car_status_changed,
}
```

### 9.4 Input Validation & Protection

- **LIKE injection prevention** via `escape_like()` in search queries
- **File type validation** (only png, jpg, jpeg, webp allowed)
- **File size limit** (10 MB max via `MAX_CONTENT_LENGTH`)
- **Email normalization** (`.strip().lower()`)
- **User enumeration prevention** on forgot-password endpoint
- **Self-booking prevention** — owners cannot book their own cars
- **IDOR protection** — ownership checks on all mutation endpoints

---

## 10. Notification System

The application features an **automatic in-app notification system** that triggers on key events:

```python
# app/utils/notification_utils.py
def notify(user_id, title, message, notif_type="general"):
    notif = Notification(
        user_id=user_id, title=title, message=message,
        type=notif_type, is_read=False
    )
    db.session.add(notif)
    return notif

# Auto-triggered notifications:
# - notify_booking_created()   → Owner gets notified of new booking request
# - notify_booking_approved()  → Renter gets notified of approval
# - notify_booking_rejected()  → Renter gets notified of rejection
# - notify_booking_cancelled() → Owner gets notified of cancellation
# - notify_new_review()        → Owner gets notified of new car review
# - notify_new_message()       → Receiver gets notified of new message
```

---

## 11. Deployment

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/

ENV FLASK_ENV=production \
    FLASK_APP=manage.py
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "manage:app"]
```

### Entry Point

```python
# manage.py
from app import create_app
app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    app.run(host=host, port=port, debug=debug_mode)
```

---

## 12. Database Seeding

The project includes a comprehensive seeder (`seed.py`) that generates realistic Egyptian test data:

| Entity | Count | Details |
|---|---|---|
| Users | 1,000 | Egyptian names, 85% renters / 15% owners |
| Cars | 300 | 11 brands with Arabic translations, Egyptian cities |
| Bookings | 3,000 | Random dates spanning past year to 6 months ahead |
| Reviews | 1,500 | Ratings 2–5, linked to valid renter-car pairs |
| Notifications | ~1,500 | Mixed types across 300 users |
| Search History | ~1,200 | Realistic Arabic/English search queries |

---

## 13. API Response Format

All list endpoints follow a consistent **paginated response format**:

```json
{
  "cars": [ ... ],
  "total_cars": 150,
  "total_pages": 15,
  "current_page": 1,
  "has_next": true,
  "has_prev": false
}
```

Error responses follow a consistent format:

```json
{
  "error": "Email already registered"
}
// or with field-level validation errors:
{
  "msg": "Invalid data provided",
  "errors": { "email": ["Not a valid email address."] }
}
```
