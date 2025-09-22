from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import User
from app.schemas import UserSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    # validation
    if not data.get("name") or not data.get("email") or not data.get("password") or not data.get("role"):
        return jsonify({"error": "All fields are required: name, email, password, role"}), 400

    # check existing
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_password,   # must match your models/db field name
        role=data["role"]
    )

    db.session.add(new_user)
    db.session.commit()

    # return created user (password excluded by schema)
    return UserSchema().jsonify(new_user), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    # identity must be string
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": UserSchema().dump(user)
    }), 200
