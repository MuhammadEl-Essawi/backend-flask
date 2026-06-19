"""
Test: Favorites, Reviews, Profile Endpoints
=============================================
Covers: favorites CRUD, reviews CRUD, user profile, profile photo
"""
from helpers import *


def run_favorites(token):
    print_section("FAVORITES ENDPOINTS")
    r = TestReport("Favorites")

    res = requests.post(f"{BASE_URL}/favorites/1", headers=auth_header(token))
    r.check(res.status_code in [201, 400], "Add favorite → 201/400 (already exists)", f"Add favorite → {res.status_code}")

    res = requests.get(f"{BASE_URL}/favorites", headers=auth_header(token))
    r.check(res.status_code == 200 and "favorites" in res.json(), "Get favorites → 200", f"Get favorites → {res.status_code}")

    res = requests.post(f"{BASE_URL}/favorites/99999", headers=auth_header(token))
    r.check(res.status_code == 404, "Add favorite car 99999 → 404", f"Add favorite car 99999 → {res.status_code}")

    res = requests.delete(f"{BASE_URL}/favorites/1", headers=auth_header(token))
    r.check(res.status_code in [200, 404], "Remove favorite → 200/404", f"Remove favorite → {res.status_code}")

    res = requests.get(f"{BASE_URL}/favorites")
    r.check(res.status_code in [401, 422], "Favorites: no token → 401/422", f"Favorites: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


def run_reviews(token):
    print_section("REVIEWS ENDPOINTS")
    r = TestReport("Reviews")

    res = requests.get(f"{BASE_URL}/reviews?car_id=1")
    r.check(res.status_code == 200 and "reviews" in res.json(), "List reviews → 200", f"List reviews → {res.status_code}")

    res = requests.post(f"{BASE_URL}/reviews", headers=auth_header(token), json={
        "car_id": 1, "rating": 10, "comment": "Too high"
    })
    r.check(res.status_code in [400, 403], "Add review: rating=10 → rejected", f"Add review: rating=10 → {res.status_code}")

    res = requests.post(f"{BASE_URL}/reviews", headers=auth_header(token), json={})
    r.check(res.status_code == 400, "Add review: empty → 400", f"Add review: empty → {res.status_code}")

    res = requests.post(f"{BASE_URL}/reviews", headers=H_JSON, json={"car_id": 1, "rating": 5})
    r.check(res.status_code in [401, 422], "Add review: no token → 401/422", f"Add review: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


def run_profile(token):
    print_section("USER PROFILE ENDPOINTS")
    r = TestReport("Profile")

    res = requests.get(f"{BASE_URL}/users/profile", headers=auth_header(token))
    if res.status_code == 200:
        data = res.json()
        has_fields = all(k in data for k in ["name", "email", "phone", "profile_image"])
        r.check(has_fields, "Get profile → has all expected fields", "Get profile → missing fields")
    else:
        r.log_fail(f"Get profile → {res.status_code}")

    res = requests.put(f"{BASE_URL}/users/profile", headers=auth_header(token), json={"first_name": "Updated", "last_name": "Name"})
    r.check(res.status_code == 200, "Update profile → 200", f"Update profile → {res.status_code}")

    res = requests.put(f"{BASE_URL}/users/profile", headers=auth_header(token), json={"email": "hacked@evil.com"})
    r.check(res.status_code == 400, "Update profile: email change → 400", f"Update profile: email change → {res.status_code}")

    res = requests.get(f"{BASE_URL}/users/profile")
    r.check(res.status_code in [401, 422], "Profile: no token → 401/422", f"Profile: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    t, _ = login("renter@example.com", "password123")
    if t:
        run_favorites(t)
        run_reviews(t)
        run_profile(t)
