import requests
import time

BASE_URL = "http://localhost:5000"

def test_risk_score():
    print("\n--- Testing Risk Score ---")
    
    # 1. Login as Admin to get token (or existing user)
    # We use admin to get a token, but we need to register a user to test risk effectively
    # OR we can just use an existing patient if we know their ID.
    # Let's register a NEW specific high-risk user to be deterministic.
    
    reg_data = {
        "username": "risk_tester_99",
        "password": "password123",
        "patientDetails": {
            "firstName": "Risk", "lastName": "Tester",
            "gender": "male", "birthDate": "1945-01-01", # > 75 years old (+2 score)
            "mobile": "5555555555", "address": "123 Risk Ave, New York"
        },
        # Conditions: Diabetes (+1 general + 2 specific = 3), Heart Disease (+1 general + 2 specific = 3)
        # Total Conditions = 6. Age = 2. Total Score = 8 -> High
        "conditions": ["Diabetes", "Heart Disease"], 
        "observations": []
    }
    
    print("1. Registering High Risk Patient...")
    try:
        reg_res = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        if reg_res.status_code == 201:
            print("   Registration success.")
        elif reg_res.status_code == 400 and "exists" in reg_res.text:
            print("   User already exists, proceeding to login.")
        else:
            print(f"   Registration failed: {reg_res.status_code} {reg_res.text}")
            return
    except requests.exceptions.ConnectionError:
        print("   Connection refused. Ensure backend is running.")
        return

    print("2. Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "risk_tester_99", "password": "password123"})
    if login_res.status_code != 200:
        print(f"   Login failed: {login_res.text}")
        return
        
    p_data = login_res.json()
    token = p_data["token"]
    p_id = p_data["patientId"]
    print(f"   Logged in as Patient ID: {p_id}")
    
    print("3. Fetching Risk Score...")
    headers = {"Authorization": f"Bearer {token}"}
    risk_res = requests.get(f"{BASE_URL}/Patient/{p_id}/risk", headers=headers)
    
    if risk_res.status_code == 200:
        data = risk_res.json()
        print(f"   Risk Score: {data['risk_score']}")
        print(f"   Risk Label: {data['risk_label']}")
        
        if data['risk_label'] == "High" and data['risk_score'] >= 5:
             print("   SUCCESS: High Risk correctly identified.")
        else:
             print(f"   FAILURE: Expected High Risk (>=5), got {data['risk_label']} ({data['risk_score']})")
    else:
        print(f"   Error fetching risk: {risk_res.status_code} {risk_res.text}")

def test_analytics_filter():
    print("\n--- Testing Analytics Filter ---")
    # Login as admin for analytics
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json().get("token")
    if not token:
        print("   Admin login failed (check if admin exists)")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. No Filter
    print("1. Fetching Trends (No Filter)...")
    res1 = requests.get(f"{BASE_URL}/stats/trends", headers=headers)
    count1 = sum(item['value'] for item in res1.json().get('top_conditions', []))
    print(f"   Matches found: {count1}")
    
    # 2. Location Filter (New York)
    # The user we just created has address "New York".
    print("2. Fetching Trends (Location='New York')...")
    res2 = requests.get(f"{BASE_URL}/stats/trends?location=New York", headers=headers)
    if res2.status_code == 200:
        data = res2.json()
        count2 = sum(item['value'] for item in data.get('top_conditions', []))
        print(f"   Matches found in NY: {count2}")
        if count2 > 0:
            print("   SUCCESS: Filter returned results.")
        else:
             print("   WARNING: Filter returned 0 results (expected at least the new user's conditions).")
    else:
        print(f"   Filter request failed: {res2.text}")

if __name__ == "__main__":
    test_risk_score()
    test_analytics_filter()
