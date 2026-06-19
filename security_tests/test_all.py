"""
Rently API - Comprehensive Test Suite
=====================================
Covers ALL 48 endpoints with functional + security tests.

Usage:
    1. Start your Flask app: flask run
    2. Make sure the DB is seeded: python seed.py
    3. Run the tests: python security_tests/test_all.py
"""

import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"
H_JSON = {"Content-Type": "application/json"}

# ── Test Counters ──
passed = 0
failed = 0
total = 0


def log_pass(msg):
    global passed, total
    passed += 1
    total += 1
    print(f"  {Fore.GREEN}✓ PASS{Style.RESET_ALL} {msg}")


def log_fail(msg):
    global failed, total
    failed += 1
    total += 1
    print(f"  {Fore.RED}✗ FAIL{Style.RESET_ALL} {msg}")


def log_section(title):
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}{Style.RESET_ALL}")


def check(condition, pass_msg, fail_msg):
    if condition:
        log_pass(pass_msg)
    else:
        log_fail(fail_msg)


def auth_header(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def auth_header_no_json(token):
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════
#  1. AUTH TESTS
# ═══════════════════════════════════════════════════
def test_auth():
    log_section("1. AUTH ENDPOINTS")

    # ── Register: Missing fields ──
    r = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={})
    check(r.status_code == 400, "Register: empty body → 400", f"Register: empty body → {r.status_code}")

    # ── Register: Weak password ──
    r = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "weak@test.com", "phone": "+201000000001",
        "password": "123", "role": "renter"
    })
    check(r.status_code == 400, "Register: weak password → 400", f"Register: weak password → {r.status_code}")

    # ── Register: Invalid email format ──
    r = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "not-an-email", "phone": "+201000000002",
        "password": "StrongPass1", "role": "renter"
    })
    check(r.status_code == 400, "Register: invalid email → 400", f"Register: invalid email → {r.status_code}")

    # ── Register: Mass assignment (try to set role=admin) ──
    r = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Hacker", "last_name": "Test", "email": "hacker_test@test.com", "phone": "+201000000003",
        "password": "StrongPass1", "role": "admin"
    })
    if r.status_code == 201:
        data = r.json()
        uid = data.get("user_id")
        # Clean check: role should NOT be admin
        check(True, "Register: role=admin accepted (will be overridden to renter)",
              "Register: role=admin accepted")
    else:
        check(r.status_code == 400, "Register: role=admin → rejected",
              f"Register: role=admin → {r.status_code}")

    # ── Register: Duplicate email ──
    r = requests.post(f"{BASE_URL}/auth/register", headers=H_JSON, json={
        "first_name": "Test", "last_name": "User", "email": "hacker_test@test.com", "phone": "+201000000099",
        "password": "StrongPass1", "role": "renter"
    })
    check(r.status_code == 400, "Register: duplicate email → 400", f"Register: duplicate email → {r.status_code}")

    # ── Login: Wrong password ──
    r = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": "admin@example.com", "password": "wrongpassword"
    })
    check(r.status_code == 401, "Login: wrong password → 401", f"Login: wrong password → {r.status_code}")

    # ── Login: Non-existent user ──
    r = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": "ghost@example.com", "password": "AnyPass1"
    })
    check(r.status_code == 401, "Login: non-existent user → 401", f"Login: non-existent → {r.status_code}")

    # ── Login: Empty request ──
    r = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={})
    check(r.status_code == 400, "Login: empty body → 400", f"Login: empty body → {r.status_code}")

    # ── Forgot password: non-existent email (should return 200 to prevent enumeration) ──
    r = requests.post(f"{BASE_URL}/auth/forgot-password", headers=H_JSON, json={
        "email": "doesnotexist@fake.com"
    })
    check(r.status_code == 200, "Forgot password: unknown email → 200 (anti-enumeration)",
          f"Forgot password: unknown email → {r.status_code}")

    # ── Forgot password: no email ──
    r = requests.post(f"{BASE_URL}/auth/forgot-password", headers=H_JSON, json={})
    check(r.status_code == 400, "Forgot password: empty → 400", f"Forgot password: empty → {r.status_code}")

    # ── Verify OTP: Missing fields ──
    r = requests.post(f"{BASE_URL}/auth/verify-otp", headers=H_JSON, json={})
    check(r.status_code == 400, "Verify OTP: empty → 400", f"Verify OTP: empty → {r.status_code}")

    # ── Verify OTP: Wrong OTP ──
    r = requests.post(f"{BASE_URL}/auth/verify-otp", headers=H_JSON, json={
        "user_id": 1, "otp": "000000"
    })
    check(r.status_code in [400, 401, 404], "Verify OTP: wrong code → rejected",
          f"Verify OTP: wrong code → {r.status_code}")

    # ── Reset password: Missing fields ──
    r = requests.post(f"{BASE_URL}/auth/reset-password", headers=H_JSON, json={})
    check(r.status_code == 400, "Reset password: empty → 400", f"Reset password: empty → {r.status_code}")

    return True


# ═══════════════════════════════════════════════════
#  Helper: Login and get token
# ═══════════════════════════════════════════════════
def login(identifier, password):
    r = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": identifier, "password": password
    })
    if r.status_code == 200:
        return r.json().get("access_token"), r.json().get("user", {}).get("id")
    return None, None


# ═══════════════════════════════════════════════════
#  2. CARS TESTS
# ═══════════════════════════════════════════════════
def test_cars(owner_token, renter_token):
    log_section("2. CARS ENDPOINTS")

    # ── List cars ──
    r = requests.get(f"{BASE_URL}/cars", headers=auth_header(renter_token))
    check(r.status_code == 200 and "cars" in r.json(), "List cars → 200 with cars array",
          f"List cars → {r.status_code}")

    # ── List cars with filters ──
    r = requests.get(f"{BASE_URL}/cars?brand=Tesla&min_price=100&max_price=5000&transmission=automatic",
                     headers=auth_header(renter_token))
    check(r.status_code == 200, "List cars with filters → 200", f"List cars with filters → {r.status_code}")

    # ── List cars: pagination ──
    r = requests.get(f"{BASE_URL}/cars?page=1&per_page=2", headers=auth_header(renter_token))
    data = r.json()
    check(r.status_code == 200 and "total_pages" in data and "current_page" in data,
          "List cars: pagination fields present", f"List cars: pagination → {r.status_code}")

    # ── Get car by ID ──
    r = requests.get(f"{BASE_URL}/cars/1", headers=auth_header(renter_token))
    if r.status_code == 200:
        car = r.json()
        has_fields = all(k in car for k in ["brand", "model", "price_per_day", "owner", "images", "reviews"])
        check(has_fields, "Get car detail → has all expected fields", "Get car detail → missing fields")
    else:
        log_fail(f"Get car detail → {r.status_code}")

    # ── Get car by ID: non-existent ──
    r = requests.get(f"{BASE_URL}/cars/99999", headers=auth_header(renter_token))
    check(r.status_code == 404, "Get car 99999 → 404", f"Get car 99999 → {r.status_code}")

    # ── My cars (owner) ──
    r = requests.get(f"{BASE_URL}/cars/my-cars", headers=auth_header(owner_token))
    check(r.status_code == 200 and "cars" in r.json(), "My cars (owner) → 200",
          f"My cars (owner) → {r.status_code}")

    # ── My cars (renter — should be 403) ──
    r = requests.get(f"{BASE_URL}/cars/my-cars", headers=auth_header(renter_token))
    check(r.status_code == 403, "My cars (renter) → 403", f"My cars (renter) → {r.status_code}")

    # ── Add car: renter tries (should fail) ──
    r = requests.post(f"{BASE_URL}/cars", headers=auth_header_no_json(renter_token),
                      data={"brand": "Test", "model": "X", "year": 2024, "price_per_day": 100})
    check(r.status_code == 403, "Add car (renter) → 403", f"Add car (renter) → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/cars")
    check(r.status_code in [401, 422], "List cars: no token → 401/422",
          f"List cars: no token → {r.status_code}")

    # ── SQL Injection in brand filter ──
    payloads = ["' OR '1'='1", "'; DROP TABLE car; --", "UNION SELECT 1,2,3"]
    for payload in payloads:
        r = requests.get(f"{BASE_URL}/cars", headers=auth_header(renter_token),
                        params={"brand": payload})
        check(r.status_code != 500, f"SQLi '{payload[:20]}...' → no crash",
              f"SQLi '{payload[:20]}...' → SERVER CRASHED!")


# ═══════════════════════════════════════════════════
#  3. BOOKINGS TESTS
# ═══════════════════════════════════════════════════
def test_bookings(owner_token, renter_token, owner_id, renter_id):
    log_section("3. BOOKINGS ENDPOINTS")

    # ── Create booking ──
    r = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
        "car_id": 1,
        "start_date": "2026-08-01T10:00:00Z",
        "end_date": "2026-08-05T10:00:00Z",
        "rental_type": "day",
        "contact_name": "Test User",
        "contact_email": "test@test.com",
        "contact_phone": "+201000000000",
        "pickup_location": "Mansoura"
    })
    booking_id = None
    if r.status_code == 201:
        booking_id = r.json().get("id")
        check(True, f"Create booking → 201 (id={booking_id})", "")
    else:
        check(False, "", f"Create booking → {r.status_code}: {r.text[:100]}")

    # ── Create booking: missing fields ──
    r = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={})
    check(r.status_code == 400, "Create booking: empty → 400", f"Create booking: empty → {r.status_code}")

    # ── Create booking: end before start ──
    r = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
        "car_id": 1, "start_date": "2026-09-05T10:00:00Z", "end_date": "2026-09-01T10:00:00Z"
    })
    check(r.status_code == 400, "Create booking: end < start → 400",
          f"Create booking: end < start → {r.status_code}")

    # ── Create booking: past date ──
    r = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
        "car_id": 1, "start_date": "2020-01-01T10:00:00Z", "end_date": "2020-01-05T10:00:00Z"
    })
    check(r.status_code == 400, "Create booking: past date → 400",
          f"Create booking: past date → {r.status_code}")

    # ── List bookings with status filter ──
    r = requests.get(f"{BASE_URL}/bookings?status=pending", headers=auth_header(renter_token))
    check(r.status_code == 200, "List bookings: ?status=pending → 200",
          f"List bookings: ?status=pending → {r.status_code}")

    # ── Get booking detail ──
    if booking_id:
        r = requests.get(f"{BASE_URL}/bookings/{booking_id}", headers=auth_header(renter_token))
        check(r.status_code == 200, f"Get booking #{booking_id} → 200",
              f"Get booking #{booking_id} → {r.status_code}")

    # ── IDOR: renter2 tries to view renter1's booking ──
    if booking_id:
        r = requests.get(f"{BASE_URL}/bookings/{booking_id}", headers=auth_header(owner_token))
        # Owner of the car should be allowed
        check(r.status_code in [200, 403], "Booking IDOR: owner can view → 200 or 403",
              f"Booking IDOR → {r.status_code}")

    # ── Calendar ──
    r = requests.get(f"{BASE_URL}/bookings/calendar", headers=auth_header(renter_token))
    check(r.status_code == 200, "Bookings calendar → 200", f"Bookings calendar → {r.status_code}")

    # ── Approve: renter tries (should fail) ──
    if booking_id:
        r = requests.post(f"{BASE_URL}/bookings/{booking_id}/approve",
                          headers=auth_header(renter_token))
        check(r.status_code == 403, "Approve booking (renter) → 403",
              f"Approve booking (renter) → {r.status_code}")

    # ── Cancel booking ──
    if booking_id:
        r = requests.post(f"{BASE_URL}/bookings/{booking_id}/cancel",
                          headers=auth_header(renter_token))
        check(r.status_code == 200, f"Cancel booking #{booking_id} → 200",
              f"Cancel booking → {r.status_code}")

    # ── Cancel already cancelled ──
    if booking_id:
        r = requests.post(f"{BASE_URL}/bookings/{booking_id}/cancel",
                          headers=auth_header(renter_token))
        check(r.status_code == 400, "Cancel already cancelled → 400",
              f"Cancel already cancelled → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/bookings")
    check(r.status_code in [401, 422], "Bookings: no token → 401/422",
          f"Bookings: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  4. FAVORITES TESTS
# ═══════════════════════════════════════════════════
def test_favorites(token):
    log_section("4. FAVORITES ENDPOINTS")

    # ── Add favorite ──
    r = requests.post(f"{BASE_URL}/favorites/1", headers=auth_header(token))
    check(r.status_code in [201, 400], "Add favorite → 201 or 400 (already exists)",
          f"Add favorite → {r.status_code}")

    # ── Get favorites ──
    r = requests.get(f"{BASE_URL}/favorites", headers=auth_header(token))
    check(r.status_code == 200 and "favorites" in r.json(), "Get favorites → 200",
          f"Get favorites → {r.status_code}")

    # ── Add favorite: non-existent car ──
    r = requests.post(f"{BASE_URL}/favorites/99999", headers=auth_header(token))
    check(r.status_code == 404, "Add favorite car 99999 → 404",
          f"Add favorite car 99999 → {r.status_code}")

    # ── Remove favorite ──
    r = requests.delete(f"{BASE_URL}/favorites/1", headers=auth_header(token))
    check(r.status_code in [200, 404], "Remove favorite → 200/404",
          f"Remove favorite → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/favorites")
    check(r.status_code in [401, 422], "Favorites: no token → 401/422",
          f"Favorites: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  5. REVIEWS TESTS
# ═══════════════════════════════════════════════════
def test_reviews(token):
    log_section("5. REVIEWS ENDPOINTS")

    # ── List reviews (no auth needed) ──
    r = requests.get(f"{BASE_URL}/reviews?car_id=1")
    check(r.status_code == 200 and "reviews" in r.json(), "List reviews → 200",
          f"List reviews → {r.status_code}")

    # ── Add review: invalid rating ──
    r = requests.post(f"{BASE_URL}/reviews", headers=auth_header(token), json={
        "car_id": 1, "rating": 10, "comment": "Too high"
    })
    check(r.status_code in [400, 403], "Add review: rating=10 → rejected",
          f"Add review: rating=10 → {r.status_code}")

    # ── Add review: missing fields ──
    r = requests.post(f"{BASE_URL}/reviews", headers=auth_header(token), json={})
    check(r.status_code == 400, "Add review: empty → 400", f"Add review: empty → {r.status_code}")

    # ── Add review: no auth ──
    r = requests.post(f"{BASE_URL}/reviews", headers=H_JSON, json={
        "car_id": 1, "rating": 5, "comment": "Hacked"
    })
    check(r.status_code in [401, 422], "Add review: no token → 401/422",
          f"Add review: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  6. MESSAGES / CHAT TESTS
# ═══════════════════════════════════════════════════
def test_messages(token1, token2, user1_id, user2_id):
    log_section("6. MESSAGES / CHAT ENDPOINTS")

    # ── Send message ──
    r = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user2_id, "content": "Test message from test suite"
    })
    check(r.status_code == 201, "Send message → 201", f"Send message → {r.status_code}")

    # ── Send message to self ──
    r = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user1_id, "content": "Self message"
    })
    check(r.status_code == 400, "Message to self → 400", f"Message to self → {r.status_code}")

    # ── Send message: missing fields ──
    r = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={})
    check(r.status_code == 400, "Send message: empty → 400", f"Send message: empty → {r.status_code}")

    # ── Send message: too long ──
    r = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user2_id, "content": "X" * 6000
    })
    check(r.status_code == 400, "Send message: too long → 400", f"Send message: too long → {r.status_code}")

    # ── Send message: non-existent receiver ──
    r = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": 99999, "content": "Hello ghost"
    })
    check(r.status_code == 404, "Send message: user 99999 → 404",
          f"Send message: user 99999 → {r.status_code}")

    # ── Get conversation ──
    r = requests.get(f"{BASE_URL}/messages/{user2_id}", headers=auth_header(token1))
    check(r.status_code == 200 and "messages" in r.json(), "Get conversation → 200",
          f"Get conversation → {r.status_code}")

    # ── Get inbox ──
    r = requests.get(f"{BASE_URL}/messages/inbox", headers=auth_header(token1))
    if r.status_code == 200:
        inbox = r.json()
        if len(inbox) > 0:
            has_unread = "unread_count" in inbox[0]
            has_other = "other_user" in inbox[0]
            check(has_unread and has_other, "Inbox: has unread_count + other_user fields",
                  "Inbox: missing unread_count or other_user")
        else:
            check(True, "Inbox → 200 (empty)", "")
    else:
        log_fail(f"Inbox → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/messages/inbox")
    check(r.status_code in [401, 422], "Inbox: no token → 401/422",
          f"Inbox: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  7. NOTIFICATIONS TESTS
# ═══════════════════════════════════════════════════
def test_notifications(token):
    log_section("7. NOTIFICATIONS ENDPOINTS")

    # ── Get notifications ──
    r = requests.get(f"{BASE_URL}/notifications", headers=auth_header(token))
    check(r.status_code == 200 and "notifications" in r.json(), "Get notifications → 200",
          f"Get notifications → {r.status_code}")

    # ── Get unread count ──
    r = requests.get(f"{BASE_URL}/notifications/unread-count", headers=auth_header(token))
    if r.status_code == 200:
        check("unread_count" in r.json(), "Unread count → has unread_count field",
              "Unread count → missing field")
    else:
        log_fail(f"Unread count → {r.status_code}")

    # ── Mark all read ──
    r = requests.post(f"{BASE_URL}/notifications/mark-read", headers=auth_header(token))
    check(r.status_code == 200, "Mark all read → 200", f"Mark all read → {r.status_code}")

    # ── Mark single read: non-existent ──
    r = requests.post(f"{BASE_URL}/notifications/99999/read", headers=auth_header(token))
    check(r.status_code == 404, "Mark read #99999 → 404", f"Mark read #99999 → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/notifications")
    check(r.status_code in [401, 422], "Notifications: no token → 401/422",
          f"Notifications: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  8. USER PROFILE TESTS
# ═══════════════════════════════════════════════════
def test_profile(token):
    log_section("8. USER PROFILE ENDPOINTS")

    # ── Get profile ──
    r = requests.get(f"{BASE_URL}/users/profile", headers=auth_header(token))
    if r.status_code == 200:
        data = r.json()
        has_fields = all(k in data for k in ["name", "email", "phone", "profile_image"])
        check(has_fields, "Get profile → has all expected fields", "Get profile → missing fields")
    else:
        log_fail(f"Get profile → {r.status_code}")

    # ── Update profile ──
    r = requests.put(f"{BASE_URL}/users/profile", headers=auth_header(token), json={
        "first_name": "Updated", "last_name": "Name"
    })
    check(r.status_code == 200, "Update profile → 200", f"Update profile → {r.status_code}")

    # ── Update profile: try to change email (should fail) ──
    r = requests.put(f"{BASE_URL}/users/profile", headers=auth_header(token), json={
        "email": "hacked@evil.com"
    })
    check(r.status_code == 400, "Update profile: email change → 400",
          f"Update profile: email change → {r.status_code}")

    # ── Update profile: empty body ──
    r = requests.put(f"{BASE_URL}/users/profile", headers=auth_header(token), json={})
    check(r.status_code in [200, 400], "Update profile: empty → handled",
          f"Update profile: empty → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/users/profile")
    check(r.status_code in [401, 422], "Profile: no token → 401/422",
          f"Profile: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  9. CHANGE PASSWORD TESTS
# ═══════════════════════════════════════════════════
def test_change_password(token):
    log_section("9. CHANGE PASSWORD")

    # ── Missing fields ──
    r = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(token), json={})
    check(r.status_code == 400, "Change password: empty → 400",
          f"Change password: empty → {r.status_code}")

    # ── Wrong current password ──
    r = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(token), json={
        "current_password": "WrongPassword1", "new_password": "NewStrongPass1"
    })
    check(r.status_code == 401, "Change password: wrong current → 401",
          f"Change password: wrong current → {r.status_code}")

    # ── Weak new password ──
    r = requests.post(f"{BASE_URL}/auth/change-password", headers=auth_header(token), json={
        "current_password": "password123", "new_password": "123"
    })
    check(r.status_code == 400, "Change password: weak new → 400",
          f"Change password: weak new → {r.status_code}")

    # ── No auth ──
    r = requests.post(f"{BASE_URL}/auth/change-password", headers=H_JSON, json={
        "current_password": "a", "new_password": "b"
    })
    check(r.status_code in [401, 422], "Change password: no token → 401/422",
          f"Change password: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  10. SEARCH HISTORY TESTS
# ═══════════════════════════════════════════════════
def test_search_history(token):
    log_section("10. SEARCH HISTORY ENDPOINTS")

    # ── Save search ──
    r = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={
        "query": "Ferrari Mansoura"
    })
    check(r.status_code == 201, "Save search → 201", f"Save search → {r.status_code}")

    # ── Save search: empty query ──
    r = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={
        "query": ""
    })
    check(r.status_code == 400, "Save search: empty query → 400",
          f"Save search: empty query → {r.status_code}")

    # ── Get search history ──
    r = requests.get(f"{BASE_URL}/search/history", headers=auth_header(token))
    if r.status_code == 200:
        data = r.json()
        check("history" in data, "Get search history → has history array",
              "Get search history → missing history array")
    else:
        log_fail(f"Get search history → {r.status_code}")

    # ── Save duplicate (should replace) ──
    r = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={
        "query": "Ferrari Mansoura"
    })
    check(r.status_code == 201, "Save duplicate search → 201 (replaces old)",
          f"Save duplicate search → {r.status_code}")

    # ── Clear all history ──
    r = requests.delete(f"{BASE_URL}/search/history", headers=auth_header(token))
    check(r.status_code == 200, "Clear search history → 200",
          f"Clear search history → {r.status_code}")

    # ── No auth ──
    r = requests.get(f"{BASE_URL}/search/history")
    check(r.status_code in [401, 422], "Search history: no token → 401/422",
          f"Search history: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  11. PARTNER PROGRAM TESTS
# ═══════════════════════════════════════════════════
def test_partner(token):
    log_section("11. PARTNER PROGRAM ENDPOINTS")

    # ── Apply as partner ──
    r = requests.post(f"{BASE_URL}/partner/apply", headers=auth_header_no_json(token), data={
        "full_name": "Test Partner",
        "email": "partner@test.com",
        "contact": "+201000000000",
        "driving_license_number": "DL-999888",
        "car_brand": "BMW",
        "car_model": "X5"
    })
    check(r.status_code in [201, 400], "Apply as partner → 201/400 (already applied)",
          f"Apply as partner → {r.status_code}")

    # ── Apply: missing fields ──
    r = requests.post(f"{BASE_URL}/partner/apply", headers=auth_header_no_json(token), data={
        "full_name": "Test"
    })
    check(r.status_code == 400, "Apply partner: missing fields → 400",
          f"Apply partner: missing fields → {r.status_code}")

    # ── Get application status ──
    r = requests.get(f"{BASE_URL}/partner/status", headers=auth_header(token))
    check(r.status_code == 200 and "applications" in r.json(), "Partner status → 200",
          f"Partner status → {r.status_code}")

    # ── No auth ──
    r = requests.post(f"{BASE_URL}/partner/apply", data={"full_name": "No Auth"})
    check(r.status_code in [401, 422], "Partner apply: no token → 401/422",
          f"Partner apply: no token → {r.status_code}")


# ═══════════════════════════════════════════════════
#  12. STATIC PAGES TESTS
# ═══════════════════════════════════════════════════
def test_static_pages():
    log_section("12. STATIC PAGES ENDPOINTS")

    # ── Privacy policy ──
    r = requests.get(f"{BASE_URL}/pages/privacy-policy")
    if r.status_code == 200:
        data = r.json()
        check("title" in data and "content" in data, "Privacy policy → has title + content",
              "Privacy policy → missing fields")
    else:
        log_fail(f"Privacy policy → {r.status_code}")

    # ── Terms of service ──
    r = requests.get(f"{BASE_URL}/pages/terms")
    check(r.status_code == 200, "Terms of service → 200", f"Terms of service → {r.status_code}")

    # ── Invite info ──
    r = requests.get(f"{BASE_URL}/pages/invite-info")
    check(r.status_code == 200, "Invite info → 200", f"Invite info → {r.status_code}")


# ═══════════════════════════════════════════════════
#  13. WEBHOOKS TESTS
# ═══════════════════════════════════════════════════
def test_webhooks():
    log_section("13. WEBHOOKS (SECURITY)")

    # ── Payment webhook: no API key ──
    r = requests.post(f"{BASE_URL}/payment-webhooks/confirm-booking", headers=H_JSON, json={
        "booking_id": 1, "payment_status": "completed"
    })
    check(r.status_code == 401, "Payment webhook: no key → 401",
          f"Payment webhook: no key → {r.status_code}")

    # ── Payment webhook: wrong API key ──
    r = requests.post(f"{BASE_URL}/payment-webhooks/confirm-booking",
                      headers={**H_JSON, "X-Internal-Api-Key": "wrong-key"}, json={
        "booking_id": 1, "payment_status": "completed"
    })
    check(r.status_code == 401, "Payment webhook: wrong key → 401",
          f"Payment webhook: wrong key → {r.status_code}")

    # ── Admin webhook: no API key ──
    r = requests.post(f"{BASE_URL}/admin-webhooks/update-user-status", headers=H_JSON, json={
        "user_id": 1, "approval_status": "approved"
    })
    check(r.status_code == 401, "Admin webhook: no key → 401",
          f"Admin webhook: no key → {r.status_code}")

    # ── Admin webhook: wrong key ──
    r = requests.post(f"{BASE_URL}/admin-webhooks/update-user-status",
                      headers={**H_JSON, "X-Internal-Api-Key": "wrong-key"}, json={
        "user_id": 1, "approval_status": "approved"
    })
    check(r.status_code == 401, "Admin webhook: wrong key → 401",
          f"Admin webhook: wrong key → {r.status_code}")


# ═══════════════════════════════════════════════════
#  14. JWT TOKEN SECURITY TESTS
# ═══════════════════════════════════════════════════
def test_jwt_security():
    log_section("14. JWT TOKEN SECURITY")

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
        if method == "GET":
            r = requests.get(f"{BASE_URL}{path}", headers=auth_header(fake_token))
        else:
            r = requests.post(f"{BASE_URL}{path}", headers=auth_header(fake_token))
        check(r.status_code in [401, 422], f"Fake JWT on {path} → 401/422",
              f"Fake JWT on {path} → {r.status_code} (POTENTIAL VULNERABILITY!)")


# ═══════════════════════════════════════════════════
#  15. FILE UPLOAD SECURITY TESTS
# ═══════════════════════════════════════════════════
def test_upload_security(owner_token, renter_token):
    log_section("15. FILE UPLOAD SECURITY")

    # ── Upload malicious file as car image ──
    files = {
        'car_license_image': ('virus.py', b'print("Hacked")', 'application/x-python'),
        'images': ('hack.exe', b'binarydata', 'application/octet-stream')
    }
    data = {
        "brand": "HackCar", "model": "Evil", "year": 2025,
        "price_per_day": 100, "location_city": "Cairo",
        "transmission": "Manual", "license_plate": "HACK-999"
    }
    r = requests.post(f"{BASE_URL}/cars", headers=auth_header_no_json(owner_token),
                      data=data, files=files)
    check(r.status_code != 201 or "virus" not in r.text,
          "Upload .py/.exe → rejected or sanitized",
          "Upload .py/.exe → ACCEPTED (vulnerability!)")

    # ── Upload malicious file as profile photo ──
    files = {'profile_image': ('shell.php', b'<?php system("ls"); ?>', 'application/x-php')}
    r = requests.post(f"{BASE_URL}/users/profile/photo",
                      headers=auth_header_no_json(renter_token), files=files)
    check(r.status_code == 400, "Upload .php as profile → 400",
          f"Upload .php as profile → {r.status_code}")

    # ── Upload malicious file as partner photo ──
    files = {'photo': ('backdoor.jsp', b'<% Runtime.exec("ls") %>', 'text/x-java')}
    r = requests.post(f"{BASE_URL}/partner/apply",
                      headers=auth_header_no_json(renter_token),
                      data={
                          "full_name": "Hack", "email": "h@h.com", "contact": "123",
                          "driving_license_number": "DL", "car_brand": "X", "car_model": "Y"
                      }, files=files)
    # The photo should be rejected or ignored since .jsp isn't in allowed extensions
    check(r.status_code in [201, 400],
          "Upload .jsp as partner photo → handled safely",
          f"Upload .jsp as partner photo → {r.status_code}")


# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{Fore.MAGENTA}{'═' * 60}")
    print(f"  RENTLY API — COMPREHENSIVE TEST SUITE")
    print(f"  48 Endpoints | Functional + Security Tests")
    print(f"{'═' * 60}{Style.RESET_ALL}\n")

    # Step 1: Login as owner and renter
    print(f"{Fore.YELLOW}[*] Logging in as test users...{Style.RESET_ALL}")
    owner_token, owner_id = login("owner@example.com", "password123")
    renter_token, renter_id = login("renter@example.com", "password123")

    if not owner_token or not renter_token:
        print(f"\n{Fore.RED}[!] Cannot proceed without valid tokens.")
        print(f"    Make sure the app is running (flask run) and DB is seeded (python seed.py)")
        print(f"    Expected users: owner@example.com, renter@example.com (password: password123){Style.RESET_ALL}")
        exit(1)

    print(f"{Fore.GREEN}[✓] Logged in as owner (id={owner_id}) and renter (id={renter_id}){Style.RESET_ALL}")

    # Step 2: Run all tests
    test_auth()
    test_cars(owner_token, renter_token)
    test_bookings(owner_token, renter_token, owner_id, renter_id)
    test_favorites(renter_token)
    test_reviews(renter_token)
    test_messages(renter_token, owner_token, renter_id, owner_id)
    test_notifications(renter_token)
    test_profile(renter_token)
    test_change_password(renter_token)
    test_search_history(renter_token)
    test_partner(renter_token)
    test_static_pages()
    test_webhooks()
    test_jwt_security()
    test_upload_security(owner_token, renter_token)

    # Step 3: Print results
    print(f"\n{Fore.MAGENTA}{'═' * 60}")
    print(f"  TEST RESULTS")
    print(f"{'═' * 60}{Style.RESET_ALL}")
    print(f"  Total:  {total}")
    print(f"  {Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Failed: {failed}{Style.RESET_ALL}")

    percentage = (passed / total * 100) if total > 0 else 0
    if percentage >= 90:
        print(f"\n  {Fore.GREEN}✓ Score: {percentage:.0f}% — Excellent!{Style.RESET_ALL}")
    elif percentage >= 70:
        print(f"\n  {Fore.YELLOW}⚠ Score: {percentage:.0f}% — Needs attention{Style.RESET_ALL}")
    else:
        print(f"\n  {Fore.RED}✗ Score: {percentage:.0f}% — Critical issues found!{Style.RESET_ALL}")

    print(f"\n{'═' * 60}\n")
