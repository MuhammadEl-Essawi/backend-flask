# app/utils/mail_utils.py
from flask_mail import Message
from ..extensions import mail
from flask import current_app

def send_otp_email(recipient_email, otp_code):
    """
    """
    if not recipient_email:
        current_app.logger.warning("No recipient email provided for OTP")
        return

    if current_app.config.get("ENV") == "development":
        current_app.logger.info(f"--- FAKE EMAIL [DEV OTP] to {recipient_email} ---")
        current_app.logger.info(f"--- Your verification code: {otp_code} ---")
        return 
    subject = "Your Verification Code"
    body = f"Your verification code is: {otp_code}"
    
    msg = Message(
        subject=subject,
        recipients=[recipient_email],
        body=body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER') 
    )
    try:
        mail.send(msg)
        current_app.logger.info(f"OTP email sent to {recipient_email}")
    except Exception as e:
        current_app.logger.exception(f"Failed to send OTP email to {recipient_email}: {e}")

def send_booking_approved_email(recipient_email, booking_id, car_model, start_date, end_date):
    """
    """
    if not recipient_email:
        current_app.logger.warning(f"No recipient email provided for booking {booking_id} approval")
        return

    if current_app.config.get("ENV") == "development":
        current_app.logger.info(f"--- FAKE EMAIL [DEV BOOKING APPROVED] to {recipient_email} ---")
        current_app.logger.info(f"--- Booking ID: {booking_id}, Car: {car_model} ---")
        return

    subject = f"Booking Approved! Your request for {car_model} is confirmed."
    start_str = start_date.strftime('%Y-%m-%d at %I:%M %p') if start_date else 'N/A'
    end_str = end_date.strftime('%Y-%m-%d at %I:%M %p') if end_date else 'N/A'
    
    body = f"""
    Great news!

    Your booking (ID: {booking_id}) for the car '{car_model}' has been approved by the owner.

    Booking Details:
    Start Date: {start_str}
    End Date: {end_str}

    Thank you for choosing our Car Rental service!
    """
    

    msg = Message(
        subject=subject,
        recipients=[recipient_email],
        body=body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    try:
        mail.send(msg)
        current_app.logger.info(f"Booking approval email sent to {recipient_email} for booking {booking_id}")
    except Exception as e:
        current_app.logger.exception(f"Failed to send booking approval email to {recipient_email}: {e}")
