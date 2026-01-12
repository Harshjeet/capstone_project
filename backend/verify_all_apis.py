
import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

class HealthAIVerifier:
    def __init__(self):
        self.admin_token = None
        self.patient_token = None
        self.patient_id = None
        self.results = []
        self.ts = int(time.time())
        self.test_last_name = f"Verifier_{self.ts}"

    def log_result(self, endpoint, method, status, success):
        icon = "✅" if success else "❌"
        self.results.append({
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "success": success,
            "icon": icon
        })
        print(f"{icon} {method} {endpoint} -> {status}")

    def test_endpoint(self, endpoint, method="GET", payload=None, token=None):
        url = f"{BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            if method == "GET":
                res = requests.get(url, headers=headers)
            elif method == "POST":
                res = requests.post(url, headers=headers, json=payload)
            
            success = res.status_code in [200, 201]
            self.log_result(endpoint, method, res.status_code, success)
            return res
        except Exception as e:
            self.log_result(endpoint, method, str(e), False)
            return None

    def setup_accounts(self):
        print("\n🔑 SETUP: Preparing test environment...")
        
        # 1. Admin Login
        res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
        if res.status_code == 200:
            self.admin_token = res.json().get("token")
        
        # 2. Register & Login Patient
        username = f"api_test_{self.ts}"
        register_payload = {
            "username": username,
            "password": "password123",
            "patientDetails": {
                "firstName": "API", "lastName": self.test_last_name, "gender": "other",
                "birthDate": "1995-05-05", "mobile": "999-0000", "address": "Verifier St"
            },
            "conditions": [],
            "vitals": {}
        }
        reg_res = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
        if reg_res.status_code == 201:
            login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": "password123"})
            if login_res.status_code == 200:
                self.patient_token = login_res.json().get("token")
                
                # Find patient ID
                search_url = f"{BASE_URL}/admin/patients?search={self.test_last_name}"
                all_patients = requests.get(search_url, headers={"Authorization": f"Bearer {self.admin_token}"}).json()
                for p in all_patients.get("data", []):
                    if self.test_last_name in p.get("name", ""):
                        self.patient_id = p["id"]
                        break
                
                # 3. Create Consent (Required for Recommendation API)
                consent_payload = {
                    "resourceType": "Consent",
                    "status": "active",
                    "scope": {"text": "Research"},
                    "category": [{"text": "Privacy"}],
                    "patient": {"reference": f"Patient/{self.patient_id}"}
                }
                requests.post(f"{BASE_URL}/Consent", headers={"Authorization": f"Bearer {self.patient_token}"}, json=consent_payload)

        return bool(self.admin_token and self.patient_token and self.patient_id)

    def run_all(self):
        if not self.setup_accounts(): 
            print("🛑 ABORTING: Setup incomplete.")
            return

        print("\n🚀 STARTING COMPREHENSIVE API VERIFICATION (20 OPERATIONS) 🚀\n")

        # --- PUBLIC ---
        self.test_endpoint("/registration-data", "GET")
        self.test_endpoint("/auth/login", "POST", payload={"username": "admin", "password": "admin123"})
        self.test_endpoint("/auth/register", "POST", payload={
             "username": f"user_{self.ts}_alt", "password": "123",
             "patientDetails": {"firstName": "Alt", "lastName": "User", "mobile": "0", "address": "x"},
             "vitals": {}
        })

        # --- FHIR ---
        self.test_endpoint("/Patient", "GET", token=self.admin_token)
        self.test_endpoint("/Condition", "GET", token=self.admin_token)
        self.test_endpoint("/Patient", "POST", token=self.admin_token, payload={"resourceType": "Patient", "name": [{"text": "Doc Test"}]})
        # Fix Condition payload
        self.test_endpoint("/Condition", "POST", token=self.admin_token, payload={
            "resourceType": "Condition", 
            "clinicalStatus": {"text": "Active"},
            "code": {"text": "Fever"}, 
            "subject": {"reference": f"Patient/{self.patient_id}"}
        })

        # --- ADMIN ---
        self.test_endpoint("/admin/patients", "GET", token=self.admin_token)
        self.test_endpoint("/admin/users", "GET", token=self.admin_token)
        self.test_endpoint("/admin/plans", "GET", token=self.admin_token)
        self.test_endpoint("/admin/plans", "POST", token=self.admin_token, payload={"name": "API Spec Plan", "provider": "Verify", "type": "Gold"})
        self.test_endpoint("/admin/stats/risk-distribution", "GET", token=self.admin_token)
        self.test_endpoint(f"/admin/patients/{self.patient_id}/fhir", "GET", token=self.admin_token)

        # --- PATIENT SELF SERVICE ---
        self.test_endpoint(f"/Patient/{self.patient_id}/clinical-update", "POST", token=self.patient_token, payload={
            "conditions": [], "vitals": {"systolic": 120, "diastolic": 80}
        })
        self.test_endpoint(f"/Patient/{self.patient_id}/clinical-history", "GET", token=self.patient_token)
        self.test_endpoint(f"/Patient/{self.patient_id}/risk", "GET", token=self.patient_token)
        self.test_endpoint(f"/recommendation/{self.patient_id}", "POST", token=self.patient_token)

        # --- POPULATION ANALYTICS ---
        self.test_endpoint("/analytics/population/medications", "GET", token=self.admin_token)
        self.test_endpoint("/analytics/population/vitals", "GET", token=self.admin_token)
        self.test_endpoint("/analytics/population/disease-distribution", "GET", token=self.admin_token)

        self.print_summary()

    def print_summary(self):
        print("\n" + "="*75)
        print(f"{'ENDPOINT':<55} | {'METHOD':<6} | {'STATUS':<6}")
        print("-" * 75)
        success_count = 0
        for res in self.results:
            endpoint_display = res["endpoint"][:52] + "..." if len(res["endpoint"]) > 55 else res["endpoint"]
            print(f"{endpoint_display:<55} | {res['method']:<6} | {res['status']:<6} {res['icon']}")
            if res["success"]: success_count += 1
        
        print("-" * 75)
        print(f"TOTAL: {len(self.results)} Operations Verified")
        print(f"PASSED: {success_count} / {len(self.results)}")
        print("="*75)

if __name__ == "__main__":
    verifier = HealthAIVerifier()
    verifier.run_all()
