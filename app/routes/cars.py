# app/routes/cars.py
from flask import Blueprint, request, jsonify, current_app 
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Car, Booking, CarImage, CarUnavailableDate, SearchHistory
from app.schemas import CarSchema, CarUnavailableDateSchema
from marshmallow import ValidationError
from sqlalchemy import func 
from datetime import datetime 
from ..extensions import cache 
import os
import uuid
from werkzeug.utils import secure_filename

cars_bp = Blueprint("cars", __name__, url_prefix="/cars")

def escape_like(value: str) -> str:
    """Escape LIKE wildcards to prevent pattern manipulation."""
    return value.replace('%', '\\%').replace('_', '\\_')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_car_file(file, type_prefix):
    if not file or file.filename == '' or not allowed_file(file.filename):
        return None
    upload_root = os.path.join(current_app.root_path, "uploads")
    car_dir = os.path.join(upload_root, "cars")
    os.makedirs(car_dir, exist_ok=True)
    
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{type_prefix}_{uuid.uuid4().hex[:8]}.{ext}"
    file.save(os.path.join(car_dir, unique_filename))
    return f"uploads/cars/{unique_filename}"

# ---------------------------
# 1. إضافة سيارة
# ---------------------------
@cars_bp.route("", methods=["POST"])
@jwt_required()
def add_car():
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can add cars"}), 403

    try:
        data = request.form.to_dict()
        # التعديل: load بترجع object جاهز (new_car) مش dict
        new_car = CarSchema(unknown='EXCLUDE').load(data) 
    except ValidationError as err:
        return jsonify({"msg": "Invalid data provided", "errors": err.messages}), 400

    user_id = get_jwt_identity()
    license_file = request.files.get('car_license_image')
    car_license_path = save_car_file(license_file, "license")

    # التعديل: بنكمل البيانات على الـ object الجاهز
    new_car.owner_id = user_id
    new_car.car_license_image = car_license_path
    new_car.status = "available"
    
    if not new_car.insurance_details:
        new_car.insurance_details = "Comprehensive Insurance"

    db.session.add(new_car)
    db.session.commit()

    images = request.files.getlist('images')
    if images:
        for img in images:
            path = save_car_file(img, f"car_{new_car.id}")
            if path:
                db.session.add(CarImage(car_id=new_car.id, image_path=path))
        db.session.commit()

    return CarSchema().jsonify(new_car), 201


# ---------------------------
# عرض سيارات المالك
# ---------------------------
@cars_bp.route("/my-cars", methods=["GET"])
@jwt_required()
def my_cars():
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can view their cars"}), 403

    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Car.query.filter_by(owner_id=user_id)\
        .order_by(Car.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "cars": CarSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }), 200


# ---------------------------
# تفاصيل سيارة واحدة
# ---------------------------
@cars_bp.route("/<int:car_id>", methods=["GET"])
@jwt_required(optional=True)
def get_car(car_id):
    car = Car.query.get_or_404(car_id)
    return CarSchema().jsonify(car), 200


# ---------------------------
# تعديل سيارة
# ---------------------------
@cars_bp.route("/<int:car_id>", methods=["PUT"])
@jwt_required()
def update_car(car_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can update cars"}), 403

    user_id = int(get_jwt_identity())
    car = Car.query.get_or_404(car_id)

    if car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    data = request.form.to_dict() if request.form else (request.get_json() or {})

    updatable_fields = ["brand", "model", "year", "price_per_day", "transmission",
                        "color", "location_city", "description", "features", "license_plate"]
    for field in updatable_fields:
        if field in data:
            value = data[field]
            if field == "year":
                value = int(value)
            elif field == "price_per_day":
                value = float(value)
            setattr(car, field, value)

    # Handle new images
    new_images = request.files.getlist("images")
    if new_images:
        upload_root = os.path.join(current_app.root_path, "uploads")
        os.makedirs(upload_root, exist_ok=True)
        for image_file in new_images:
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                if ext not in {'png', 'jpg', 'jpeg'}:
                    continue
                unique_name = f"car_{car.id}_{uuid.uuid4().hex[:8]}.{ext}"
                image_file.save(os.path.join(upload_root, unique_name))
                car_img = CarImage(car_id=car.id, image_path=f"uploads/{unique_name}")
                db.session.add(car_img)

    db.session.commit()
    return CarSchema().jsonify(car), 200


# ---------------------------
# حذف سيارة
# ---------------------------
@cars_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def delete_car(car_id):
    claims = get_jwt()
    if claims.get("role") != "owner":
        return jsonify({"msg": "Only owners can delete cars"}), 403

    user_id = int(get_jwt_identity())
    car = Car.query.get_or_404(car_id)

    if car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    # Check for active bookings
    active_bookings = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.status.in_(["pending", "approved"])
    ).count()

    if active_bookings > 0:
        return jsonify({"msg": "Cannot delete car with active bookings. Cancel or complete them first."}), 400

    db.session.delete(car)
    db.session.commit()
    return jsonify({"msg": "Car deleted successfully"}), 200


# ---------------------------
# فحص التاريخ إذا متاح
# ---------------------------
@cars_bp.route("/<int:car_id>/availability", methods=["GET"])
@jwt_required()
def check_availability(car_id):
    car = Car.query.get_or_404(car_id)

    start_str = request.args.get("start_date")
    end_str = request.args.get("end_date")

    if not start_str or not end_str:
        return jsonify({"msg": "start_date and end_date query params are required"}), 400

    try:
        from datetime import datetime
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
        end = datetime.fromisoformat(end_str.replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    # Check approved bookings conflict
    conflict = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.status == 'approved',
        Booking.start_date < end,
        Booking.end_date > start
    ).first()

    # Check owner-blocked dates
    from app.models import CarUnavailableDate
    blocked = CarUnavailableDate.query.filter(
        CarUnavailableDate.car_id == car_id,
        CarUnavailableDate.start_date < end,
        CarUnavailableDate.end_date > start
    ).first()

    is_available = conflict is None and blocked is None

    return jsonify({
        "car_id": car_id,
        "start_date": start_str,
        "end_date": end_str,
        "available": is_available,
        "reason": None if is_available else ("Already booked" if conflict else "Dates blocked by owner")
    }), 200



# ---------------------------
# 2. حظر التواريخ (Blocked Dates)
# ---------------------------
@cars_bp.route("/<int:car_id>/block-dates", methods=["POST"])
@jwt_required()
def block_car_dates(car_id):
    user_id = int(get_jwt_identity())
    car = Car.query.get_or_404(car_id)

    if car.owner_id != user_id:
        return jsonify({"msg": "You don't own this car"}), 403

    data = request.get_json() or {}
    if not data.get("start_date") or not data.get("end_date"):
        return jsonify({"msg": "start_date and end_date are required"}), 400

    try:
        start_date = datetime.fromisoformat(data["start_date"].replace('Z', '+00:00')).replace(tzinfo=None)
        end_date = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    if end_date <= start_date:
        return jsonify({"msg": "End date must be after start date"}), 400

    unavailable = CarUnavailableDate(
        car_id=car.id,
        start_date=start_date,
        end_date=end_date,
        reason=data.get("reason", "Blocked by owner")
    )
    db.session.add(unavailable)
    db.session.commit()

    return jsonify({"msg": "Dates blocked successfully"}), 201


# ---------------------------
# 3. عرض السيارات (مع الفلترة والترتيب)
# ---------------------------
@cars_bp.route("", methods=["GET"])
@jwt_required(optional=True)
@cache.cached(timeout=60, query_string=True) 
def list_cars():
    current_app.logger.debug("Cache miss or expired for GET /cars.") 

    brand = request.args.get('brand', type=str)
    model = request.args.get('model', type=str)
    min_year = request.args.get('min_year', type=int)
    max_year = request.args.get('max_year', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    color = request.args.get('color', type=str) 
    transmission = request.args.get('transmission', type=str) 
    location = request.args.get('location', type=str) 
    available_from_str = request.args.get('available_from', type=str) 
    available_to_str = request.args.get('available_to', type=str)     

    query = Car.query 

    if brand: query = query.filter(func.lower(Car.brand).like(f"%{escape_like(brand.lower())}%")) 
    if model: query = query.filter(func.lower(Car.model).like(f"%{escape_like(model.lower())}%"))
    if min_year: query = query.filter(Car.year >= min_year)
    if max_year: query = query.filter(Car.year <= max_year)
    if min_price: query = query.filter(Car.price_per_day >= min_price)
    if max_price: query = query.filter(Car.price_per_day <= max_price)
    if color: query = query.filter(func.lower(Car.color) == color.lower())
    if transmission: query = query.filter(func.lower(Car.transmission) == transmission.lower())
    if location: query = query.filter(func.lower(Car.location_city).like(f"%{escape_like(location.lower())}%"))

    if available_from_str and available_to_str:
        try:
            available_from = datetime.fromisoformat(available_from_str.replace('Z', '+00:00'))
            available_to = datetime.fromisoformat(available_to_str.replace('Z', '+00:00'))
            
            if available_to <= available_from:
                 return jsonify({"msg": "available_to must be after available_from"}), 400

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

        except ValueError:
            return jsonify({"msg": "Invalid date format"}), 400
    else:
         query = query.filter(Car.status == 'available')

    query = query.order_by(Car.created_at.desc()) 

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) 
    cars_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    cars = cars_pagination.items

    return jsonify({
        "cars": CarSchema(many=True).dump(cars),
        "total_cars": cars_pagination.total,
        "total_pages": cars_pagination.pages,
        "current_page": page,
        "has_next": cars_pagination.has_next,
        "has_prev": cars_pagination.has_prev
    }), 200