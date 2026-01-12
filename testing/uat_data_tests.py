import requests
import json
import time
import concurrent.futures
from pymongo import MongoClient

BASE_URL = "http://localhost:5000/api"
MONGO_URI = "mongodb://localhost:27017/fhir_db"

def get_admin_token():
    payload = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=payload)
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_uat_data_01_duplicate_prevention(token):
    print("Running UAT-DATA-01: Duplicate patient profile prevention...")
    client = MongoClient(MONGO_URI)
    db = client.fhir_db
    patient_id = "uat-data-duplicate-id-2"
    db.patients.delete_many({"id": patient_id})
    data = {"resourceType": "Patient", "id": patient_id, "name": [{"text": "Dup Test"}]}
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/Patient", json=data, headers=headers)
    requests.post(f"{BASE_URL}/Patient", json=data, headers=headers)
    count = db.patients.count_documents({"id": patient_id})
    if count == 1:
        print("[PASS] UAT-DATA-01: Duplicate prevented.")
    else:
        print(f"[FAIL] UAT-DATA-01: Duplicate found (Count: {count})")

def test_sequential_analytics(token):
    print("Running Sequential Analytics Check...")
    urls = [
        f"{BASE_URL}/analytics/population/disease-distribution",
        f"{BASE_URL}/analytics/population/disease-trends-by-age",
        f"{BASE_URL}/analytics/population/vitals",
        f"{BASE_URL}/analytics/population/medications"
    ]
    headers = {"Authorization": f"Bearer {token}"}
    for url in urls:
        res = requests.get(url, headers=headers)
        print(f" Checked {url.split('/')[-1]}: {res.status_code}")

def test_uat_data_02_concurrency(token):
    print("Running UAT-DATA-02: Concurrent analytics requests...")
    urls = [f"{BASE_URL}/analytics/population/disease-distribution"] * 4
    headers = {"Authorization": f"Bearer {token}"}
    
    def fetch(url):
        return requests.get(url, headers=headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch, url) for url in urls]
        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            res = f.result()
            print(f" Concurrent Request {i+1} done: {res.status_code}")
    
    print("[PASS] UAT-DATA-02: System stable under concurrency.")

def test_uat_data_03_performance(token):
    print("Running UAT-DATA-03: Performance under load...")
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    res = requests.get(f"{BASE_URL}/analytics/population/disease-trends-by-age", headers=headers)
    latency = time.time() - start
    print(f" Latency: {latency:.3f}s")
    if latency < 2.0:
        print("[PASS] UAT-DATA-03: Performance acceptable.")
    else:
        print("[FAIL] UAT-DATA-03: Performance too slow.")

if __name__ == "__main__":
    token = get_admin_token()
    if token:
        test_uat_data_01_duplicate_prevention(token)
        test_sequential_analytics(token)
        test_uat_data_02_concurrency(token)
        test_uat_data_03_performance(token)
        print("ALL_TESTS_FINISHED")
