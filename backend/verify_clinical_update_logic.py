
import requests
import time

BASE_URL = "http://localhost:5000/api"

def test_clinical_update_sync():
    ts = int(time.time())
    username = f"sync_test_v3_{ts}"
    print(f"🚀 Starting Clinical Sync Test for {username}")

    # 1. Register with high-weight conditions
    reg_payload = {
        "username": username,
        "password": "123",
        "patientDetails": {"firstName": "Sync", "lastName": "Tester", "birthDate": "1990-01-01"},
        "conditions": ["Essential Hypertension", "Type 2 Diabetes"], # High risk combo + comorbidity
        "medications": ["Aspirin", "Metformin"],
        "vitals": {"systolic": "160"} # High BP
    }
    requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    
    # 2. Login
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": "123"}).json()
    token = login_res["token"]
    pid = login_res["patientId"]
    headers = {"Authorization": f"Bearer {token}"}

    def get_dash_state():
        risk = requests.get(f"{BASE_URL}/Patient/{pid}/risk", headers=headers).json()
        conds = requests.get(f"{BASE_URL}/Condition?patient={pid}", headers=headers).json()
        meds = requests.get(f"{BASE_URL}/Medication?patient={pid}", headers=headers).json()
        return risk["risk_score"], [c["code"]["text"] for c in conds], [m.get("medication", {}).get("concept", {}).get("text") or m.get("medicationCodeableConcept", {}).get("text") for m in meds]

    # Initial Check (Should be High Score)
    score1, conds1, meds1 = get_dash_state()
    print(f"Initial: Score={score1}, Conds={conds1}, Meds={meds1}")

    # 3. Update (Clear everything to a healthy state)
    update_payload = {
        "conditions": ["Acne Vulgaris"], # Non high-risk
        "medications": ["Multivitamin"],
        "vitals": {"systolic": "120"} # Normal BP
    }
    requests.post(f"{BASE_URL}/Patient/{pid}/clinical-update", headers=headers, json=update_payload)
    
    # Final Check (Should be Low Score)
    score2, conds2, meds2 = get_dash_state()
    print(f"Updated: Score={score2}, Conds={conds2}, Meds={meds2}")
    
    # Assertions
    assert "Essential Hypertension" not in conds2
    assert "Acne Vulgaris" in conds2
    assert "Aspirin" not in meds2
    assert "Multivitamin" in meds2
    assert score2 < score1, f"Risk score should have decreased (from {score1} to {score2})"
    
    print("✅ VERIFICATION SUCCESSFUL: Dashboard and Risk correctly synchronized and filtered.")

if __name__ == "__main__":
    test_clinical_update_sync()
