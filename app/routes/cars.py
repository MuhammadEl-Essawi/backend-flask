from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Car

cars_bp = Blueprint("cars", __name__, url_prefix="/cars")

# 🟢 إضافة عربية جديدة
@cars_bp.route("", methods=["POST"])
@jwt_required()
def add_car():
    data = request.get_json()

    required_fields = ("brand", "model", "year", "price_per_day")
    if not all(field in data for field in required_fields):
        return jsonify({"msg": f"Missing fields. Required: {required_fields}"}), 400

    user_id = get_jwt_identity()

    new_car = Car(
        brand=data["brand"],
        model=data["model"],
        year=data["year"],
        price_per_day=data["price_per_day"],
        owner_id=user_id
    )

    db.session.add(new_car)
    db.session.commit()

    return jsonify({"msg": "Car added successfully"}), 201


# 🟢 عرض كل العربيات
@cars_bp.route("", methods=["GET"])
@jwt_required()
def list_cars():
    cars = Car.query.all()
    cars_list = [
        {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "year": car.year,
            "price_per_day": car.price_per_day,
            "owner_id": car.owner_id
        }
        for car in cars
    ]
    return jsonify(cars_list), 200
