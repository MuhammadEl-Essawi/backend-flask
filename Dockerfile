# 1️⃣ استخدم صورة Python خفيفة
FROM python:3.12-slim

# 2️⃣ عرّف مجلد العمل
WORKDIR /app

# 3️⃣ انسخ الملفات الخاصة بالrequirements الأول (علشان الكاش)
COPY requirements.txt /app/

# 4️⃣ سطّب المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ انسخ باقي ملفات المشروع
COPY . /app/

# 6️⃣ عرّف متغيرات البيئة
ENV FLASK_ENV=production \
    FLASK_APP=manage.py

# 7️⃣ وضّح البورت
EXPOSE 5000

# 8️⃣ شغل السيرفر
CMD ["python", "manage.py"]
