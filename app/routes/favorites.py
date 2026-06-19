# app/routes/favorites.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Favorite, Car
from app.schemas import CarSchema

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")

@favorites_bp.route("", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = int(get_jwt_identity())
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Car.query.join(Favorite, Favorite.car_id == Car.id)\
        .filter(Favorite.user_id == user_id)\
        .order_by(Favorite.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "favorites": CarSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page
    }), 200

@favorites_bp.route("/<int:car_id>", methods=["POST"])
@jwt_required()
def add_favorite(car_id):
    user_id = int(get_jwt_identity())
    
    if not Car.query.get(car_id):
        return jsonify({"msg": "Car not found"}), 404
        
    if Favorite.query.filter_by(user_id=user_id, car_id=car_id).first():
        return jsonify({"msg": "Already in favorites"}), 400
        
    fav = Favorite(user_id=user_id, car_id=car_id)
    db.session.add(fav)
    db.session.commit()
    
    return jsonify({"msg": "Added to favorites"}), 201

@favorites_bp.route("/<int:car_id>", methods=["DELETE"])
@jwt_required()
def remove_favorite(car_id):
    user_id = int(get_jwt_identity())
    
    fav = Favorite.query.filter_by(user_id=user_id, car_id=car_id).first()
    if not fav:
        return jsonify({"msg": "Not in favorites"}), 404
        
    db.session.delete(fav)
    db.session.commit()
    
    return jsonify({"msg": "Removed from favorites"}), 200