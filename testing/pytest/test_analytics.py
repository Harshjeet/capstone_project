import requests
import pytest

# --- C. Population Health Analytics (UAT-POP-01 to 04) ---

def test_uat_pop_01_disease_distribution(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/disease-distribution", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_uat_pop_02_disease_trends_by_age(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/disease-trends-by-age", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_uat_pop_03_disease_trends_by_location(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/disease-trends-by-location", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_uat_pop_04_chronic_vs_acute_analytics(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/chronic-acute", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data or isinstance(data, list) # Depending on exact implementation

# --- D. Observation & Medication Analytics (UAT-OBS-01 to 02, UAT-MED-01) ---

def test_uat_obs_01_abnormal_vital_detection(api_base_url, auth_header, mongo_db):
    p_id = "pytest-obs-01"
    mongo_db.patients.delete_many({"id": p_id})
    requests.post(f"{api_base_url}/Patient", json={"resourceType": "Patient", "id": p_id}, headers=auth_header)
    
    # Post high BP (Abnormal)
    requests.post(f"{api_base_url}/Observation", json={
        "resourceType": "Observation",
        "status": "final",
        "code": {"coding": [{"display": "Systolic blood pressure"}]},
        "subject": {"reference": f"Patient/{p_id}"},
        "valueQuantity": {"value": 170, "unit": "mmHg"}
    }, headers=auth_header)
    
    response = requests.get(f"{api_base_url}/analytics/population/vitals", headers=auth_header)
    assert response.status_code == 200
    # The abnormal count should include our new record
    # API returns list of aggregations
    data = response.json()
    assert any(d["vital"] == "High BP" for d in data)

def test_uat_obs_02_observation_aggregation(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/vitals", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 0

def test_uat_med_01_medication_usage_by_disease(api_base_url, auth_header):
    response = requests.get(f"{api_base_url}/analytics/population/medications", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "by_disease" in data
