import requests
from flask_mail import Message
from flask import current_app
from ..extensions import mail

def send_otp_email(recipient_email, otp_code):
    """
    Send OTP either via Mailtrap API or fallback to Flask-Mail SMTP
    """
    api_token = current_app.config.get("MAILTRAP_API_TOKEN")

    if api_token:  # ✅ استخدم Mailtrap API لو التوكن موجود
        try:
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            data = {
                "from": {"email": "hello@demomailtrap.co", "name": "Car Rent System"},
                "to": [{"email": recipient_email}],
                "subject": "Your OTP Verification Code",
                "text": f"Your OTP code is: {otp_code}\n\nThis code expires in 5 minutes.",
                "category": "OTP"
            }
            response = requests.post("https://send.api.mailtrap.io/api/send", headers=headers, json=data)
            if response.status_code in (200, 202):
                current_app.logger.info(f"✅ OTP sent to {recipient_email} via Mailtrap API")
                return True
        except Exception as e:
            current_app.logger.warning(f"Mailtrap failed: {e}")

    # 🔁 لو Mailtrap فشل أو التوكن مش موجود استخدم Flask-Mail العادي
    try:
        msg = Message(
            subject="Your OTP Code",
            recipients=[recipient_email],
            body=f"Your OTP code is: {otp_code}"
        )
        mail.send(msg)
        current_app.logger.info(f"✅ OTP sent to {recipient_email} via Flask-Mail")
        return True
    except Exception as e:
        current_app.logger.exception(f"❌ Both methods failed: {e}")
        return False
