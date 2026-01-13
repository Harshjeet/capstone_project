import requests
import pytest

def test_uat_auth_01_valid_login(api_base_url):
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{api_base_url}/auth/login", json=payload)
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["role"] == "admin"

def test_uat_auth_02_role_based_access(api_base_url, auth_header, mongo_db):
    # Admin access check
    resp_admin = requests.get(f"{api_base_url}/admin/patients", headers=auth_header)
    assert resp_admin.status_code == 200
    
    # Patient access check - Create a unique test patient and user
    p_id = "pytest-auth-p"
    user_p = "pytest-user-p"
    mongo_db.patients.delete_many({"id": p_id})
    mongo_db.users.delete_many({"username": user_p})
    
    requests.post(f"{api_base_url}/Patient", json={"resourceType": "Patient", "id": p_id}, headers=auth_header)
    # Mock user creation manually for testing patient login
    mongo_db.users.insert_one({"username": user_p, "password": "123", "role": "patient", "patientId": p_id})
    
    p_login = {"username": user_p, "password": "123"}
    p_res = requests.post(f"{api_base_url}/auth/login", json=p_login)
    assert p_res.status_code == 200
    
    p_token = p_res.json()["token"]
    p_headers = {"Authorization": f"Bearer {p_token}"}
    
    # Patient should see their own risk, but NOT admin stats
    resp_p_data = requests.get(f"{api_base_url}/analytics/patient/{p_id}/risk", headers=p_headers)
    assert resp_p_data.status_code == 200
    
    resp_p_admin = requests.get(f"{api_base_url}/admin/patients", headers=p_headers)
    assert resp_p_admin.status_code == 403

def test_uat_auth_03_invalid_login(api_base_url):
    payload = {"username": "admin", "password": "wrong-password"}
    response = requests.post(f"{api_base_url}/auth/login", json=payload)
    assert response.status_code == 401
    assert "error" in response.json()

def test_uat_auth_04_unauthorized_access(api_base_url):
    # No token access
    response = requests.get(f"{api_base_url}/admin/patients")
    assert response.status_code == 401
