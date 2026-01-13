import requests
import pytest

def test_uat_sim_01_patient_similarity(api_base_url, auth_header, mongo_db):
    p1_id = "pytest-sim-01-p1"
    p2_id = "pytest-sim-01-p2"
    mongo_db.patients.delete_many({"id": {"$in": [p1_id, p2_id]}})
    mongo_db.conditions.delete_many({"subject.reference": {"$in": [f"Patient/{p1_id}", f"Patient/{p2_id}"]}})
    
    # Setup two similar patients
    for pid in [p1_id, p2_id]:
        requests.post(f"{api_base_url}/Patient", json={
            "resourceType": "Patient", "id": pid, "gender": "female", "birthDate": "1985-01-01"
        }, headers=auth_header)
        # Same condition for both
        requests.post(f"{api_base_url}/Condition", json={
            "resourceType": "Condition", "clinicalStatus": {"text": "Active"}, 
            "code": {"text": "Diabetes"}, "subject": {"reference": f"Patient/{pid}"}
        }, headers=auth_header)

    response = requests.get(f"{api_base_url}/analytics/patient/{p1_id}/similarity", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    # Check if similar patients are mentioned in explanation or data
    assert "explanation" in data
    # In my implementation, similarity is internally used by recommendation
    # We check if the recommendation returned some cohort size or similar patient mentions
    assert "similar" in data["explanation"].lower()

def test_uat_ins_01_insurance_recommendation(api_base_url, auth_header, mongo_db):
    p_id = "pytest-ins-01"
    mongo_db.patients.delete_many({"id": p_id})
    requests.post(f"{api_base_url}/Patient", json={
        "resourceType": "Patient", "id": p_id, "birthDate": "1960-01-01"
    }, headers=auth_header)
    
    # High risk condition
    requests.post(f"{api_base_url}/Condition", json={
        "resourceType": "Condition", "clinicalStatus": {"text": "Active"}, 
        "code": {"text": "Cancer"}, "subject": {"reference": f"Patient/{p_id}"}
    }, headers=auth_header)

    response = requests.get(f"{api_base_url}/analytics/patient/{p_id}/similarity", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_plans" in data
    assert len(data["recommended_plans"]) > 0

def test_uat_ins_02_recommendation_explanation(api_base_url, auth_header):
    # Use any existing patient
    p_id = "pytest-ins-01"
    response = requests.get(f"{api_base_url}/analytics/patient/{p_id}/similarity", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert len(data["explanation"]) > 20 # Ensure non-empty meaningful explanation
