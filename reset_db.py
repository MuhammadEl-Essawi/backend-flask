import os
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database  # السطر السحري الجديد

load_dotenv()

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    if not database_exists(db_url):
        print("🛠️ Database not found! Creating it automatically...")
        create_database(db_url)
        print("✅ Database created successfully!")
    else:
        print("⚡ Database already exists. Moving to tables...")

    print("🗑️ Dropping all tables...")
    db.drop_all()
    
    print("✅ Creating all tables...")
    db.create_all()
    
    print("🎉 Database reset completely and ready for seeding!")