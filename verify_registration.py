import requests
import sys
import datetime

BASE_URL = "http://localhost:5000/api"

def test_registration():
    session = requests.Session()
    ts = int(datetime.datetime.now().timestamp())
    username = f"strict_user_{ts}"

    # 1. Valid Registration with structured data
    print(f"1. Registering {username} with structured data...")
    reg_data = {
        "username": username,
        "password": "password123",
        "patientDetails": {
            "firstName": "Strict",
            "lastName": "User",
            "gender": "male",
            "birthDate": "1990-01-01",
            "mobile": "555-0199",
            "address": "123 Safe St"
        },
        "conditions": ["Diabetes mellitus", "Invalid Condition Code", "<script>alert('xss')</script>"],
        "vitals": {
            "systolic": "120",
            "diastolic": "80",
            "heartRate": "72",
            "weight": "70",
            "height": "175",
            "badField": "should_be_ignored"
        },
        "insuranceProvider": "BlueCross <script>evil()</script>"
    }
    
    try:
        res = session.post(f"{BASE_URL}/auth/register", json=reg_data)
        if res.status_code != 201:
            print(f"Registration failed: {res.text}")
            sys.exit(1)
        
        data = res.json()
        patient_id = data["patientId"]
        print(f"Success. Patient ID: {patient_id}")
        
        # 2. Login to inspect data
        print("2. Logging in to inspect stored data...")
        login_res = session.post(f"{BASE_URL}/auth/login", json={"username": username, "password": "password123"})
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Verify Conditions (Should filter invalid ones)
        print("3. Verifying Conditions...")
        cond_res = session.get(f"{BASE_URL}/Condition?patient={patient_id}", headers=headers)
        conditions = cond_res.json()
        cond_names = [c["code"]["text"] for c in conditions]
        print(f"Stored Conditions: {cond_names}")
        
        if "Diabetes mellitus" in cond_names and "Invalid Condition Code" not in cond_names:
             print("Condition filtering passed.")
        else:
             print("Condition filtering FAILED.")

        # 4. Verify Vitals
        print("4. Verifying Vitals...")
        obs_res = session.get(f"{BASE_URL}/Observation?patient={patient_id}", headers=headers)
        observations = obs_res.json()
        print(f"Stored Observations count: {len(observations)}")
        # Expect 5 vitals
        if len(observations) >= 5:
             print("Vitals storage passed.")
        else:
             print("Vitals storage FAILED.")

        # 5. Verify Insurance (Sanitization)
        print("5. Verifying Coverage Sanitization...")
        cov_res = session.get(f"{BASE_URL}/Coverage?patient={patient_id}", headers=headers)
        coverages = cov_res.json()
        if coverages:
            provider = coverages[0]["payor"][0]["display"]
            print(f"Stored Provider: {provider}")
            if "<script>" not in provider and "BlueCross" in provider:
                print("Sanitization passed.")
            else:
                print("Sanitization FAILED.")
        else:
            print("No coverage found. FAILED.")

    except Exception as e:
        print(f"Test failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_registration()
