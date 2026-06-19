# app/routes/search.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import SearchHistory
from app.schemas import SearchHistorySchema

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/history", methods=["GET"])
@jwt_required()
def get_search_history():
    user_id = int(get_jwt_identity())

    history = db.session.query(SearchHistory).filter_by(user_id=user_id)\
        .order_by(SearchHistory.created_at.desc())\
        .limit(20).all()

    return jsonify({
        "history": SearchHistorySchema(many=True).dump(history)
    }), 200


@search_bp.route("/history", methods=["POST"])
@jwt_required()
def save_search():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    query_text = data.get("query", "").strip()
    if not query_text:
        return jsonify({"msg": "Query is required"}), 400

    # Avoid duplicates — remove old entry with same query
    db.session.query(SearchHistory).filter_by(user_id=user_id, query=query_text).delete()

    entry = SearchHistory(user_id=user_id, query=query_text)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"msg": "Search saved"}), 201


@search_bp.route("/history", methods=["DELETE"])
@jwt_required()
def clear_search_history():
    user_id = int(get_jwt_identity())
    db.session.query(SearchHistory).filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"msg": "Search history cleared"}), 200


@search_bp.route("/history/<int:history_id>", methods=["DELETE"])
@jwt_required()
def delete_search_entry(history_id):
    user_id = int(get_jwt_identity())
    entry = db.session.query(SearchHistory).get(history_id)

    if not entry:
        return jsonify({"msg": "Search entry not found"}), 404

    if entry.user_id != user_id:
        return jsonify({"msg": "Not your search history"}), 403

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"msg": "Search entry deleted"}), 200

