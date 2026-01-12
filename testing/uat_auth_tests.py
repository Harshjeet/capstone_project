import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_uat_auth_01_valid_login():
    print("Running UAT-AUTH-01: User login with valid credentials...")
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if "token" in data and data["role"] == "admin":
            print("[PASS] UAT-AUTH-01: JWT token generated and user logged in as Admin.")
            return data["token"]
        else:
            print(f"[FAIL] UAT-AUTH-01: Missing token or incorrect role. Data: {data}")
    else:
        print(f"[FAIL] UAT-AUTH-01: Login failed with status {response.status_code}. Response: {response.text}")
    return None

def test_uat_auth_03_invalid_login():
    print("Running UAT-AUTH-03: Invalid login attempt...")
    payload = {
        "username": "admin",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    
    if response.status_code == 401:
        print("[PASS] UAT-AUTH-03: Login denied with error message.")
    else:
        print(f"[FAIL] UAT-AUTH-03: Expected 401, got {response.status_code}. Response: {response.text}")

def test_uat_auth_04_unauthorized_api_access(patient_token):
    print("Running UAT-AUTH-04: Unauthorized API access (Patient accessing Admin endpoints)...")
    # Endpoint that requires admin role
    admin_endpoint = f"{BASE_URL}/admin/patients"
    headers = {
        "Authorization": f"Bearer {patient_token}"
    }
    response = requests.get(admin_endpoint, headers=headers)
    
    if response.status_code == 403:
        print("[PASS] UAT-AUTH-04: Access blocked with authorization error (403).")
    else:
        print(f"[FAIL] UAT-AUTH-04: Expected 403, got {response.status_code}. Response: {response.text}")

def get_patient_token():
    payload = {
        "username": "test",
        "password": "123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

if __name__ == "__main__":
    print("=== Starting UAT Backend Tests ===\n")
    
    # UAT-AUTH-01
    admin_token = test_uat_auth_01_valid_login()
    print()
    
    # UAT-AUTH-03
    test_uat_auth_03_invalid_login()
    print()
    
    # UAT-AUTH-04
    patient_token = get_patient_token()
    if patient_token:
        test_uat_auth_04_unauthorized_api_access(patient_token)
    else:
        print("[SKIP] UAT-AUTH-04: Could not get patient token.")
    
    print("\n=== UAT Backend Tests Completed ===")
