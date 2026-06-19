"""
Test: Security Tests
=====================
Covers: JWT manipulation, webhook auth, file upload attacks
"""
from helpers import *


def run_jwt_security():
    print_section("JWT TOKEN SECURITY")
    r = TestReport("JWT Security")

    fake_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.fake_signature"

    endpoints = [
        ("GET", "/cars"),
        ("GET", "/bookings"),
        ("GET", "/users/profile"),
        ("GET", "/favorites"),
        ("GET", "/notifications"),
        ("GET", "/messages/inbox"),
        ("GET", "/search/history"),
    ]

    for method, path in endpoints:
        res = requests.get(f"{BASE_URL}{path}", headers=auth_header(fake_token))
        r.check(res.status_code in [401, 422], f"Fake JWT on {path} → 401/422",
                f"Fake JWT on {path} → {res.status_code} (VULNERABILITY!)")

    r.print_summary()
    return r.summary()


def run_webhook_security():
    print_section("WEBHOOK SECURITY")
    r = TestReport("Webhook Security")

    # Payment webhook: no key
    res = requests.post(f"{BASE_URL}/payment-webhooks/confirm-booking", headers=H_JSON,
                        json={"booking_id": 1, "payment_status": "completed"})
    r.check(res.status_code == 401, "Payment webhook: no key → 401", f"Payment webhook: no key → {res.status_code}")

    # Payment webhook: wrong key
    res = requests.post(f"{BASE_URL}/payment-webhooks/confirm-booking",
                        headers={**H_JSON, "X-Internal-Api-Key": "wrong-key"},
                        json={"booking_id": 1, "payment_status": "completed"})
    r.check(res.status_code == 401, "Payment webhook: wrong key → 401", f"Payment webhook: wrong key → {res.status_code}")

    # Admin webhook: no key
    res = requests.post(f"{BASE_URL}/admin-webhooks/update-user-status", headers=H_JSON,
                        json={"user_id": 1, "approval_status": "approved"})
    r.check(res.status_code == 401, "Admin webhook: no key → 401", f"Admin webhook: no key → {res.status_code}")

    # Admin webhook: wrong key
    res = requests.post(f"{BASE_URL}/admin-webhooks/update-user-status",
                        headers={**H_JSON, "X-Internal-Api-Key": "wrong-key"},
                        json={"user_id": 1, "approval_status": "approved"})
    r.check(res.status_code == 401, "Admin webhook: wrong key → 401", f"Admin webhook: wrong key → {res.status_code}")

    r.print_summary()
    return r.summary()


def run_upload_security(owner_token, renter_token):
    print_section("FILE UPLOAD SECURITY")
    r = TestReport("Upload Security")

    # Malicious car files
    files = {
        'car_license_image': ('virus.py', b'print("Hacked")', 'application/x-python'),
        'images': ('hack.exe', b'binarydata', 'application/octet-stream')
    }
    data = {"brand": "HackCar", "model": "Evil", "year": 2025, "price_per_day": 100,
            "location_city": "Cairo", "transmission": "Manual", "license_plate": "HACK-999"}

    res = requests.post(f"{BASE_URL}/cars", headers=auth_header_no_json(owner_token), data=data, files=files)
    r.check(res.status_code != 201 or "virus" not in res.text,
            "Upload .py/.exe as car → rejected/sanitized", "Upload .py/.exe → ACCEPTED (vulnerability!)")

    # PHP as profile photo
    files = {'profile_image': ('shell.php', b'<?php system("ls"); ?>', 'application/x-php')}
    res = requests.post(f"{BASE_URL}/users/profile/photo", headers=auth_header_no_json(renter_token), files=files)
    r.check(res.status_code == 400, "Upload .php as profile → 400", f"Upload .php as profile → {res.status_code}")

    # JSP as partner photo
    files = {'photo': ('backdoor.jsp', b'<% Runtime.exec("ls") %>', 'text/x-java')}
    res = requests.post(f"{BASE_URL}/partner/apply", headers=auth_header_no_json(renter_token),
                        data={"full_name": "H", "email": "h@h.com", "contact": "123",
                              "driving_license_number": "DL", "car_brand": "X", "car_model": "Y"},
                        files=files)
    r.check(res.status_code in [201, 400], "Upload .jsp as partner photo → handled safely",
            f"Upload .jsp → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    run_jwt_security()
    run_webhook_security()
    ot, _ = login("owner@example.com", "password123")
    rt, _ = login("renter@example.com", "password123")
    if ot and rt:
        run_upload_security(ot, rt)
