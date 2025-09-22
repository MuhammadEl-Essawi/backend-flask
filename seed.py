from app.extensions import db
from app.models import Car, User
from werkzeug.security import generate_password_hash
from manage import app

with app.app_context():
    # ✅ Create Owner
    owner = User.query.filter_by(email="owner@example.com").first()
    if not owner:
        owner = User(
            name="Owner User",
            email="owner@example.com",
            password=generate_password_hash("123456"),
            role="owner"
        )
        db.session.add(owner)
        db.session.commit()
        print("✅ Owner user created: owner@example.com / 123456")

    # ✅ Create Renter
    renter = User.query.filter_by(email="renter@example.com").first()
    if not renter:
        renter = User(
            name="Renter User",
            email="renter@example.com",
            password=generate_password_hash("123456"),
            role="renter"
        )
        db.session.add(renter)
        db.session.commit()
        print("✅ Renter user created: renter@example.com / 123456")

    # ✅ Add Cars (only if not already added)
    if Car.query.count() == 0:
        cars_data = [
            {"model": "Hyundai Elantra", "price_per_day": 800},
            {"model": "Kia Cerato", "price_per_day": 750},
            {"model": "Toyota Corolla", "price_per_day": 900},
            {"model": "Mitsubishi Lancer", "price_per_day": 700},
            {"model": "Chevrolet Optra", "price_per_day": 650},
            {"model": "Renault Logan", "price_per_day": 600},
            {"model": "Nissan Sunny", "price_per_day": 650},
            {"model": "Skoda Octavia", "price_per_day": 950},
            {"model": "Honda Civic", "price_per_day": 1000},
            {"model": "Mercedes C180", "price_per_day": 2000},
        ]

        for car_data in cars_data:
            car = Car(
                model=car_data["model"],
                price_per_day=car_data["price_per_day"],
                available=True,
                owner_id=owner.id
            )
            db.session.add(car)

        db.session.commit()
        print("🚗 Cars seeded successfully!")
    else:
        print("⚠️ Cars already exist, skipping seeding.")
