import os
from dotenv import load_dotenv
from flask import Flask
from .extensions import db, ma, jwt, cors
from .routes.auth import auth_bp
from .routes.cars import cars_bp
from .routes.bookings import bookings_bp
from .routes.payments import payments_bp

# load .env file from project root (if exists)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(ROOT_DIR, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def create_app():
    app = Flask(__name__)

    # تحميل الإعدادات من المتغيرات البيئية
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__),'data.db')}")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config["ENV"] = os.getenv("FLASK_ENV", "development")

    # تهيئة الإضافات
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    # استيراد الموديلات هنا (كي يعرف SQLAlchemy الجداول)
    from . import models  # important: ensures models are registered before create_all()

    # تسجيل Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)

    return app
