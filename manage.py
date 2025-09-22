import os
from app import create_app
from app.extensions import db

app = create_app()

# ✅ تحديد المسار الحقيقي لقاعدة البيانات
db_path = os.path.abspath("data.db")
print(f"📂 Database will be stored at: {db_path}")

with app.app_context():
    # 🗑 اعمل Drop لكل الجداول (اختياري لو عايز تبدأ من جديد)
    # db.drop_all()

    # ✅ اعمل Create للجداول لو مش موجودة
    db.create_all()
    print("🎉 Database & tables created successfully!")

if __name__ == "__main__":
    app.run(debug=True)
