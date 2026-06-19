import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}

VICTIM_CREDENTIALS = {
    "email": "victim@example.com",
    "password": "password123"
}

ATTACKER_CREDENTIALS = {
    "email": "hacker@example.com",
    "password": "password123"
}

def log(message, status="INFO"):
    if status == "INFO":
        print(f"{Fore.CYAN}[*] {message}")
    elif status == "SUCCESS":
        print(f"{Fore.GREEN}[+] {message}")
    elif status == "FAIL":
        print(f"{Fore.RED}[-] {message}")
    elif status == "WARN":
        print(f"{Fore.YELLOW}[!] {message}")

def get_auth_token(email, password):
    url = f"{BASE_URL}/auth/login"
    payload = {"email": email, "password": password}
    
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        if response.status_code == 200:
            token = response.json().get("access_token")
            log(f"Authenticated successfully as {email}", "SUCCESS")
            return token
        else:
            log(f"Failed to login as {email}: {response.text}", "FAIL")
            return None
    except Exception as e:
        log(f"Connection Error: {e}", "FAIL")
        return None

def test_idor(victim_token, attacker_token):
    log("--- Starting IDOR Attack Simulation ---", "WARN")

    create_url = f"{BASE_URL}/bookings"
    booking_data = {
        "car_id": 1,
        "start_date": "2026-05-01",
        "end_date": "2026-05-05"
    }
    
    res = requests.post(create_url, json=booking_data, headers={"Authorization": f"Bearer {victim_token}", **HEADERS})
    
    if res.status_code != 201:
        log("Victim failed to create booking. Skipping IDOR test.", "FAIL")
        return

    booking_id = res.json().get("data", {}).get("id")
    log(f"Victim created booking with ID: {booking_id}", "SUCCESS")

    log(f"Attacker attempting to delete Booking ID: {booking_id}...", "INFO")
    
    delete_url = f"{BASE_URL}/bookings/{booking_id}"
    
    attack_res = requests.delete(delete_url, headers={"Authorization": f"Bearer {attacker_token}"})
    
    if attack_res.status_code == 200 or attack_res.status_code == 204:
        log(f"CRITICAL VULNERABILITY: Attacker deleted Victim's booking! (IDOR Found)", "FAIL")
    elif attack_res.status_code == 403:
        log("Secure! Server blocked the attacker (403 Forbidden).", "SUCCESS")
    elif attack_res.status_code == 404:
        log("Secure-ish (404 Not Found) - Or attacker can't see the resource.", "SUCCESS")
    else:
        log(f"Unexpected response code: {attack_res.status_code}", "INFO")

def fuzz_booking_endpoint(token):
    log("--- Starting Fuzzing / Input Validation Test ---", "WARN")
    
    url = f"{BASE_URL}/bookings"
    auth_header = {"Authorization": f"Bearer {token}", **HEADERS}

    payloads = [
        {"desc": "Negative Car ID", "data": {"car_id": -1, "start_date": "2026-01-01", "end_date": "2026-01-02"}},
        {"desc": "End Date before Start Date", "data": {"car_id": 1, "start_date": "2026-01-05", "end_date": "2026-01-01"}},
        {"desc": "Huge String in ID", "data": {"car_id": "999999 OR 1=1", "start_date": "2026-01-01", "end_date": "2026-01-02"}},
        {"desc": "Empty Data", "data": {}}
    ]

    for p in payloads:
        res = requests.post(url, json=p["data"], headers=auth_header)
        if res.status_code == 500:
            log(f"Server CRASHED (500) on payload: {p['desc']}", "FAIL")
        elif res.status_code == 400 or res.status_code == 422:
            log(f"Server handled payload: {p['desc']} correctly ({res.status_code})", "SUCCESS")
        else:
            log(f"Odd response for {p['desc']}: {res.status_code}", "INFO")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}=== AUTOMATED SECURITY AUDIT SCRIPT ===\n")
    
    victim_token = get_auth_token(VICTIM_CREDENTIALS["email"], VICTIM_CREDENTIALS["password"])
    attacker_token = get_auth_token(ATTACKER_CREDENTIALS["email"], ATTACKER_CREDENTIALS["password"])

    if victim_token and attacker_token:
        test_idor(victim_token, attacker_token)
        fuzz_booking_endpoint(attacker_token)
    else:
        log("Cannot proceed without valid tokens for both users.", "FAIL")