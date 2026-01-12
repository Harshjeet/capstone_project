import requests
import pytest

def test_uat_risk_01_calculation(api_base_url, auth_header, mongo_db):
    patient_id = "pytest-risk-calc"
    mongo_db.patients.delete_many({"id": patient_id})
    requests.post(f"{api_base_url}/Patient", json={
        "resourceType": "Patient", "id": patient_id, "birthDate": "1980-01-01", "gender": "male"
    }, headers=auth_header)
    
    response = requests.get(f"{api_base_url}/analytics/patient/{patient_id}/risk", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"][0]["probabilityDecimal"] > 0

def test_uat_risk_02_classification(api_base_url, auth_header, mongo_db):
    patient_id = "pytest-risk-low"
    mongo_db.patients.delete_many({"id": patient_id})
    # Young patient, no conditions -> Low
    requests.post(f"{api_base_url}/Patient", json={
        "resourceType": "Patient", "id": patient_id, "birthDate": "2010-01-01", "gender": "female"
    }, headers=auth_header)
    
    response = requests.get(f"{api_base_url}/analytics/patient/{patient_id}/risk", headers=auth_header)
    assert response.status_code == 200
    label = response.json()["prediction"][0]["qualitativeRisk"]["coding"][0]["display"]
    assert label == "Low"

def test_uat_risk_03_comorbidity_bonus(api_base_url, auth_header, mongo_db):
    patient_id = "pytest-risk-bonus"
    mongo_db.patients.delete_many({"id": patient_id})
    mongo_db.conditions.delete_many({"subject.reference": f"Patient/{patient_id}"})
    
    requests.post(f"{api_base_url}/Patient", json={"resourceType": "Patient", "id": patient_id}, headers=auth_header)
    
    # Add two conditions
    requests.post(f"{api_base_url}/Condition", json={
        "resourceType": "Condition", "clinicalStatus": {"text": "Active"}, 
        "code": {"text": "Hypertension"}, "subject": {"reference": f"Patient/{patient_id}"}
    }, headers=auth_header)
    requests.post(f"{api_base_url}/Condition", json={
        "resourceType": "Condition", "clinicalStatus": {"text": "Active"}, 
        "code": {"text": "Diabetes"}, "subject": {"reference": f"Patient/{patient_id}"}
    }, headers=auth_header)
    
    response = requests.get(f"{api_base_url}/analytics/patient/{patient_id}/risk", headers=auth_header)
    assert response.status_code == 200
    note = response.json().get("note", [{}])[0].get("text", "")
    assert "Comorbidity Bonus" in note
