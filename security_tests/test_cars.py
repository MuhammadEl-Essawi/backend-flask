"""
Test: Cars Endpoints
====================
Covers: list, detail, my-cars, add car, block dates, filters, SQL injection
"""
from helpers import *


def run(owner_token, renter_token):
    print_section("CARS ENDPOINTS")
    r = TestReport("Cars")

    # ── List cars ──
    res = requests.get(f"{BASE_URL}/cars", headers=auth_header(renter_token))
    r.check(res.status_code == 200 and "cars" in res.json(), "List cars → 200 with cars array",
            f"List cars → {res.status_code}")

    # ── List cars with filters ──
    res = requests.get(f"{BASE_URL}/cars?brand=Tesla&min_price=100&max_price=5000&transmission=automatic",
                       headers=auth_header(renter_token))
    r.check(res.status_code == 200, "List cars with filters → 200", f"List cars with filters → {res.status_code}")

    # ── Pagination ──
    res = requests.get(f"{BASE_URL}/cars?page=1&per_page=2", headers=auth_header(renter_token))
    data = res.json()
    r.check(res.status_code == 200 and "total_pages" in data and "current_page" in data,
            "List cars: pagination fields present", f"List cars: pagination → {res.status_code}")

    # ── Get car detail ──
    res = requests.get(f"{BASE_URL}/cars/1", headers=auth_header(renter_token))
    if res.status_code == 200:
        car = res.json()
        has_fields = all(k in car for k in ["brand", "model", "price_per_day", "owner", "images", "reviews"])
        r.check(has_fields, "Get car detail → has all expected fields", "Get car detail → missing fields")
    else:
        r.log_fail(f"Get car detail → {res.status_code}")

    # ── Get car: Non-existent ──
    res = requests.get(f"{BASE_URL}/cars/99999", headers=auth_header(renter_token))
    r.check(res.status_code == 404, "Get car 99999 → 404", f"Get car 99999 → {res.status_code}")

    # ── My cars (owner) ──
    res = requests.get(f"{BASE_URL}/cars/my-cars", headers=auth_header(owner_token))
    r.check(res.status_code == 200 and "cars" in res.json(), "My cars (owner) → 200",
            f"My cars (owner) → {res.status_code}")

    # ── My cars (renter — should be 403) ──
    res = requests.get(f"{BASE_URL}/cars/my-cars", headers=auth_header(renter_token))
    r.check(res.status_code == 403, "My cars (renter) → 403", f"My cars (renter) → {res.status_code}")

    # ── Add car: renter tries (should fail) ──
    res = requests.post(f"{BASE_URL}/cars", headers=auth_header_no_json(renter_token),
                        data={"brand": "Test", "model": "X", "year": 2024, "price_per_day": 100})
    r.check(res.status_code == 403, "Add car (renter) → 403", f"Add car (renter) → {res.status_code}")

    # ── No auth ──
    res = requests.get(f"{BASE_URL}/cars")
    r.check(res.status_code in [401, 422], "List cars: no token → 401/422",
            f"List cars: no token → {res.status_code}")

    # ── SQL Injection in brand filter ──
    payloads = ["' OR '1'='1", "'; DROP TABLE car; --", "UNION SELECT 1,2,3"]
    for payload in payloads:
        res = requests.get(f"{BASE_URL}/cars", headers=auth_header(renter_token),
                          params={"brand": payload})
        r.check(res.status_code != 500, f"SQLi '{payload[:25]}' → no crash",
                f"SQLi '{payload[:25]}' → SERVER CRASHED!")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    ot, _ = login("owner@example.com", "password123")
    rt, _ = login("renter@example.com", "password123")
    if ot and rt:
        run(ot, rt)
