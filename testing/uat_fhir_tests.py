import requests
import json
from pymongo import MongoClient

BASE_URL = "http://localhost:5000/api"
MONGO_URI = "mongodb://localhost:27017/fhir_db"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_uat_fhir_01_valid_ingestion(token):
    print("Running UAT-FHIR-01: Valid FHIR data ingestion...")
    client = MongoClient(MONGO_URI)
    db = client.fhir_db
    # Cleanup
    db.patients.delete_many({"id": "uat-test-patient-01"})
    initial_count = db.patients.count_documents({})
    
    patient_data = {
        "resourceType": "Patient",
        "id": "uat-test-patient-01",
        "name": [{"text": "UAT Test Patient"}],
        "gender": "male",
        "birthDate": "1990-01-01"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    
    if response.status_code == 201:
        new_count = db.patients.count_documents({})
        if new_count == initial_count + 1:
            print("[PASS] UAT-FHIR-01: Data ingested and stored in MongoDB.")
            return True
        else:
            print(f"[FAIL] UAT-FHIR-01: Response 201 but count did not increase correctly. ({initial_count} -> {new_count})")
    else:
        print(f"[FAIL] UAT-FHIR-01: Failed with status {response.status_code}. Response: {response.text}")
    return False

def test_uat_fhir_02_duplicate_prevention(token):
    print("Running UAT-FHIR-02: Duplicate FHIR data ingestion...")
    client = MongoClient(MONGO_URI)
    db = client.fhir_db
    
    # Cleanup any previous attempts
    db.patients.delete_many({"id": "uat-test-patient-duplicate"})
    
    patient_data = {
        "resourceType": "Patient",
        "id": "uat-test-patient-duplicate",
        "name": [{"text": "Duplicate Test Patient"}]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First insertion
    requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    count_after_first = db.patients.count_documents({"id": "uat-test-patient-duplicate"})
    
    # Second insertion (should not create a new record if UAT-FHIR-02 is met)
    requests.post(f"{BASE_URL}/Patient", json=patient_data, headers=headers)
    count_after_second = db.patients.count_documents({"id": "uat-test-patient-duplicate"})
    
    if count_after_first == 1 and count_after_second == 1:
        print("[PASS] UAT-FHIR-02: No duplicate records created.")
    else:
        print(f"[FAIL] UAT-FHIR-02: Duplicate records found. Count after 1st: {count_after_first}, Count after 2nd: {count_after_second}")

def test_uat_fhir_03_invalid_structure(token):
    print("Running UAT-FHIR-03: Invalid FHIR structure...")
    # Missing resourceType or invalid fields
    invalid_data = {
        "resourceType": "NotARealResource",
        "something": "wrong"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/Patient", json=invalid_data, headers=headers)
    
    if response.status_code == 400:
        print("[PASS] UAT-FHIR-03: Ingestion rejected with error.")
    else:
        print(f"[FAIL] UAT-FHIR-03: Expected 400, got {response.status_code}. Response: {response.text}")

if __name__ == "__main__":
    token = get_admin_token()
    if not token:
        print("Could not get admin token. Are services running?")
    else:
        print("=== Starting UAT FHIR Ingestion Tests ===\n")
        test_uat_fhir_01_valid_ingestion(token)
        print()
        test_uat_fhir_02_duplicate_prevention(token)
        print()
        test_uat_fhir_03_invalid_structure(token)
        print("\n=== UAT FHIR Ingestion Tests Completed ===")
