from flask import Blueprint

from .auth import auth_bp
from .bookings import bookings_bp
from .cars import cars_bp
from .payments import payments_bp
from .users import users_bp  # 👈 ضيف دا

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(users_bp)  # 👈 ودا كمان
