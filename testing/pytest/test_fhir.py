import requests
import pytest

def test_uat_fhir_01_valid_ingestion(api_base_url, auth_header, mongo_db):
    patient_id = "pytest-fhir-01"
    mongo_db.patients.delete_many({"id": patient_id})
    
    data = {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [{"text": "Pytest FHIR Patient"}]
    }
    response = requests.post(f"{api_base_url}/Patient", json=data, headers=auth_header)
    assert response.status_code == 201
    assert mongo_db.patients.count_documents({"id": patient_id}) == 1

def test_uat_fhir_02_duplicate_prevention(api_base_url, auth_header, mongo_db):
    patient_id = "pytest-fhir-02"
    mongo_db.patients.delete_many({"id": patient_id})
    
    data = {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [{"text": "Duplicate Test"}]
    }
    # First post
    requests.post(f"{api_base_url}/Patient", json=data, headers=auth_header)
    # Second post (Atomic upsert should handle this)
    response = requests.post(f"{api_base_url}/Patient", json=data, headers=auth_header)
    
    assert response.status_code in [201, 200]
    assert mongo_db.patients.count_documents({"id": patient_id}) == 1

def test_uat_fhir_03_invalid_structure(api_base_url, auth_header):
    data = {
         "resourceType": "Patient",
         "name": "Invalid String Name instead of Array"
    }
    response = requests.post(f"{api_base_url}/Patient", json=data, headers=auth_header)
    assert response.status_code == 400
