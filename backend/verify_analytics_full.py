import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def print_result(test_name, success, details=""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}: {details}")

def verify_analytics():
    print("--- Verifying Analytics Endpoints ---")
    
    # 1. Population Level
    endpoints = [
        "population/disease-distribution",
        "population/disease-trends-by-age",
        "population/disease-trends-by-location",
        "population/vitals",
        "population/medications",
        "population/chronic-acute",
        "population/comorbidity"
    ]
    
    for ep in endpoints:
        try:
            resp = requests.get(f"{BASE_URL}/analytics/{ep}")
            if resp.status_code == 200:
                print_result(ep, True, f"Got {len(resp.json())} records")
            else:
                print_result(ep, False, f"Status {resp.status_code}")
        except Exception as e:
            print_result(ep, False, str(e))

    # 2. Patient Level
    # Need a valid patient ID. We can create one or fetch one.
    # Let's try to fetch all patients first
    try:
        # Assuming there's an endpoint to list patients or we rely on seed data.
        # Can use Admin Controller if available, but let's just create a dummy if we can't find one?
        # Actually, let's just pick one from the DB using python directly if needed, or assume seed data exists.
        # Since I can't interact with DB directly easily here without importing app code, 
        # I'll rely on the app running.
        # Let's try to "seed" via the endpoint if possible, or just guess logic.
        pass
    except:
        pass

    # Create a test patient via existing API if possible (Authentication needed?)
    # For now, let's assume the developer (me) will check the output of population stats above, 
    # which implies data exists if > 0.
    # To properly test Patient Risk, I need a patient ID.
    
    # Let's list patients via admin API (if accessible)
    # Or just hardcode logic if we know seed data.
    pass

if __name__ == "__main__":
    verify_analytics()
