# app/__init__.py
import os
from flask import Flask
from .extensions import db, ma, jwt, cors, mail, limiter
from .routes.auth import auth_bp
from .routes.cars import cars_bp
from .routes.bookings import bookings_bp
from .routes.payments import payments_bp
from .extensions import db, ma, jwt, cors, mail, limiter, migrate
from app.routes.users import users_bp


def create_app():
    app = Flask(__name__)

    # absolute path to ensure data.db is created at project root
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, os.pardir))
    db_path = os.path.join(project_root, "data.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")

    # Mail config (example; set env vars in .env)
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587") or 587)
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL", "False") == "True"

    # OTP config
    app.config["OTP_EXPIRY_SECONDS"] = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
    app.config["OTP_LENGTH"] = int(os.getenv("OTP_LENGTH", 6))

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(users_bp)

    return app
