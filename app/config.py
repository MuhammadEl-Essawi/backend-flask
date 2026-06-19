import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv(override=True)

load_dotenv()

def get_env_variable(name: str) -> str:
    """Get a required environment variable or raise an error."""
    var = os.getenv(name)
    if not var:
        raise ValueError(f"CRITICAL: Environment variable '{name}' is not set.")
    return var

class Config:    
    SECRET_KEY = get_env_variable("SECRET_KEY")
    JWT_SECRET_KEY = get_env_variable("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = get_env_variable("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Mail configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # OTP configuration
    OTP_EXPIRY_SECONDS = int(os.getenv("OTP_EXPIRY_SECONDS", 300))
    OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))

    # Cache configuration
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Upload configuration
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    # Internal API key for webhooks
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")

    # Webhook secret for .NET Management backend (must match Webhooks:Flask:Secret in appsettings)
    RENTLY_WEBHOOK_SECRET = os.getenv("RENTLY_WEBHOOK_SECRET", "DEV_FLASK_WEBHOOK_SECRET")