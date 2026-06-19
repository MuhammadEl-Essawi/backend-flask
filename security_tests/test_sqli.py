import requests

BASE_URL = "http://127.0.0.1:5000"
SEARCH_URL = f"{BASE_URL}/cars"

payloads = ["'", "' OR '1'='1", "admin' --", "UNION SELECT 1,2,3"]

print("[*] Testing SQL Injection on Search Filter...")

for payload in payloads:
    params = {"brand": payload}
    response = requests.get(SEARCH_URL, params=params)
    
    if response.status_code == 500:
        print(f"[!] DANGER: Server crashed (Potential SQLi) with payload: {payload}")
    elif len(response.json().get('cars', [])) > 100: 
        print(f"[!] DANGER: Logic bypassed with payload: {payload}")
    else:
        print(f"[+] Safe response for: {payload}")