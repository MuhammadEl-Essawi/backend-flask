"""
Test: Messages / Chat Endpoints
================================
Covers: send message, get conversation, inbox with unread count
"""
from helpers import *


def run(token1, token2, user1_id, user2_id):
    print_section("MESSAGES / CHAT ENDPOINTS")
    r = TestReport("Messages")

    # ── Send message ──
    res = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user2_id, "content": "Test message from test suite"
    })
    r.check(res.status_code == 201, "Send message → 201", f"Send message → {res.status_code}")

    # ── Send message to self ──
    res = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user1_id, "content": "Self message"
    })
    r.check(res.status_code == 400, "Message to self → 400", f"Message to self → {res.status_code}")

    # ── Send message: missing fields ──
    res = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={})
    r.check(res.status_code == 400, "Send message: empty → 400", f"Send message: empty → {res.status_code}")

    # ── Send message: too long ──
    res = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": user2_id, "content": "X" * 6000
    })
    r.check(res.status_code == 400, "Send message: too long → 400", f"Send message: too long → {res.status_code}")

    # ── Send message: non-existent receiver ──
    res = requests.post(f"{BASE_URL}/messages", headers=auth_header(token1), json={
        "receiver_id": 99999, "content": "Hello ghost"
    })
    r.check(res.status_code == 404, "Send message: user 99999 → 404", f"Send message: user 99999 → {res.status_code}")

    # ── Get conversation ──
    res = requests.get(f"{BASE_URL}/messages/{user2_id}", headers=auth_header(token1))
    r.check(res.status_code == 200 and "messages" in res.json(), "Get conversation → 200",
            f"Get conversation → {res.status_code}")

    # ── Get inbox ──
    res = requests.get(f"{BASE_URL}/messages/inbox", headers=auth_header(token1))
    if res.status_code == 200:
        inbox = res.json()
        if len(inbox) > 0:
            has_unread = "unread_count" in inbox[0]
            has_other = "other_user" in inbox[0]
            r.check(has_unread and has_other, "Inbox: has unread_count + other_user fields",
                    "Inbox: missing unread_count or other_user")
        else:
            r.check(True, "Inbox → 200 (empty)", "")
    else:
        r.log_fail(f"Inbox → {res.status_code}")

    # ── No auth ──
    res = requests.get(f"{BASE_URL}/messages/inbox")
    r.check(res.status_code in [401, 422], "Inbox: no token → 401/422", f"Inbox: no token → {res.status_code}")

    r.print_summary()
    return r.summary()


if __name__ == "__main__":
    t1, id1 = login("renter@example.com", "password123")
    t2, id2 = login("owner@example.com", "password123")
    if t1 and t2:
        run(t1, t2, id1, id2)
