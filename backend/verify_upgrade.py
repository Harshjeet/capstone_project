import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth():
    print("\n--- Testing Auth ---")
    # 1. Login (should succeed)
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if res.status_code == 200:
        print("Login Success")
        return res.json()["token"]
    else:
        print("Login Failed:", res.text)
        return None

def test_protected(token):
    print("\n--- Testing Protected Endpoint ---")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/Patient", headers=headers)
    if res.status_code == 200:
        print("Protected Access Success")
    else:
        print("Protected Access Failed:", res.status_code)

def test_validation(token):
    print("\n--- Testing Validation ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Invalid Data (Missing resourceType)
    invalid_data = {"code": {"text": "Invalid"}}
    res = requests.post(f"{BASE_URL}/Condition", json=invalid_data, headers=headers)
    if res.status_code == 400:
        print("Validation Caught Invalid Data Success")
    else:
        print("Validation Failed to Catch Error:", res.status_code, res.text)

    # Valid Data
    valid_data = {
        "resourceType": "Condition",
        "code": {"text": "Test Condition"},
        "subject": {"reference": "Patient/p001"},
        "clinicalStatus": {"text": "Active"} # Required by some profiles, but minimal valid R4 is mainly resourceType
    }
    # Note: fhir.resources might require specific structures.
    # Let's try minimal valid.
    
    res = requests.post(f"{BASE_URL}/Condition", json=valid_data, headers=headers)
    if res.status_code == 201:
        print("Valid Data Creation Success")
        return res.json()["id"]
    else:
        print("Valid Data Creation Failed:", res.text)
        return None

if __name__ == "__main__":
    token = test_auth()
    if token:
        test_protected(token)
        test_validation(token)
