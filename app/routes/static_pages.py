# app/routes/static_pages.py
from flask import Blueprint, jsonify

static_pages_bp = Blueprint("static_pages", __name__, url_prefix="/pages")


@static_pages_bp.route("/privacy-policy", methods=["GET"])
def privacy_policy():
    return jsonify({
        "title": "Privacy Policy",
        "content": (
            "At Rently, we value your privacy. This policy explains how we collect, "
            "use, and protect your personal information when you use our car rental platform.\n\n"
            "1. Information We Collect: Name, email, phone number, nationality, "
            "payment information, and location data.\n\n"
            "2. How We Use Your Information: To process bookings, verify identity, "
            "communicate with you, and improve our services.\n\n"
            "3. Data Security: We use industry-standard encryption to protect your data.\n\n"
            "4. Contact: For questions about this policy, contact us at support@rently.com."
        ),
        "last_updated": "2026-01-01"
    }), 200


@static_pages_bp.route("/terms", methods=["GET"])
def terms_of_service():
    return jsonify({
        "title": "Terms of Service",
        "content": (
            "By using Rently, you agree to the following terms:\n\n"
            "1. You must be 18 years or older to use this service.\n\n"
            "2. All bookings are subject to availability and owner approval.\n\n"
            "3. Renters are responsible for any damage during the rental period.\n\n"
            "4. Cancellation policies apply as specified at time of booking.\n\n"
            "5. Rently reserves the right to suspend accounts that violate these terms."
        ),
        "last_updated": "2026-01-01"
    }), 200


@static_pages_bp.route("/invite-info", methods=["GET"])
def invite_info():
    """
    Returns invite/referral program information.
    """
    return jsonify({
        "title": "Invite Friends",
        "message": "Share Rently with your friends and earn rewards!",
        "referral_link_template": "https://rently.app/invite/{user_id}",
        "reward": "Get 50 LE credit for each friend who completes their first booking."
    }), 200
