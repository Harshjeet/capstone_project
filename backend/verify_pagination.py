
import requests

BASE_URL = "http://localhost:5000/api"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_pagination(endpoint, name):
    print(f"--- Testing Pagination for {name} ---")
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Page 1
    res = requests.get(f"{BASE_URL}{endpoint}?page=1&limit=15", headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"[SUCCESS] Page 1 fetched. Total: {data['total']}, Page: {data['page']}, Total Pages: {data['total_pages']}")
        print(f"Items on page: {len(data['data'])}")
        
        if data['total_pages'] > 1:
            # Test Page 2
            res2 = requests.get(f"{BASE_URL}{endpoint}?page=2&limit=15", headers=headers)
            if res2.status_code == 200:
                print(f"[SUCCESS] Page 2 fetched. Items: {len(res2.json()['data'])}")
            else:
                print(f"[FAIL] Page 2 failed: {res2.status_code}")
    else:
        print(f"[FAIL] {name} failed: {res.status_code}, {res.text}")
    print()

if __name__ == "__main__":
    test_pagination("/admin/patients", "Patients")
    test_pagination("/admin/users", "Users")
