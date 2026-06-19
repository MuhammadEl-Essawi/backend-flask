"""
Test: Search History & Partner Program
=======================================
Covers: search history CRUD, partner application
"""
from helpers import *


def run_search(token):
    print_section("SEARCH HISTORY ENDPOINTS")
    r = TestReport("Search History")

    res = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={"query": "Ferrari Mansoura"})
    r.check(res.status_code == 201, "Save search → 201", f"Save search → {res.status_code}")

    res = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={"query": ""})
    r.check(res.status_code == 400, "Save search: empty query → 400", f"Save search: empty → {res.status_code}")

    res = requests.get(f"{BASE_URL}/search/history", headers=auth_header(token))
    if res.status_code == 200:
        r.check("history" in res.json(), "Get search history → has history array", "Get history → missing array")
    else:
        r.log_fail(f"Get search history → {res.status_code}")

    res = requests.post(f"{BASE_URL}/search/history", headers=auth_header(token), json={"query": "Ferrari Mansoura"})
    r.check(res.status_code == 201, "Save duplicate → 201 (replaces old)", f"Save duplicate → {res.status_code}")

    res = requests.delete(f"{BASE_URL}/search/history", headers=auth_header(token))
    r.check(res.status_code == 200, "Clear search history → 200", f"Clear history → {res.status_code}")

    res = requests.get(f"{BASE_URL}/search/history")
    r.check(res.status_code in [401, 422], "Search history: no token → 401/422", f"No token → {res.status_code}")

    r.print_summary()
    return r.summary()


def run_partner(token):
    print_section("PARTNER PROGRAM ENDPOINTS")
    r = TestReport("Partner Program")

    res = requests.post(f"{BASE_URL}/partner/apply", headers=auth_header_no_json(token), data={
        "full_name": "Test Partner", "email": "partner@test.com", "contact": "+201000000000",
        "driving_license_number": "DL-999888", "car_brand": "BMW", "car_model": "X5"
    })
    r.check(res.status_code in [201, 400], "Apply as partner → 201/400 (already applied)", f"Apply → {res.status_code}")

    res = requests.post(f"{BASE_URL}/partner/apply", headers=auth_header_no_json(token), data={"full_name": "Test"})
    r.check(res.status_code == 400, "Apply: missing fields → 400", f"Apply missing → {res.status_code}")

    res = requests.get(f"{BASE_URL}/partner/status", headers=auth_header(token))
    r.check(res.status_code == 200 and "applications" in res.json(), "Partner status → 200", f"Status → {res.status_code}")

    res = requests.post(f"{BASE_URL}/partner/apply", data={"full_name": "No Auth"})
    r.check(res.status_code in [401, 422], "Partner apply: no token → 401/422", f"No token → {res.status_code}")

    r.print_summary()
    return r.summary()


def run_static_pages():
    print_section("STATIC PAGES ENDPOINTS")
    r = TestReport("Static Pages")

    res = requests.get(f"{BASE_URL}/pages/privacy-policy")
    if res.status_code == 200:
        data = res.json()
        r.check("title" in data and "content" in data, "Privacy policy → has title + content", "Privacy → missing fields")
    else:
        r.log_fail(f"Privacy policy → {res.status_code}")

    res = requests.get(f"{BASE_URL}/pages/terms")
    r.check(res.status_code == 200, "Terms of service → 200", f"Terms → {res.status_code}")

    res = requests.get(f"{BASE_URL}/pages/invite-info")
    r.check(res.status_code == 200, "Invite info → 200", f"Invite → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    t, _ = login("renter@example.com", "password123")
    if t:
        run_search(t)
        run_partner(t)
    run_static_pages()
