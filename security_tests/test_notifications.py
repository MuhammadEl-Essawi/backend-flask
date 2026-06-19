"""
Test: Notifications Endpoints
==============================
Covers: list, unread count, mark all read, mark single read
"""
from helpers import *


def run(token):
    print_section("NOTIFICATIONS ENDPOINTS")
    r = TestReport("Notifications")

    # ── Get notifications ──
    res = requests.get(f"{BASE_URL}/notifications", headers=auth_header(token))
    r.check(res.status_code == 200 and "notifications" in res.json(), "Get notifications → 200",
            f"Get notifications → {res.status_code}")

    # ── Get unread count ──
    res = requests.get(f"{BASE_URL}/notifications/unread-count", headers=auth_header(token))
    if res.status_code == 200:
        r.check("unread_count" in res.json(), "Unread count → has unread_count field",
                "Unread count → missing field")
    else:
        r.log_fail(f"Unread count → {res.status_code}")

    # ── Mark all read ──
    res = requests.post(f"{BASE_URL}/notifications/mark-read", headers=auth_header(token))
    r.check(res.status_code == 200, "Mark all read → 200", f"Mark all read → {res.status_code}")

    # ── Mark single read: non-existent ──
    res = requests.post(f"{BASE_URL}/notifications/99999/read", headers=auth_header(token))
    r.check(res.status_code == 404, "Mark read #99999 → 404", f"Mark read #99999 → {res.status_code}")

    # ── No auth ──
    res = requests.get(f"{BASE_URL}/notifications")
    r.check(res.status_code in [401, 422], "Notifications: no token → 401/422",
            f"Notifications: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    t, _ = login("renter@example.com", "password123")
    if t:
        run(t)
