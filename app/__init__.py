# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, ma, jwt, cors, mail, limiter, migrate, cache 
from .routes.auth import auth_bp
from .routes.cars import cars_bp
from .routes.bookings import bookings_bp
from .routes.users import users_bp
from .routes.admin_webhooks import admin_bp 
from .routes.payment_webhooks import payment_webhooks_bp 
from .routes.reviews import reviews_bp
from .routes.messages import messages_bp
from .routes.notifications import notifications_bp
from .routes.favorites import favorites_bp
from .routes.search import search_bp
from .routes.partner import partner_bp
from .routes.static_pages import static_pages_bp
from .routes.rently_webhooks import rently_webhooks_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"]) 
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app) 

    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(payment_webhooks_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(partner_bp)
    app.register_blueprint(static_pages_bp)
    app.register_blueprint(rently_webhooks_bp)

    return app
