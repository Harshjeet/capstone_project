import requests
import sys

BASE_URL = "http://localhost:5000/api"

def test_age_filter():
    print("\n--- Testing Analytics Age Filter ---")
    
    # 1. Login as Admin
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if login_res.status_code != 200:
        print("Login failed")
        return
        
    token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test No Filter
    print("1. Fetching Trends (No Filter)...")
    res1 = requests.get(f"{BASE_URL}/stats/trends", headers=headers)
    count1 = sum(item['value'] for item in res1.json().get('top_conditions', []))
    print(f"   Matches found: {count1}")
    
    # 3. Test Age Filter (Young Patients 0-30)
    print("2. Fetching Trends (Age 0-30)...")
    res2 = requests.get(f"{BASE_URL}/stats/trends?age_min=0&age_max=30", headers=headers)
    if res2.status_code == 200:
        data = res2.json()
        count2 = sum(item['value'] for item in data.get('top_conditions', []))
        print(f"   Matches found (Age 0-30): {count2}")
        
    # 4. Test Age Filter (Old Patients 60-100)
    print("3. Fetching Trends (Age 60-100)...")
    res3 = requests.get(f"{BASE_URL}/stats/trends?age_min=60&age_max=100", headers=headers)
    if res3.status_code == 200:
        data = res3.json()
        count3 = sum(item['value'] for item in data.get('top_conditions', []))
        print(f"   Matches found (Age 60-100): {count3}")

    if count1 >= count2 and count1 >= count3:
        print("   SUCCESS: Filter subsets data correctly.")
    else:
        print("   FAILURE: Filtered data larger than total?")

if __name__ == "__main__":
    test_age_filter()
