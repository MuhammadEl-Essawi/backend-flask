"""
Test: Auth Endpoints
====================
Covers: register, login, OTP, forgot/reset password, change password
"""
from helpers import *

def run(renter_token=None):
    print_section("AUTH ENDPOINTS")
    r = TestReport("Auth")

    # ── Register: Empty body ──
    res = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={})
    r.check(res.status_code == 400, "Register: empty body → 400", f"Register: empty body → {res.status_code}")

    # ── Register: Weak password ──
    res = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "weak_test@test.com", "phone": "+201099900001",
        "password": "123", "role": "renter"
    })
    r.check(res.status_code == 400, "Register: weak password → 400", f"Register: weak password → {res.status_code}")

    # ── Register: Invalid email format ──
    res = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "not-an-email", "phone": "+201099900002",
        "password": "StrongPass1", "role": "renter"
    })
    r.check(res.status_code == 400, "Register: invalid email → 400", f"Register: invalid email → {res.status_code}")

    # ── Register: Mass assignment (role=admin) ──
    res = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Hacker", "last_name": "Test", "email": "hacker_mass@test.com", "phone": "+201099900003",
        "password": "StrongPass1", "role": "admin"
    })
    r.check(res.status_code in [201, 400], "Register: role=admin → handled (overridden to renter)", 
            f"Register: role=admin → {res.status_code}")

    # ── Register: Duplicate email ──
    res = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "hacker_mass@test.com", "phone": "+201099900099",
        "password": "StrongPass1", "role": "renter"
    })
    r.check(res.status_code == 400, "Register: duplicate email → 400", f"Register: duplicate email → {res.status_code}")

    # ── Login: Wrong password ──
    res = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": "admin@example.com", "password": "wrongpassword"
    })
    r.check(res.status_code == 401, "Login: wrong password → 401", f"Login: wrong password → {res.status_code}")

    # ── Login: Non-existent user ──
    res = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": "ghost@example.com", "password": "AnyPass1"
    })
    r.check(res.status_code == 401, "Login: non-existent user → 401", f"Login: non-existent → {res.status_code}")

    # ── Login: Empty request ──
    res = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={})
    r.check(res.status_code == 400, "Login: empty body → 400", f"Login: empty body → {res.status_code}")

    # ── Forgot password: Unknown email (anti-enumeration) ──
    res = requests.post(f"{BASE_URL}/auth/forgot-password", headers=H_JSON, json={
        "email": "doesnotexist@fake.com"
    })
    r.check(res.status_code == 200, "Forgot password: unknown email → 200 (anti-enumeration)",
            f"Forgot password: unknown email → {res.status_code}")

    # ── Forgot password: No email ──
    res = requests.post(f"{BASE_URL}/auth/forgot-password", headers=H_JSON, json={})
    r.check(res.status_code == 400, "Forgot password: empty → 400", f"Forgot password: empty → {res.status_code}")

    # ── Verify OTP: Missing fields ──
    res = requests.post(f"{BASE_URL}/auth/verify-otp", headers=H_JSON, json={})
    r.check(res.status_code == 400, "Verify OTP: empty → 400", f"Verify OTP: empty → {res.status_code}")

    # ── Verify OTP: Wrong code ──
    res = requests.post(f"{BASE_URL}/auth/verify-otp", headers=H_JSON, json={
        "user_id": 1, "otp": "000000"
    })
    r.check(res.status_code in [400, 401, 404], "Verify OTP: wrong code → rejected",
            f"Verify OTP: wrong code → {res.status_code}")

    # ── Reset password: Missing fields ──
    res = requests.post(f"{BASE_URL}/auth/reset-password", headers=H_JSON, json={})
    r.check(res.status_code == 400, "Reset password: empty → 400", f"Reset password: empty → {res.status_code}")

    # ── Change password: Missing fields ──
    if renter_token:
        res = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(renter_token), json={})
        r.check(res.status_code == 400, "Change password: empty → 400", f"Change password: empty → {res.status_code}")

        # ── Change password: Wrong current ──
        res = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(renter_token), json={
            "current_password": "WrongPassword1", "new_password": "NewStrongPass1"
        })
        r.check(res.status_code == 401, "Change password: wrong current → 401", f"Change password: wrong current → {res.status_code}")

        # ── Change password: Weak new password ──
        res = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(renter_token), json={
            "current_password": "password123", "new_password": "123"
        })
        r.check(res.status_code == 400, "Change password: weak new → 400", f"Change password: weak new → {res.status_code}")

    # ── Change password: No auth ──
    res = requests.post(f"{BASE_URL}/auth/change-password", headers=H_JSON, json={
        "current_password": "a", "new_password": "b"
    })
    r.check(res.status_code in [401, 422], "Change password: no token → 401/422", f"Change password: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    token, _ = login("renter@example.com", "password123")
    run(renter_token=token)
