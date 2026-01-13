import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_uat_sim_ins_all(token):
    print("Running UAT-SIM-01, UAT-INS-01, UAT-INS-02...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Register two similar patients
    p1_id = "sim-p1"
    p2_id = "sim-p2"
    
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/fhir_db")
    db = client.fhir_db
    db.patients.delete_many({"id": {"$in": [p1_id, p2_id]}})
    db.conditions.delete_many({"subject.reference": {"$in": [f"Patient/{p1_id}", f"Patient/{p2_id}"]}})
    db.medications.delete_many({"subject.reference": {"$in": [f"Patient/{p1_id}", f"Patient/{p2_id}"]}})
    db.observations.delete_many({"subject.reference": {"$in": [f"Patient/{p1_id}", f"Patient/{p2_id}"]}})
    db.risk_assessments.delete_many({"subject.reference": {"$in": [f"Patient/{p1_id}", f"Patient/{p2_id}"]}})
    
    # Delete if exists to ensure clean state
    # (Models already prevent duplicates but let's be fresh)
    p_data_1 = {
        "resourceType": "Patient",
        "id": p1_id,
        "name": [{"text": "Target Patient"}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }
    p_data_2 = {
        "resourceType": "Patient",
        "id": p2_id,
        "name": [{"text": "Similar Patient"}],
        "gender": "male",
        "birthDate": "1990-01-01" # Exact match for age and gender
    }
    
    r1 = requests.post(f"{BASE_URL}/Patient", json=p_data_1, headers=headers)
    print(f"Patient 1 Status: {r1.status_code}")
    r2 = requests.post(f"{BASE_URL}/Patient", json=p_data_2, headers=headers)
    print(f"Patient 2 Status: {r2.status_code}")
    
    # 2. Add High Risk conditions to Target Patient to test Insurance Recommendation
    # Hypertension + Diabetes
    r3 = requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Hypertension"},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)
    print(f"Condition 1 Status: {r3.status_code}")
    
    r4 = requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Diabetes"},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)
    
    requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Heart failure"},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)

    requests.post(f"{BASE_URL}/Condition", json={
        "resourceType": "Condition",
        "clinicalStatus": {"text": "Active"},
        "code": {"text": "Cancer"},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)
    print(f"Condition 2 Status: {r4.status_code}")
    
    r5 = requests.post(f"{BASE_URL}/Medication", json={
        "resourceType": "MedicationRequest",
        "status": "active",
        "intent": "order",
        "medication": {"concept": {"text": "Metformin"}},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)
    print(f"Med 1 Status: {r5.status_code}")

    r6 = requests.post(f"{BASE_URL}/Medication", json={
        "resourceType": "MedicationRequest",
        "status": "active",
        "intent": "order",
        "medication": {"concept": {"text": "Lisinopril"}},
        "subject": {"reference": f"Patient/{p1_id}"}
    }, headers=headers)
    requests.post(f"{BASE_URL}/Observation", json={
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"display": "Systolic blood pressure"}]},
        "subject": {"reference": f"Patient/{p1_id}"},
        "valueQuantity": {"value": 150, "unit": "mmHg"}
    }, headers=headers)

    response = requests.get(f"{BASE_URL}/analytics/patient/{p1_id}/similarity", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Data: {json.dumps(data, indent=2)}")
        
        # UAT-SIM-01 Check: Similarity criteria applied
        explanation = data.get("explanation", "")
        if "similar patients" in explanation:
            print("[PASS] UAT-SIM-01: Similarity criteria applied.")
        else:
            print("[FAIL] UAT-SIM-01: No similarity mention.")
            
        # UAT-INS-01 Check: Risk level evaluated and suitable plan recommended
        risk_level = data.get("risk_level")
        plans = [p["name"] for p in data.get("recommended_plans", [])]
        print(f"Risk Level: {risk_level}, Recommended Plans: {plans}")
        
        # Accept High or Medium if the plans match the ruleset
        if risk_level == "High" and any(p in ["Gold Premium", "Platinum Elite"] for p in plans):
            print("[PASS] UAT-INS-01: High-risk insurance plans recommended.")
        elif risk_level == "Medium" and any(p in ["Standard Care", "Gold Premium"] for p in plans):
            print("[PASS] UAT-INS-01: Medium-risk insurance plans recommended.")
        else:
             print(f"[FAIL] UAT-INS-01: Unexpected recommendation.")

        # UAT-INS-02 Check: Resolution explanation displayed clearly
        if explanation and len(explanation) > 20:
            print("[PASS] UAT-INS-02: Recommendation explanation displayed clearly.")
        else:
            print("[FAIL] UAT-INS-02: Explanation missing or too short.")
    else:
        print(f"[FAIL] Sim/Ins Request failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    token = get_admin_token()
    if token:
        print("=== Starting UAT Similarity & Insurance Tests ===\n")
        test_uat_sim_ins_all(token)
        print("\n=== UAT Similarity & Insurance Tests Completed ===")
    else:
        print("Could not get admin token.")
