import pytest
import requests
from pymongo import MongoClient

BASE_URL = "http://localhost:5000/api"
MONGO_URI = "mongodb://localhost:27017/fhir_db"

@pytest.fixture(scope="session")
def api_base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def mongo_db():
    client = MongoClient(MONGO_URI)
    return client.fhir_db

@pytest.fixture(scope="session")
def admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    assert response.status_code == 200
    return response.json()["token"]

@pytest.fixture(scope="session", autouse=True)
def cleanup_db(mongo_db):
    """Clean up all test data starting with 'pytest-' prefix after the session."""
    yield
    # Cleanup Patients and related resources
    test_prefix = "pytest-"
    
    # Identify test patients
    test_patients = list(mongo_db.patients.find({"id": {"$regex": f"^{test_prefix}"}}))
    test_patient_ids = [p["id"] for p in test_patients]
    test_patient_refs = [f"Patient/{pid}" for pid in test_patient_ids]
    
    # Delete from all relevant collections
    mongo_db.patients.delete_many({"id": {"$regex": f"^{test_prefix}"}})
    mongo_db.conditions.delete_many({"subject.reference": {"$in": test_patient_refs}})
    mongo_db.observations.delete_many({"subject.reference": {"$in": test_patient_refs}})
    mongo_db.medications.delete_many({"subject.reference": {"$in": test_patient_refs}})
    mongo_db.risk_assessments.delete_many({"subject.reference": {"$in": test_patient_refs}})
    # Also cleanup clinical versions and history
    mongo_db.clinical_versions.delete_many({"patientId": {"$in": test_patient_ids}})
    mongo_db.history.delete_many({"originalId": {"$regex": f"^{test_prefix}"}})
    # Cleanup test users
    mongo_db.users.delete_many({"username": {"$regex": f"^{test_prefix}"}})

@pytest.fixture
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
