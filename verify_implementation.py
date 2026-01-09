import requests
import sys

BASE_URL = "http://localhost:5000/api"

def test_flow():
    session = requests.Session()
    
    # 1. Register
    print("1. Registering new patient...")
    reg_data = {
        "username": "test_patient_001",
        "password": "password123",
        "patientDetails": {
            "firstName": "Test",
            "lastName": "User",
            "gender": "male",
            "birthDate": "1980-01-01",
            "mobile": "1234567890",
            "address": "123 Test St"
        },
        "conditions": ["Diabetes mellitus"],
        "observations": []
    }
    try:
        res = session.post(f"{BASE_URL}/auth/register", json=reg_data)
        if res.status_code == 400 and "already exists" in res.text:
            print("User already exists, proceeding to login.")
        elif res.status_code != 201:
            print(f"Registration failed: {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    # 2. Login
    print("2. Logging in...")
    login_data = {"username": "test_patient_001", "password": "password123"}
    res = session.post(f"{BASE_URL}/auth/login", json=login_data)
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        sys.exit(1)
        
    token = res.json()["token"]
    patient_id = res.json()["patientId"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in. Patient ID: {patient_id}")

    # 3. Check Recommendation (Should fail without consent)
    print("3. Checking Recommendation (Expect 403)...")
    res = session.post(f"{BASE_URL}/recommendation/{patient_id}", headers=headers)
    if res.status_code == 403:
        print("Success: Access denied as expected.")
    else:
        print(f"Unexpected status: {res.status_code}")

    # 4. Give Consent
    print("4. Granting Consent...")
    consent_data = {
        "resourceType": "Consent",
        "status": "active",
        "patient": {"reference": f"Patient/{patient_id}"}
    }
    res = session.post(f"{BASE_URL}/Consent", json=consent_data, headers=headers)
    if res.status_code != 201:
        print(f"Consent failed: {res.text}")
        sys.exit(1)
    print("Consent granted.")

    # 5. Check Recommendation (Should succeed)
    print("5. Checking Recommendation again...")
    res = session.post(f"{BASE_URL}/recommendation/{patient_id}", headers=headers)
    if res.status_code != 200:
        print(f"Recommendation failed: {res.text}")
        sys.exit(1)
    
    data = res.json()
    print(f"Recommended Plan: {data['recommended_plan']['name']}")
    print(f"Similar Patients Found: {data['similar_cohort_size']}")
    
    if data['recommended_plan']['id'] == 'gold' or data['recommended_plan']['id'] == 'platinum': 
        print("Recommendation logic looks correct (Diabetes -> Gold/Platinum).")
    elif data['recommended_plan']['id'] == 'basic':
        print("Warning: Recommended Basic plan for Diabetes? Check logic.")

    # 6. Select Plan
    print("6. Selecting Plan...")
    coverage_data = {
        "resourceType": "Coverage",
        "beneficiary": {"reference": f"Patient/{patient_id}"},
        "class": [{"name": data['recommended_plan']['name'], "value": data['recommended_plan']['id']}]
    }
    res = session.post(f"{BASE_URL}/Coverage", json=coverage_data, headers=headers)
    if res.status_code != 201:
        print(f"Coverage creation failed: {res.text}")
        sys.exit(1)
    print("Plan selected.")

    print("\nVerification Complete: All flows successful!")

if __name__ == "__main__":
    test_flow()
