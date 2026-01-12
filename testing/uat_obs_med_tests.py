import requests
import json

BASE_URL = "http://localhost:5000/api"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_uat_obs_01_02_vital_analytics(token):
    print("Running UAT-OBS-01 & UAT-OBS-02: Abnormal vital detection and aggregation...")
    
    # 1. Create a test patient and high vital
    headers = {"Authorization": f"Bearer {token}"}
    patient_data = {
        "resourceType": "Patient",
        "id": "obs-test-patient",
        "name": [{"text": "Obs Test"}],
        "birthDate": "1980-01-01" # Age group 31-45 or 46-60 depending on year
    }
    requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    
    # High BP (150 > 140)
    observation_data = {
        "resourceType": "Observation",
        "status": "final",
        "code": {"text": "Systolic blood pressure"},
        "subject": {"reference": "Patient/obs-test-patient"},
        "valueQuantity": {"value": 150, "unit": "mmHg"}
    }
    requests.post(f"{BASE_URL}/Observation", json=observation_data, headers=headers)
    
    # 2. Check analytics
    response = requests.get(f"{BASE_URL}/analytics/population/vitals", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        found_high_bp = any(item["vital"] == "High BP" and item["count"] > 0 for item in data)
        if found_high_bp:
            print("[PASS] UAT-OBS-01: High BP flagged correctly.")
            print("[PASS] UAT-OBS-02: Aggregated statistics displayed.")
        else:
            print(f"[FAIL] UAT-OBS-01/02: High BP not found in analytics. Data: {data}")
    else:
        print(f"[FAIL] UAT-OBS-01/02: Failed with status {response.status_code}")

def test_uat_med_01_medication_analytics(token):
    print("Running UAT-MED-01: Medication usage analytics...")
    
    # Ensure there's a med and condition to link
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Check current trends
    response = requests.get(f"{BASE_URL}/analytics/population/medications", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        by_disease = data.get("by_disease", [])
        if isinstance(by_disease, list) and len(by_disease) > 0:
            sample = by_disease[0]
            if "medication" in sample and "disease" in sample and "count" in sample:
                print(f"[PASS] UAT-MED-01: Medication trends shown by disease. Sample: {sample}")
            else:
                print(f"[FAIL] UAT-MED-01: Unexpected data structure. Sample: {sample}")
        else:
            print(f"[FAIL] UAT-MED-01: Empty or invalid list returned. Data: {data}")
    else:
        print(f"[FAIL] UAT-MED-01: Failed with status {response.status_code}")

if __name__ == "__main__":
    token = get_admin_token()
    if not token:
        print("Could not get admin token.")
    else:
        print("=== Starting UAT Observation & Medication Analytics Tests ===\n")
        test_uat_obs_01_02_vital_analytics(token)
        print()
        test_uat_med_01_medication_analytics(token)
        print("\n=== UAT Observation & Medication Analytics Tests Completed ===")
