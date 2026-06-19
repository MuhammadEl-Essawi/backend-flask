from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Review, Car, Booking, User
from app.schemas import ReviewSchema
from marshmallow import ValidationError
from ..utils.notification_utils import notify_new_review

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")

@reviews_bp.route("", methods=["POST"])
@jwt_required()
def add_review():
    data = request.get_json() or {}
    
    user_id = int(get_jwt_identity())
    
    car_id = data.get("car_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not car_id or not rating:
        return jsonify({"msg": "car_id and rating are required"}), 400

    car = Car.query.get(car_id)
    if not car:
        return jsonify({"msg": "Car not found"}), 404

    
    has_booked = Booking.query.filter_by(
        car_id=car_id, 
        renter_id=user_id, 
        status='approved' 
    ).first()

    if not has_booked:
       return jsonify({"msg": "You can only review cars you have booked/approved."}), 403

    existing_review = Review.query.filter_by(car_id=car_id, renter_id=user_id).first()
    if existing_review:
        return jsonify({"msg": "You have already reviewed this car"}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({"msg": "Rating must be between 1 and 5"}), 400

    review = Review(
        renter_id=user_id,
        car_id=car_id,
        rating=int(rating),
        comment=comment
    )

    db.session.add(review)
    db.session.flush()  # ensure the new review is in the session

    all_reviews = Review.query.filter_by(car_id=car_id).all()
    total_rating = sum(r.rating for r in all_reviews)
    count = len(all_reviews)
    car.average_rating = round(total_rating / count, 1) if count > 0 else 0.0

    # Auto-notify car owner
    reviewer = User.query.get(user_id)
    notify_new_review(
        owner_id=car.owner_id,
        car_name=f"{car.brand} {car.model}",
        rating=int(rating),
        reviewer_name=reviewer.name if reviewer else "A user"
    )

    db.session.commit()

    return ReviewSchema().jsonify(review), 201


@reviews_bp.route("", methods=["GET"])
def list_reviews():
    car_id = request.args.get("car_id", type=int)
    renter_id = request.args.get("renter_id", type=int)

    query = Review.query

    if car_id:
        query = query.filter_by(car_id=car_id)
    
    if renter_id:
        query = query.filter_by(renter_id=renter_id)

    reviews_query = query.order_by(Review.created_at.desc())

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "reviews": ReviewSchema(many=True).dump(pagination.items),
        "total": pagination.total,
        "total_pages": pagination.pages,
        "current_page": page
    }), 200


@reviews_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    user_id = int(get_jwt_identity())
    review = Review.query.get_or_404(review_id)

    if review.renter_id != user_id:
        return jsonify({"msg": "You can only delete your own reviews"}), 403

    db.session.delete(review)
    
    car = Car.query.get(review.car_id)
    remaining_reviews = Review.query.filter(Review.car_id == car.id, Review.id != review_id).all()
    
    if remaining_reviews:
        total = sum([r.rating for r in remaining_reviews])
        car.average_rating = round(total / len(remaining_reviews), 1)
    else:
        car.average_rating = 0.0

    db.session.commit()

    return jsonify({"msg": "Review deleted successfully"}), 200