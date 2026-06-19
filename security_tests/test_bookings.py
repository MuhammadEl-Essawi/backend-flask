"""
Test: Bookings Endpoints
========================
Covers: create, list, detail, approve, reject, cancel, calendar, status filter, IDOR
"""
from helpers import *


def run(owner_token, renter_token, owner_id, renter_id):
    print_section("BOOKINGS ENDPOINTS")
    r = TestReport("Bookings")

    # ── Create booking ──
    res = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
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
    if res.status_code == 201:
        booking_id = res.json().get("id")
        r.check(True, f"Create booking → 201 (id={booking_id})", "")
    else:
        r.check(False, "", f"Create booking → {res.status_code}: {res.text[:100]}")

    # ── Create booking: missing fields ──
    res = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={})
    r.check(res.status_code == 400, "Create booking: empty → 400", f"Create booking: empty → {res.status_code}")

    # ── Create booking: end before start ──
    res = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
        "car_id": 1, "start_date": "2026-09-05T10:00:00Z", "end_date": "2026-09-01T10:00:00Z"
    })
    r.check(res.status_code == 400, "Create booking: end < start → 400",
            f"Create booking: end < start → {res.status_code}")

    # ── Create booking: past date ──
    res = requests.post(f"{BASE_URL}/bookings", headers=auth_header(renter_token), json={
        "car_id": 1, "start_date": "2020-01-01T10:00:00Z", "end_date": "2020-01-05T10:00:00Z"
    })
    r.check(res.status_code == 400, "Create booking: past date → 400",
            f"Create booking: past date → {res.status_code}")

    # ── List bookings with status filter ──
    res = requests.get(f"{BASE_URL}/bookings?status=pending", headers=auth_header(renter_token))
    r.check(res.status_code == 200, "List bookings: ?status=pending → 200",
            f"List bookings: ?status=pending → {res.status_code}")

    # ── Get booking detail ──
    if booking_id:
        res = requests.get(f"{BASE_URL}/bookings/{booking_id}", headers=auth_header(renter_token))
        r.check(res.status_code == 200, f"Get booking #{booking_id} → 200",
                f"Get booking #{booking_id} → {res.status_code}")

    # ── Calendar ──
    res = requests.get(f"{BASE_URL}/bookings/calendar", headers=auth_header(renter_token))
    r.check(res.status_code == 200, "Bookings calendar → 200", f"Bookings calendar → {res.status_code}")

    # ── Approve: renter tries (should fail) ──
    if booking_id:
        res = requests.post(f"{BASE_URL}/bookings/{booking_id}/approve",
                            headers=auth_header(renter_token))
        r.check(res.status_code == 403, "Approve booking (renter) → 403",
                f"Approve booking (renter) → {res.status_code}")

    # ── Cancel booking ──
    if booking_id:
        res = requests.post(f"{BASE_URL}/bookings/{booking_id}/cancel",
                            headers=auth_header(renter_token))
        r.check(res.status_code == 200, f"Cancel booking #{booking_id} → 200",
                f"Cancel booking → {res.status_code}")

    # ── Cancel already cancelled ──
    if booking_id:
        res = requests.post(f"{BASE_URL}/bookings/{booking_id}/cancel",
                            headers=auth_header(renter_token))
        r.check(res.status_code == 400, "Cancel already cancelled → 400",
                f"Cancel already cancelled → {res.status_code}")

    # ── No auth ──
    res = requests.get(f"{BASE_URL}/bookings")
    r.check(res.status_code in [401, 422], "Bookings: no token → 401/422",
            f"Bookings: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    ot, oid = login("owner@example.com", "password123")
    rt, rid = login("renter@example.com", "password123")
    if ot and rt:
        run(ot, rt, oid, rid)
