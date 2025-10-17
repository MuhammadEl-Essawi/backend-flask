# app/utils/sms_utils.py
import os
from twilio.rest import Client

TW_SID = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM")

def send_otp_sms(to_number: str, otp_code: str):
    if not (TW_SID and TW_TOKEN and TW_FROM):
        raise RuntimeError("Twilio config missing")
    client = Client(TW_SID, TW_TOKEN)
    body = f"Your verification code: {otp_code}"
    client.messages.create(body=body, from_=TW_FROM, to=to_number)
