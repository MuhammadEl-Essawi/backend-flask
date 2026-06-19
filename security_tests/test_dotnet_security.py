"""
Rently .NET Backend — Advanced ESSAWWI Security Tests
==============================================
Tests the .NET Admin/Payment backend for vulnerabilities.
Requires: pip install requests
Usage:   python test_dotnet_security.py --base-url https://your-ngrok-url.app

Test Categories:
  1. Authentication & JWT
  2. Authorization & Access Control
  3. Payment Security
  4. XSS & Injection
  5. IDOR (Insecure Direct Object Reference)
  6. Rate Limiting & Brute Force
  7. Webhook HMAC Security
  8. Account Takeover
  9. Input Validation
  10. Business Logic Abuse
"""

import requests
import json
import time
import hmac
import hashlib
import sys
import argparse
import urllib.parse
from datetime import datetime

# ──────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:5001"

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

class TestReport:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def log(self, category, test_name, status, detail=""):
        icon = {"PASS": f"{Colors.GREEN}✅", "FAIL": f"{Colors.RED}❌", "WARN": f"{Colors.YELLOW}⚠️"}
        color_end = Colors.END
        self.results.append((category, test_name, status, detail))
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1
        print(f"  {icon.get(status, '?')} {test_name}{color_end}: {detail}")

    def summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{'='*60}")
        print(f"{Colors.BOLD}SECURITY TEST SUMMARY{Colors.END}")
        print(f"{'='*60}")
        print(f"  {Colors.GREEN}Passed:   {self.passed}{Colors.END}")
        print(f"  {Colors.RED}Failed:   {self.failed}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {self.warnings}{Colors.END}")
        print(f"  Total:    {total}")
        print(f"{'='*60}")
        if self.failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  {self.failed} SECURITY VULNERABILITIES FOUND!{Colors.END}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All security checks passed!{Colors.END}")

report = TestReport()


# ──────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────
def api(method, path, **kwargs):
    """Make an API request and return response"""
    url = f"{BASE_URL}{path}"
    try:
        r = getattr(requests, method)(url, timeout=10, **kwargs)
        return r
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        return None

def get_admin_token(email="admin@rently.com", password="Admin123!"):
    """Try to get admin JWT token"""
    r = api("post", "/api/auth/login", json={"email": email, "password": password})
    if r and r.status_code == 200:
        data = r.json()
        return data.get("token")
    return None

def auth_header(token):
    """Return authorization header"""
    return {"Authorization": f"Bearer {token}"}


# ══════════════════════════════════════════════════════════════════
# 1. AUTHENTICATION & JWT SECURITY
# ══════════════════════════════════════════════════════════════════
def test_auth_security():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[1] AUTHENTICATION & JWT SECURITY{Colors.END}")

    # 1.1 Empty credentials
    r = api("post", "/api/auth/login", json={"email": "", "password": ""})
    if r:
        report.log("AUTH", "Empty credentials rejected",
                   "PASS" if r.status_code in [400, 401] else "FAIL",
                   f"Status: {r.status_code}")

    # 1.2 SQL injection in login
    r = api("post", "/api/auth/login", json={"email": "' OR 1=1 --", "password": "test"})
    if r:
        report.log("AUTH", "SQL injection in email",
                   "PASS" if r.status_code in [400, 401] else "FAIL",
                   f"Status: {r.status_code}")

    # 1.3 Non-admin user login rejected
    r = api("post", "/api/auth/login", json={"email": "renter@test.com", "password": "Test123!"})
    if r:
        report.log("AUTH", "Non-admin login rejected",
                   "PASS" if r.status_code in [401] else "WARN",
                   f"Status: {r.status_code}")

    # 1.4 Invalid JWT token
    r = api("get", "/api/user", headers={"Authorization": "Bearer invalid.jwt.token"})
    if r:
        report.log("AUTH", "Invalid JWT rejected",
                   "PASS" if r.status_code in [401] else "FAIL",
                   f"Status: {r.status_code}")

    # 1.5 Expired JWT (manually crafted)
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid"
    r = api("get", "/api/user", headers={"Authorization": f"Bearer {expired_token}"})
    if r:
        report.log("AUTH", "Expired JWT rejected",
                   "PASS" if r.status_code in [401] else "FAIL",
                   f"Status: {r.status_code}")

    # 1.6 None algorithm attack
    none_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwicm9sZSI6IkFkbWluIn0."
    r = api("get", "/api/user", headers={"Authorization": f"Bearer {none_token}"})
    if r:
        report.log("AUTH", "JWT 'none' algorithm rejected",
                   "PASS" if r.status_code in [401] else "FAIL",
                   f"Status: {r.status_code}")

    # 1.7 Login returns token without sensitive data
    r = api("post", "/api/auth/login", json={"email": "admin@rently.com", "password": "Admin123!"})
    if r and r.status_code == 200:
        body = r.json()
        has_password = "password" in json.dumps(body).lower()
        report.log("AUTH", "Token response has no password",
                   "PASS" if not has_password else "FAIL",
                   f"Password in response: {has_password}")

    # 1.8 Missing Authorization header
    r = api("get", "/api/user")
    if r:
        report.log("AUTH", "No auth header → 401",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# 2. AUTHORIZATION & ACCESS CONTROL
# ══════════════════════════════════════════════════════════════════
def test_authorization():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[2] AUTHORIZATION & ACCESS CONTROL{Colors.END}")

    # 2.1 Payment statistics without auth
    r = api("get", "/api/payment/statistics")
    if r:
        report.log("AUTHZ", "Payment statistics needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.2 Transactions without auth
    r = api("get", "/api/payment/transactions")
    if r:
        report.log("AUTHZ", "Transactions needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.3 Refunds without auth
    r = api("get", "/api/payment/refunds")
    if r:
        report.log("AUTHZ", "Refunds needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.4 Create payment without auth
    r = api("post", "/api/payment", json={"bookingId": 1, "amount": 100, "currency": "EGP", "status": "Succeeded"})
    if r:
        report.log("AUTHZ", "Create payment needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.5 Process refund without auth
    r = api("post", "/api/payment/process-refund", json={"paymentId": 1, "amount": 100, "reason": "test"})
    if r:
        report.log("AUTHZ", "Process refund needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.6 Mass refund without auth
    r = api("post", "/api/payment/refund-all", json=[1, 2, 3])
    if r:
        report.log("AUTHZ", "Mass refund needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.7 User CRUD without auth
    r = api("get", "/api/user")
    if r:
        report.log("AUTHZ", "User list needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.8 Car delete without auth
    r = api("delete", "/api/car/1")
    if r:
        report.log("AUTHZ", "Car delete needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.9 Dashboard without auth
    r = api("get", "/api/dashboard/stats")
    if r:
        report.log("AUTHZ", "Dashboard needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.10 Add admin without auth
    r = api("post", "/api/account/add-admin", json={"email": "hack@test.com", "password": "123"})
    if r:
        report.log("AUTHZ", "Add admin needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.11 Request admin OTP without auth
    r = api("post", "/api/account/request-admin-otp", json={"email": "hack@test.com"})
    if r:
        report.log("AUTHZ", "Request admin OTP needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")

    # 2.12 Booking list without auth
    r = api("get", "/api/booking")
    if r:
        report.log("AUTHZ", "Booking list needs auth",
                   "PASS" if r.status_code == 401 else "FAIL",
                   f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# 3. PAYMENT SECURITY
# ══════════════════════════════════════════════════════════════════
def test_payment_security():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[3] PAYMENT SECURITY{Colors.END}")

    # 3.1 Paymob callback without HMAC
    r = api("get", "/api/payment/paymob/callback?success=true&order=12345")
    if r:
        report.log("PAYMENT", "Callback without HMAC rejected",
                   "PASS" if r.status_code == 400 else "FAIL",
                   f"Status: {r.status_code}")

    # 3.2 Paymob callback with fake HMAC
    r = api("get", "/api/payment/paymob/callback?success=true&order=12345&hmac=fakehmacsignature")
    if r:
        report.log("PAYMENT", "Callback with fake HMAC rejected",
                   "PASS" if r.status_code == 400 else "FAIL",
                   f"Status: {r.status_code}")

    # 3.3 Paymob webhook without HMAC
    payload = {"obj": {"success": True, "order": {"id": "12345"}, "amount_cents": 50000}}
    r = api("post", "/api/payment/paymob/webhook", json=payload)
    if r:
        report.log("PAYMENT", "Webhook without HMAC rejected",
                   "PASS" if r.status_code == 400 else "FAIL",
                   f"Status: {r.status_code}")

    # 3.4 Webhook with tampered HMAC
    r = api("post", "/api/payment/paymob/webhook?hmac=tampered123", json=payload)
    if r:
        report.log("PAYMENT", "Webhook with tampered HMAC rejected",
                   "PASS" if r.status_code == 400 else "FAIL",
                   f"Status: {r.status_code}")

    # 3.5 Negative amount in payment creation (needs auth)
    token = get_admin_token()
    if token:
        r = api("post", "/api/payment",
                json={"bookingId": 1, "amount": -500, "currency": "EGP", "status": "Succeeded"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "Negative amount rejected",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code}")

        # 3.6 Zero amount
        r = api("post", "/api/payment",
                json={"bookingId": 1, "amount": 0, "currency": "EGP", "status": "Succeeded"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "Zero amount rejected",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code}")

        # 3.7 Huge amount (overflow attempt)
        r = api("post", "/api/payment",
                json={"bookingId": 1, "amount": 99999999999999, "currency": "EGP", "status": "Succeeded"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "Huge amount handled safely",
                       "PASS" if r.status_code in [400, 422, 201] else "WARN",
                       f"Status: {r.status_code}")

        # 3.8 Invalid currency
        r = api("post", "/api/payment",
                json={"bookingId": 1, "amount": 100, "currency": "<script>alert(1)</script>", "status": "Succeeded"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "XSS in currency field",
                       "PASS" if r.status_code in [400, 422] or "<script>" not in (r.text or "") else "FAIL",
                       f"Status: {r.status_code}")

        # 3.9 Payment status manipulation
        r = api("put", f"/api/payment/1",
                json={"status": "Succeeded"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "Direct status manipulation",
                       "WARN" if r.status_code in [204, 200] else "PASS",
                       f"Status: {r.status_code} — should require role check")

        # 3.10 Refund more than original amount
        r = api("post", "/api/payment/process-refund",
                json={"paymentId": 1, "amount": 999999, "reason": "test"},
                headers=auth_header(token))
        if r:
            report.log("PAYMENT", "Refund exceeds original amount",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code} — should validate refund <= original")
    else:
        report.log("PAYMENT", "Auth payment tests", "WARN", "Could not get admin token")


# ══════════════════════════════════════════════════════════════════
# 4. XSS & INJECTION
# ══════════════════════════════════════════════════════════════════
def test_xss_injection():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[4] XSS & INJECTION{Colors.END}")

    # 4.1 Test iframe endpoint (CRITICAL)
    r = api("get", "/api/payment/test/iframe?url=javascript:alert(document.cookie)")
    if r:
        has_js = "javascript:" in (r.text or "")
        report.log("XSS", "Test iframe: javascript: URL blocked",
                   "FAIL" if has_js else "PASS",
                   f"Status: {r.status_code}, JS in response: {has_js}")

    # 4.2 Iframe with data: URI
    r = api("get", "/api/payment/test/iframe?url=data:text/html,<script>alert(1)</script>")
    if r:
        has_data = "data:text/html" in (r.text or "")
        report.log("XSS", "Test iframe: data: URI blocked",
                   "FAIL" if has_data else "PASS",
                   f"Status: {r.status_code}")

    # 4.3 Iframe with XSS breakout
    r = api("get", '/api/payment/test/iframe?url="><img src=x onerror=alert(1)>')
    if r:
        has_xss = "onerror" in (r.text or "")
        report.log("XSS", "Test iframe: HTML breakout blocked",
                   "FAIL" if has_xss else "PASS",
                   f"Status: {r.status_code}")

    # 4.4 Iframe endpoint is AllowAnonymous
    r = api("get", "/api/payment/test/iframe?url=https://example.com")
    if r:
        report.log("XSS", "Test iframe available without auth",
                   "FAIL" if r.status_code == 200 else "PASS",
                   f"Status: {r.status_code} — should require auth or be removed")

    # 4.5 XSS in user name fields
    token = get_admin_token()
    if token:
        r = api("post", "/api/account/change-name",
                json={"firstName": "<script>alert('xss')</script>", "lastName": "Test"},
                headers=auth_header(token))
        if r and r.status_code in [200, 204]:
            report.log("XSS", "XSS in firstName field",
                       "WARN", "Stored XSS possible — no input sanitization")

    # 4.6 SQL injection in search parameters
    r = api("get", "/api/user?search=' OR 1=1 --", headers=auth_header(token) if token else {})
    if r:
        report.log("INJECTION", "SQL injection in user search",
                   "PASS" if r.status_code in [200, 401] else "FAIL",
                   f"Status: {r.status_code}")

    # 4.7 Path traversal in car image
    if token:
        r = api("post", "/api/car",
                json={"ownerId": 1, "brand": "Test", "model": "Test", "year": 2024,
                      "pricePerDay": 100, "carLicenseImage": "../../../etc/passwd"},
                headers=auth_header(token))
        if r:
            report.log("INJECTION", "Path traversal in car image",
                       "PASS" if r.status_code in [400, 201] else "WARN",
                       f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# 5. IDOR (Insecure Direct Object Reference)
# ══════════════════════════════════════════════════════════════════
def test_idor():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[5] IDOR (Insecure Direct Object Reference){Colors.END}")

    token = get_admin_token()
    if not token:
        report.log("IDOR", "IDOR tests", "WARN", "Could not get admin token — skipping")
        return

    # 5.1 Access other user's data by ID
    for user_id in [1, 2, 3, 999]:
        r = api("get", f"/api/user/{user_id}?includeContact=true", headers=auth_header(token))
        if r and r.status_code == 200:
            data = r.json()
            has_email = bool(data.get("email"))
            report.log("IDOR", f"User {user_id} data with includeContact",
                       "WARN" if has_email else "PASS",
                       f"Email exposed: {has_email}")
            break

    # 5.2 View payment details by ID enumeration
    for pid in range(1, 5):
        r = api("get", f"/api/payment/{pid}", headers=auth_header(token))
        if r and r.status_code == 200:
            report.log("IDOR", f"Payment {pid} details accessible",
                       "WARN", "No ownership check — any admin can see all payments")
            break

    # 5.3 Delete any user by ID
    r = api("delete", "/api/user/99999", headers=auth_header(token))
    if r:
        report.log("IDOR", "User delete by arbitrary ID",
                   "WARN" if r.status_code in [204, 404] else "PASS",
                   f"Status: {r.status_code} — should require Super Admin role check")

    # 5.4 Modify any booking
    r = api("get", "/api/booking/1", headers=auth_header(token))
    if r and r.status_code == 200:
        report.log("IDOR", "Booking details accessible by ID",
                   "WARN", "No ownership validation")


# ══════════════════════════════════════════════════════════════════
# 6. RATE LIMITING & BRUTE FORCE
# ══════════════════════════════════════════════════════════════════
def test_rate_limiting():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[6] RATE LIMITING & BRUTE FORCE{Colors.END}")

    # 6.1 Login brute force
    blocked = False
    for i in range(20):
        r = api("post", "/api/auth/login", json={"email": "admin@rently.com", "password": f"wrong{i}"})
        if r and r.status_code == 429:
            blocked = True
            break
    report.log("RATE", "Login rate limiting",
               "PASS" if blocked else "FAIL",
               f"Blocked after {i+1} attempts" if blocked else "20 attempts with no rate limit")

    # 6.2 Password reset brute force
    blocked = False
    for i in range(15):
        r = api("post", "/api/account/request-reset", json={"email": "test@test.com"})
        if r and r.status_code == 429:
            blocked = True
            break
    report.log("RATE", "Password reset rate limiting",
               "PASS" if blocked else "FAIL",
               f"Blocked after {i+1} attempts" if blocked else "15 requests with no rate limit")

    # 6.3 OTP brute force — try all 6 digit codes would be 1M but let's test rapid fire
    blocked = False
    for i in range(20):
        r = api("post", "/api/account/reset-password",
                json={"email": "admin@rently.com", "token": f"{100000+i}", "newPassword": "Hacked123!"})
        if r and r.status_code == 429:
            blocked = True
            break
    report.log("RATE", "OTP verification rate limiting",
               "PASS" if blocked else "FAIL",
               f"Blocked after {i+1} attempts" if blocked else "20 OTP attempts with no rate limit")


# ══════════════════════════════════════════════════════════════════
# 7. WEBHOOK SECURITY
# ══════════════════════════════════════════════════════════════════
def test_webhook_security():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[7] WEBHOOK SECURITY{Colors.END}")

    # 7.1 Paymob callback — replay check
    r1 = api("get", "/api/payment/paymob/callback?success=true&order=12345&hmac=test")
    r2 = api("get", "/api/payment/paymob/callback?success=true&order=12345&hmac=test")
    if r1 and r2:
        report.log("WEBHOOK", "Paymob callback replay protection",
                   "WARN" if r1.status_code == r2.status_code else "PASS",
                   "No idempotency check — same request processed multiple times")

    # 7.2 Webhook with empty body
    r = api("post", "/api/payment/paymob/webhook", data="", headers={"Content-Type": "application/json"})
    if r:
        report.log("WEBHOOK", "Empty webhook body handled",
                   "PASS" if r.status_code in [400, 500] else "WARN",
                   f"Status: {r.status_code}")

    # 7.3 Webhook with malformed JSON
    r = api("post", "/api/payment/paymob/webhook", data="{invalid json",
            headers={"Content-Type": "application/json"})
    if r:
        report.log("WEBHOOK", "Malformed JSON webhook handled",
                   "PASS" if r.status_code in [400, 500] else "WARN",
                   f"Status: {r.status_code}")

    # 7.4 Very large webhook payload
    large_payload = {"obj": {"data": "x" * 1000000}}
    r = api("post", "/api/payment/paymob/webhook", json=large_payload)
    if r:
        report.log("WEBHOOK", "Large payload handled",
                   "PASS" if r.status_code in [400, 413, 500] else "WARN",
                   f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# 8. ACCOUNT TAKEOVER
# ══════════════════════════════════════════════════════════════════
def test_account_takeover():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[8] ACCOUNT TAKEOVER{Colors.END}")

    # 8.1 Debug token leakage in password reset
    r = api("post", "/api/account/request-reset?debug=true",
            json={"email": "admin@rently.com"})
    if r and r.status_code == 200:
        body = r.json()
        has_token = "dev_token" in body or "token" in body
        report.log("ACCT", "Debug OTP leakage (debug=true)",
                   "FAIL" if has_token else "PASS",
                   f"OTP exposed in response: {has_token}")

    # 8.2 Password reset for non-existent user — timing leak
    t1 = time.time()
    r1 = api("post", "/api/account/request-reset", json={"email": "exists@test.com"})
    t1 = time.time() - t1

    t2 = time.time()
    r2 = api("post", "/api/account/request-reset", json={"email": "nonexistent@test.com"})
    t2 = time.time() - t2

    if r1 and r2:
        diff = abs(t1 - t2)
        report.log("ACCT", "User enumeration via timing",
                   "PASS" if diff < 0.5 else "WARN",
                   f"Time diff: {diff:.3f}s (>0.5s may leak user existence)")

    # 8.3 Password reset without expiry check
    r = api("post", "/api/account/reset-password",
            json={"email": "admin@rently.com", "token": "000000", "newPassword": "Hacked!"})
    if r:
        report.log("ACCT", "Invalid OTP rejected for reset",
                   "PASS" if r.status_code in [401, 400] else "FAIL",
                   f"Status: {r.status_code}")

    # 8.4 Change password without current password
    token = get_admin_token()
    if token:
        r = api("post", "/api/account/change-password",
                json={"currentPassword": "", "newPassword": "NewPass123!"},
                headers=auth_header(token))
        if r:
            report.log("ACCT", "Password change needs current password",
                       "PASS" if r.status_code in [400, 401] else "FAIL",
                       f"Status: {r.status_code}")

    # 8.5 Change password with wrong current password
    if token:
        r = api("post", "/api/account/change-password",
                json={"currentPassword": "WrongPassword!", "newPassword": "NewPass123!"},
                headers=auth_header(token))
        if r:
            report.log("ACCT", "Wrong current password rejected",
                       "PASS" if r.status_code in [401] else "FAIL",
                       f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# 9. INPUT VALIDATION
# ══════════════════════════════════════════════════════════════════
def test_input_validation():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[9] INPUT VALIDATION{Colors.END}")

    token = get_admin_token()

    # 9.1 Invalid email format in user creation
    if token:
        r = api("post", "/api/user",
                json={"firstName": "Test", "lastName": "User", "email": "not-an-email",
                      "phone": "1234567890", "role": "Renter"},
                headers=auth_header(token))
        if r:
            report.log("INPUT", "Invalid email format rejected",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code}")

    # 9.2 Missing required fields
    if token:
        r = api("post", "/api/user", json={}, headers=auth_header(token))
        if r:
            report.log("INPUT", "Empty user creation rejected",
                       "PASS" if r.status_code in [400, 422] else "FAIL",
                       f"Status: {r.status_code}")

    # 9.3 Negative car year
    if token:
        r = api("post", "/api/car",
                json={"ownerId": 1, "brand": "Test", "model": "Test", "year": -1,
                      "pricePerDay": 100},
                headers=auth_header(token))
        if r:
            report.log("INPUT", "Negative car year handled",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code}")

    # 9.4 Extremely long string fields
    if token:
        long_str = "A" * 10000
        r = api("post", "/api/user",
                json={"firstName": long_str, "lastName": "Test", "email": "test@long.com",
                      "phone": "123", "role": "Renter"},
                headers=auth_header(token))
        if r:
            report.log("INPUT", "Long string (10K chars) handled",
                       "PASS" if r.status_code in [400, 422, 500] else "WARN",
                       f"Status: {r.status_code}")

    # 9.5 Pagination - negative page
    if token:
        r = api("get", "/api/user?page=-1&pageSize=10", headers=auth_header(token))
        if r:
            report.log("INPUT", "Negative page number handled",
                       "PASS" if r.status_code in [200, 400] else "WARN",
                       f"Status: {r.status_code}")

    # 9.6 Pagination - huge page size (DoS vector)
    if token:
        r = api("get", "/api/user?page=1&pageSize=999999", headers=auth_header(token))
        if r:
            report.log("INPUT", "Huge pageSize (999999) capped",
                       "PASS" if r.status_code in [400] else "WARN",
                       f"Status: {r.status_code} — may return all records (DoS)")

    # 9.7 Invalid role assignment
    if token:
        r = api("post", "/api/user",
                json={"firstName": "Hacker", "lastName": "Admin", "email": "hack@test.com",
                      "phone": "0000000", "role": "Admin"},
                headers=auth_header(token))
        if r:
            report.log("INPUT", "Admin role assignment via user create",
                       "WARN" if r.status_code in [201, 200] else "PASS",
                       f"Status: {r.status_code} — should not allow Admin role via regular create")


# ══════════════════════════════════════════════════════════════════
# 10. BUSINESS LOGIC ABUSE
# ══════════════════════════════════════════════════════════════════
def test_business_logic():
    print(f"\n{Colors.CYAN}{Colors.BOLD}[10] BUSINESS LOGIC ABUSE{Colors.END}")

    token = get_admin_token()

    # 10.1 Double refund
    if token:
        r1 = api("post", "/api/payment/process-refund",
                 json={"paymentId": 1, "amount": 100, "reason": "first refund"},
                 headers=auth_header(token))
        r2 = api("post", "/api/payment/process-refund",
                 json={"paymentId": 1, "amount": 100, "reason": "second refund"},
                 headers=auth_header(token))
        if r1 and r2:
            both_ok = r1.status_code in [200] and r2.status_code in [200]
            report.log("LOGIC", "Double refund prevention",
                       "WARN" if both_ok else "PASS",
                       f"R1: {r1.status_code}, R2: {r2.status_code} — duplicate refund possible")

    # 10.2 Refund on non-existent payment
    if token:
        r = api("post", "/api/payment/process-refund",
                json={"paymentId": 99999, "amount": 100, "reason": "test"},
                headers=auth_header(token))
        if r:
            report.log("LOGIC", "Refund on non-existent payment",
                       "PASS" if r.status_code == 404 else "FAIL",
                       f"Status: {r.status_code}")

    # 10.3 Process payout with no implementation
    if token:
        r = api("post", "/api/payment/process-payout",
                json={"ownerId": 1, "amount": 9999},
                headers=auth_header(token))
        if r:
            report.log("LOGIC", "Payout endpoint is stub",
                       "WARN" if r.status_code == 200 else "PASS",
                       f"Status: {r.status_code} — returns OK without doing anything")

    # 10.4 Update payment to invalid status
    if token:
        r = api("put", "/api/payment/1",
                json={"status": "HACKED"},
                headers=auth_header(token))
        if r:
            report.log("LOGIC", "Invalid payment status accepted",
                       "PASS" if r.status_code in [400, 422] else "WARN",
                       f"Status: {r.status_code} — no status enum validation")

    # 10.5 Update booking status directly
    if token:
        r = api("patch", "/api/booking/1/status",
                json={"status": "Completed"},
                headers=auth_header(token))
        if r:
            report.log("LOGIC", "Direct booking status change",
                       "WARN" if r.status_code in [200, 204] else "PASS",
                       f"Status: {r.status_code} — no state machine validation")

    # 10.6 Mass refund with empty list
    if token:
        r = api("post", "/api/payment/refund-all", json=[], headers=auth_header(token))
        if r:
            report.log("LOGIC", "Mass refund with empty list",
                       "PASS" if r.status_code in [200, 400] else "WARN",
                       f"Status: {r.status_code}")


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rently .NET Security Tests")
    parser.add_argument("--base-url", default="http://localhost:5001", help="Base URL of .NET backend")
    args = parser.parse_args()
    BASE_URL = args.base_url.rstrip("/")

    print(f"{Colors.BOLD}{'='*60}")
    print(f"  🔒 RENTLY .NET BACKEND — SECURITY TESTS")
    print(f"  Target: {BASE_URL}")
    print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}")

    # Check connectivity
    try:
        r = requests.get(f"{BASE_URL}/api/auth/login", timeout=5)
    except:
        r = None
    if r is None:
        print(f"\n{Colors.RED}Cannot connect to {BASE_URL}")
        print(f"Make sure the .NET backend is running!{Colors.END}")
        sys.exit(1)

    # Run all tests
    test_auth_security()
    test_authorization()
    test_payment_security()
    test_xss_injection()
    test_idor()
    test_rate_limiting()
    test_webhook_security()
    test_account_takeover()
    test_input_validation()
    test_business_logic()

    # Print summary
    report.summary()
