import os
import random
from dotenv import load_dotenv

load_dotenv()

from faker import Faker
from app import create_app, db
from app.models import User, Car, Booking, Notification, SearchHistory, Review
from datetime import datetime, timedelta

app = create_app()

fake_en = Faker('en_US')
fake_ar = Faker('ar_EG') 

EGYPTIAN_FIRST_NAMES = [
    'Ahmed', 'Muhammad', 'Mahmoud', 'Mostafa', 'Youssef', 'Omar', 'Ali', 'Ibrahim', 'Hassan', 
    'Kareem', 'Tarek', 'Amr', 'Khaled', 'Hesham', 'Yasser', 'Ziad', 'Seif', 'Mazen',
    'Hussein', 'Rami', 'Adel', 'Wael', 'Emad', 'Tamer', 'Hany', 'Amir', 'Maged', 'Ayman', 'Sherif',
    'Salma', 'Nour', 'Mona', 'Nada', 'Mai', 'Sara', 'Farah', 'Mariam', 'Aya', 'Habiba', 'Fatma',
    'Amira', 'Noha', 'Rania', 'Dina', 'Heba', 'Eman', 'Hala', 'Maha', 'Nermeen', 'Rasha', 'Reem',
    'Sahar', 'Samar', 'Shereen', 'Yasmine', 'Zeinab', 'Marwa', 'Shaimaa'
]

EGYPTIAN_LAST_NAMES = [
    'Ali', 'Mahmoud', 'Hassan', 'Ibrahim', 'Samir', 'Kamal', 'Nabil', 'Fawzy', 'Taha', 
    'Othman', 'El-Sayed', 'Radwan', 'Youssef', 'Mansour', 'Salem', 'Fathy', 'Gaber', 'Saeed',
    'Tawfik', 'Saad', 'Salah', 'Soliman', 'Ghoneim', 'Farouk', 'Galal', 'Ezzat', 'Rashad',
    'Abdel-Rahman', 'Abdel-Aziz', 'El-Din', 'Helmy', 'Sadek', 'Shawky', 'Zayed'
]

CAR_BRANDS = ['BMW', 'Mercedes', 'Toyota', 'Hyundai', 'Kia', 'Ford', 'Audi', 'Nissan', 'Chevrolet', 'Peugeot', 'Renault']
ARABIC_BRANDS = {
    'BMW': 'بي إم دبليو',
    'Mercedes': 'مرسيدس',
    'Toyota': 'تويوتا',
    'Hyundai': 'هيونداي',
    'Kia': 'كيا',
    'Ford': 'فورد',
    'Audi': 'أودي',
    'Nissan': 'نيسان',
    'Chevrolet': 'شيفروليه',
    'Peugeot': 'بيجو',
    'Renault': 'رينو'
}

LOCATIONS = ['Cairo', 'Alexandria', 'Giza', 'Sharm El Sheikh', 'Hurghada', 'Mansoura', 'Tanta', 'Suez', 'Ismailia', 'Port Said']
TRANSMISSIONS = ['Automatic', 'Manual']

INSURANCE_TYPES = ['Full Coverage', 'Third Party', 'Basic']
INSURANCE_TYPES_AR = {
    'Full Coverage': 'تأمين شامل',
    'Third Party': 'تأمين ضد الغير',
    'Basic': 'تأمين أساسي'
}

def seed_database():
    with app.app_context():
        print(" Starting database seeding (MASSIVE DATASET)...")
        
        db.create_all()

        users = []
        generated_phones = set()
        generated_emails = set()
        
        print("Creating static test users...")
        test_owner = User(
            first_name="Test",
            last_name="Owner",
            email="owner@example.com",
            phone="01011111111",
            role="owner",
            nationality="Egyptian",
            is_active=True,
            approval_status="approved"
        )
        test_owner.set_password("password123")
        users.append(test_owner)
        db.session.add(test_owner)
        generated_phones.add("01011111111")
        generated_emails.add("owner@example.com")

        test_renter = User(
            first_name="Test",
            last_name="Renter",
            email="renter@example.com",
            phone="01222222222",
            role="renter",
            nationality="Egyptian",
            is_active=True,
            approval_status="approved"
        )
        test_renter.set_password("password123")
        users.append(test_renter)
        db.session.add(test_renter)
        generated_phones.add("01222222222")
        generated_emails.add("renter@example.com")
        
        db.session.commit()

        print("Creating 1000 random users (Renters & Owners)...")
        for _ in range(1000):
            first_name = random.choice(EGYPTIAN_FIRST_NAMES)
            last_name = random.choice(EGYPTIAN_LAST_NAMES)

            while True:
                network = random.choice(['0', '1', '2', '5'])
                phone = f"01{network}{random.randint(1000000, 9999999)}"
                if phone not in generated_phones:
                    generated_phones.add(phone)
                    break
            
            while True:
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99999)}@example.com"
                if email not in generated_emails:
                    generated_emails.add(email)
                    break

            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role=random.choices(['renter', 'owner'], weights=[85, 15])[0],
                nationality='Egyptian',
                is_active=True,
                approval_status='approved'
            )
            user.set_password('SeedPass123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()

        cars = []
        print("Creating 300 cars...")
        owners = [u for u in users if u.role == 'owner']
        if not owners:
            owners = [test_owner]
            
        for _ in range(300):
            chosen_brand = random.choices(list(CAR_BRANDS), weights=[5, 5, 20, 20, 20, 5, 5, 10, 5, 2, 3], k=1)[0]
            chosen_insurance = random.choice(INSURANCE_TYPES)
            owner = random.choice(owners)
            
            car = Car(
                brand=chosen_brand,
                brand_ar=ARABIC_BRANDS[chosen_brand],
                model=fake_en.word().capitalize(),
                model_ar=fake_ar.word(),
                year=random.randint(2012, 2025),
                price_per_day=float(random.randint(300, 5000)),
                location_city=random.choices(LOCATIONS, weights=[30, 20, 10, 5, 5, 10, 5, 5, 5, 5], k=1)[0],
                transmission=random.choices(TRANSMISSIONS, weights=[90, 10], k=1)[0],
                description=fake_en.text(max_nb_chars=200),
                status=random.choices(['available', 'rented', 'maintenance'], weights=[70, 25, 5])[0],
                insurance_details=chosen_insurance,
                insurance_details_ar=INSURANCE_TYPES_AR[chosen_insurance],
                owner_id=owner.id
            )
            cars.append(car)
            db.session.add(car)
        
        db.session.commit()

        print("Creating 3000 bookings...")
        renters = [u for u in users if u.role == 'renter']
        for _ in range(3000):
            date_obj = fake_en.date_between(start_date='-1y', end_date='+6m')
            start_date = datetime(date_obj.year, date_obj.month, date_obj.day) 
            days = random.randint(1, 20)
            end_date = start_date + timedelta(days=days)
            
            random_user = random.choice(renters)
            random_car = random.choice(cars)

            booking = Booking(
                renter_id=random_user.id,
                car_id=random_car.id,
                start_date=start_date, 
                end_date=end_date,
                status=random.choices(['pending', 'confirmed', 'completed', 'cancelled'], weights=[10, 20, 50, 20], k=1)[0]
            )
            db.session.add(booking)

        db.session.commit()

        print("Creating sample notifications...")
        notif_types = ['booking', 'payment', 'review', 'message', 'system']
        for user in random.sample(users, min(300, len(users))):
            for _ in range(random.randint(2, 10)):
                ntype = random.choice(notif_types)
                db.session.add(Notification(
                    user_id=user.id,
                    title=f"Sample {ntype} notification",
                    message=fake_en.sentence(),
                    type=ntype,
                    is_read=random.choice([True, False])
                ))
        db.session.commit()

        print("Creating sample search history...")
        search_queries = ['BMW Cairo', 'Toyota Automatic', 'Cheap Cars Alexandria', 'Mercedes Mansoura', 'Hyundai Giza', 'Kia Sportage', 'Family Car', 'Rent without deposit']
        for user in random.sample(users, min(400, len(users))):
            for q in random.sample(search_queries, k=min(random.randint(1, 5), len(search_queries))):
                db.session.add(SearchHistory(user_id=user.id, query=q))
        db.session.commit()

        print("Creating 1500 sample reviews...")
        for _ in range(1500):
            renter = random.choice(renters)
            car = random.choice(cars)
            if car.owner_id != renter.id:
                existing = Review.query.filter_by(car_id=car.id, renter_id=renter.id).first()
                if not existing:
                    db.session.add(Review(
                        renter_id=renter.id,
                        car_id=car.id,
                        rating=random.randint(2, 5),
                        comment=fake_en.sentence()
                    ))
        db.session.commit()
        
        print(" Database seeded successfully with a MASSIVE dataset!")

if __name__ == '__main__':
    seed_database()