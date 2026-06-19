import requests

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"

email = "admin@example.com" 
passwords = ["123456", "password", "admin", "wrongpass", "secret", "123123", "bessawy"]

print(f"[*] Starting Brute Force Attack on {email}...")

for i, pwd in enumerate(passwords):
    try:
        response = requests.post(LOGIN_URL, json={
            "email": email,
            "password": pwd
        })
        
        if response.status_code == 200:
            print(f"[+] CRITICAL: Password FOUND: {pwd}")
            break
        elif response.status_code == 429: # 429 means Too Many Requests
            print(f"[+] Secure! Server blocked us (Rate Limit hit) at attempt #{i+1}")
            break
        else:
            print(f"[-] Attempt {i+1}: Failed ({pwd}) - Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")