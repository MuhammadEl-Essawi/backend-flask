import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException 

TW_SID = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM")

def send_otp_sms(to_number: str, otp_code: str) -> bool:
    """
    """
    
    if not (TW_SID and TW_TOKEN and TW_FROM):
        print("CRITICAL ERROR: Twilio configuration is missing in .env file.")
        return False
        
    if os.getenv("FLASK_ENV") == "development":
        print("-" * 30)
        print(f"--- FAKE SMS [DEV MODE] ---")
        print(f"--- To: {to_number}")
        print(f"--- Code: {otp_code}")
        print("-" * 30)
        return True 

    try:
        client = Client(TW_SID, TW_TOKEN)
        body = f"Your verification code: {otp_code}"
        
        message = client.messages.create(
            body=body,
            from_=TW_FROM,
            to=to_number
        )
        
        print(f"Successfully sent SMS. SID: {message.sid}")
        return True
        
    except TwilioRestException as e:
        print(f"Error: Failed to send SMS via Twilio to {to_number}. Reason: {e}")
        return False
        
    except Exception as e:
        print(f"An unexpected error occurred during SMS sending: {e}")
        return False