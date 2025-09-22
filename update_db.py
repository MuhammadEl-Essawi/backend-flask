# update_db.py
from app.extensions import db
from app import create_app  # ده الملف اللي بيعمل app = Flask(__name__) أو factory
from sqlalchemy import text

app = create_app()  # لو انت عندك factory function

def add_missing_columns():
    with app.app_context():  # مهم جدًا
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]

            if "password" not in columns:
                conn.execute(text(
                    "ALTER TABLE user ADD COLUMN password VARCHAR(200) NOT NULL DEFAULT ''"
                ))
                print("✅ Column 'password' added to table 'user'.")
            else:
                print("ℹ Column 'password' already exists in 'user'.")

            conn.commit()

if __name__ == "__main__":
    add_missing_columns()
