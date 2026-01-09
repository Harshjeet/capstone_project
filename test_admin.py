import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def run_tests():
    print("Testing Admin API...")
    
    # 1. Login as Admin
    print("\n1. Login as Admin")
    try:
        res = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "admin", 
            "password": "adminpassword123"
        })
        if res.status_code != 200:
            print(f"FAILED: Login failed. {res.text}")
            return
        token = res.json().get("token")
        print("LOGIN SUCCESS. Token received.")
    except Exception as e:
        print(f"FAILED: Connection error. {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Plans (CRUD)
    print("\n2. Get Insurance Plans")
    res = requests.get(f"{BASE_URL}/admin/plans", headers=headers)
    if res.status_code == 200:
        plans = res.json()
        print(f"SUCCESS. Found {len(plans)} plans.")
    else:
        print(f"FAILED. {res.status_code} {res.text}")

    # 3. Create Plan
    print("\n3. Create New Plan")
    new_plan = {
        "id": "test-plan",
        "name": "Test Plan",
        "cost": 999,
        "description": "A test plan",
        "coverage": ["Test Condition"]
    }
    res = requests.post(f"{BASE_URL}/admin/plans", json=new_plan, headers=headers)
    if res.status_code == 201:
        created_id = res.json().get("id")
        print("SUCCESS. Plan created.")
    else:
        print(f"FAILED. {res.status_code} {res.text}")
        return

    # 4. Get Patients
    print("\n4. Get All Patients")
    res = requests.get(f"{BASE_URL}/admin/patients", headers=headers)
    if res.status_code == 200:
        patients = res.json()
        print(f"SUCCESS. Found {len(patients)} patients.")
    else:
        print(f"FAILED. {res.status_code} {res.text}")

    # 5. Get Logs
    print("\n5. Get System Logs")
    res = requests.get(f"{BASE_URL}/admin/system/logs", headers=headers)
    if res.status_code == 200:
        print("SUCCESS. Logs retrieved.")
    else:
        print(f"FAILED. {res.status_code} {res.text}")

    # 6. Delete Test Plan
    print("\n6. Cleaning up (Delete Test Plan)")
    # We need to find the plan _id to delete it, but the create returned it.
    # Actually the controller returns {"id": str(new_id)}
    if 'created_id' in locals():
        res = requests.delete(f"{BASE_URL}/admin/plans/{created_id}", headers=headers)
        if res.status_code == 200:
            print("SUCCESS. Test plan deleted.")
        else:
            print(f"FAILED Delete. {res.status_code} {res.text}")

if __name__ == "__main__":
    run_tests()
