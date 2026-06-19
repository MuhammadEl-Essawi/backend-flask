import requests

BASE_URL = "http://127.0.0.1:5000"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2ODgzODAwOSwianRpIjoiMzg0ZjczZWQtZDg4ZC00YmI0LTkwYTEtMmQ4NzQyODIzZDY5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3Njg4MzgwMDksImNzcmYiOiJjZDUyZjdkNi1hNTYwLTQzMjgtOTU3MC1kYjU4MjdiYzZhZTIiLCJleHAiOjE3Njg4Mzg5MDksInJvbGUiOiJvd25lciJ9.-cROYmXv4rZ7ukBXhtSJGiyjXU_Z74ENoXBZ_xw4U28"

headers = {"Authorization": f"Bearer {TOKEN}"}

files = {
    'car_license_image': ('virus.py', 'print("Hacked")', 'application/x-python'),
    'images': ('hack.exe', 'binarydata', 'application/octet-stream')
}

data = {
    "brand": "HackedCar",
    "model": "Test",
    "year": 2025,
    "price_per_day": 100,
    "location_city": "Cairo",
    "transmission": "Manual",
    "license_plate": "HACK-999"
}

print("[*] Attempting to upload malicious files...")

try:
    response = requests.post(f"{BASE_URL}/cars", headers=headers, data=data, files=files)
    
    if response.status_code == 201:
        print("[!] CRITICAL: The server ACCEPTED the virus file!")
    elif response.status_code == 400 or response.status_code == 422:
        print("[+] Secure! The server rejected the file format.")
    else:
        print(f"[-] Status Code: {response.status_code}")
        print(f"[-] Response: {response.text}")
except Exception as e:
    print(e)