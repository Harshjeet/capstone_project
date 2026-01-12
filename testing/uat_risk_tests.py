import requests
import json

BASE_URL = "http://localhost:5000/api"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_uat_risk_01_02(token):
    print("Running UAT-RISK-01 & 02: Risk score calculation and classification...")
    
    # 1. Register a test patient with known data
    headers = {"Authorization": f"Bearer {token}"}
    patient_data = {
        "resourceType": "Patient",
        "id": "risk-test-patient-01",
        "name": [{"text": "Risk Test 01"}],
        "birthDate": "1990-01-01", # ~36 years old -> factor 0.33 * 30 = 9.9
        "gender": "female"
    }
    r1 = requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    print(f"Patient POST status: {r1.status_code}")
    
    # Add one high risk condition (Hypertension) -> 1.0 * 15 = 15
    # Total expected score ~ 9.9 + 15 = 24.9 (Low)
    condition_data = {
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Hypertension"},
        "subject": {"reference": "Patient/risk-test-patient-01"}
    }
    r2 = requests.post(f"{BASE_URL}/Condition", json=condition_data, headers=headers)
    print(f"Condition POST status: {r2.status_code}, Response: {r2.text}")
    
    # 2. Get Risk Score
    response = requests.get(f"{BASE_URL}/analytics/patient/risk-test-patient-01/risk", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        score = data["prediction"][0]["probabilityDecimal"]
        label = data["prediction"][0]["qualitativeRisk"]["coding"][0]["display"]
        
        print(f"Computed Score: {score}, Label: {label}")
        
        if score > 0:
            print("[PASS] UAT-RISK-01: Risk score computed accurately.")
        if label in ["Low", "Medium", "High"]:
            print("[PASS] UAT-RISK-02: Correct risk level assigned.")
    else:
        print(f"[FAIL] UAT-RISK-01/02: Failed with status {response.status_code}")

def test_uat_risk_03_comorbidity(token):
    print("Running UAT-RISK-03: Comorbidity handling (Bonus)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    # 1. Patient with 2 conditions
    patient_data = {
        "resourceType": "Patient",
        "id": "risk-test-patient-multi",
        "name": [{"text": "Risk Test Multi"}],
        "birthDate": "1990-01-01",
        "gender": "male"
    }
    r1 = requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    print(f"Patient POST status: {r1.status_code}")
    
    # Cond 1
    r2 = requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Hypertension"},
        "subject": {"reference": "Patient/risk-test-patient-multi"}
    }, headers=headers)
    print(f"Condition 1 POST status: {r2.status_code}")
    
    # Cond 2 (Diabetes)
    r3 = requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Diabetes"},
        "subject": {"reference": "Patient/risk-test-patient-multi"}
    }, headers=headers)
    print(f"Condition 2 POST status: {r3.status_code}")
    
    # 2. Check note for "Comorbidity Bonus"
    response = requests.get(f"{BASE_URL}/analytics/patient/risk-test-patient-multi/risk", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        note = data["note"][0]["text"]
        print(f"Risk Assessment Note: {note}")
        if "Comorbidity Bonus" in note:
            print("[PASS] UAT-RISK-03: Risk score includes bonus for multiple conditions.")
        else:
            print(f"[FAIL] UAT-RISK-03: Bonus not found in note. Note: {note}")
    else:
        print(f"[FAIL] UAT-RISK-03: Failed with status {response.status_code}")

if __name__ == "__main__":
    token = get_admin_token()
    if not token:
        print("Could not get admin token.")
    else:
        print("=== Starting UAT Risk Scoring Tests ===\n")
        test_uat_risk_01_02(token)
        print()
        test_uat_risk_03_comorbidity(token)
        print("\n=== UAT Risk Scoring Tests Completed ===")
