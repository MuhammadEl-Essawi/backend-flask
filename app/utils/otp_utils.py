# app/utils/otp_utils.py
import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))
OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))  # default 5 minutes

def generate_numeric_otp(length: int = OTP_LENGTH) -> str:
    if length <= 0:
        length = 6
    start = 10**(length-1)
    end = (10**length) - 1
    return str(random.randint(start, end))

def hash_otp(otp_plain: str) -> str:
    return generate_password_hash(otp_plain)

def verify_otp_hash(hashed: str, otp_plain: str) -> bool:
    return check_password_hash(hashed, otp_plain)

def otp_expiry_datetime() -> datetime:
    return datetime.utcnow() + timedelta(seconds=OTP_EXPIRY_SECONDS)
