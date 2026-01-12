import requests
import pytest
import time
import concurrent.futures

def test_uat_data_01_duplicate_patient_profiles(api_base_url, auth_header, mongo_db):
    p_id = "pytest-data-01-dup"
    mongo_db.patients.delete_many({"id": p_id})
    data = {"resourceType": "Patient", "id": p_id, "name": [{"text": "Dup Stability Test"}]}
    
    # Concurrent ingestion to test race conditions
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(requests.post, f"{api_base_url}/Patient", json=data, headers=auth_header) for _ in range(5)]
        for f in futures: f.result()
    
    assert mongo_db.patients.count_documents({"id": p_id}) == 1

def test_uat_data_02_concurrent_analytics_requests(api_base_url, auth_header):
    # Simulate multiple admin users hitting analytics
    analytics_urls = [
        f"{api_base_url}/analytics/population/disease-distribution",
        f"{api_base_url}/analytics/population/vitals",
        f"{api_base_url}/analytics/population/medications"
    ] * 3
    
    def hit_analytics(url):
        return requests.get(url, headers=auth_header)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(hit_analytics, url) for url in analytics_urls]
        for f in concurrent.futures.as_completed(futures):
            assert f.result().status_code == 200

def test_uat_data_03_performance_under_load(api_base_url, auth_header):
    # Performance check for a relatively heavy query
    start = time.time()
    response = requests.get(f"{api_base_url}/analytics/population/disease-trends-by-age", headers=auth_header)
    duration = time.time() - start
    
    assert response.status_code == 200
    # Acceptance criteria: within acceptable time (e.g. < 2 seconds for this dataset size)
    assert duration < 2.0
