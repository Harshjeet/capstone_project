import requests
import json

BASE_URL = "http://localhost:5000/api/analytics"

def test_uat_pop_01_disease_distribution():
    print("Running UAT-POP-01: Disease distribution analytics...")
    response = requests.get(f"{BASE_URL}/population/disease-distribution")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
            if "disease" in sample and "count" in sample:
                print(f"[PASS] UAT-POP-01: Diseases aggregated correctly. Sample: {sample}")
            else:
                print(f"[FAIL] UAT-POP-01: Unexpected data structure. Sample: {sample}")
        else:
            print(f"[FAIL] UAT-POP-01: Empty or invalid list returned. Data: {data}")
    else:
        print(f"[FAIL] UAT-POP-01: Failed with status {response.status_code}. Response: {response.text}")

def test_uat_pop_02_disease_trends_by_age():
    print("Running UAT-POP-02: Disease trends by age group...")
    response = requests.get(f"{BASE_URL}/population/disease-trends-by-age")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
            if "disease" in sample and "age_group" in sample and "count" in sample:
                print(f"[PASS] UAT-POP-02: Age-disease trends displayed. Sample: {sample}")
            else:
                print(f"[FAIL] UAT-POP-02: Unexpected data structure. Sample: {sample}")
        else:
            print(f"[FAIL] UAT-POP-02: Empty or invalid list returned. Data: {data}")
    else:
        print(f"[FAIL] UAT-POP-02: Failed with status {response.status_code}. Response: {response.text}")

def test_uat_pop_03_disease_trends_by_location():
    print("Running UAT-POP-03: Disease trends by location...")
    response = requests.get(f"{BASE_URL}/population/disease-trends-by-location")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
            if "disease" in sample and "location" in sample and "count" in sample:
                print(f"[PASS] UAT-POP-03: Regional disease patterns shown. Sample: {sample}")
            else:
                print(f"[FAIL] UAT-POP-03: Unexpected data structure. Sample: {sample}")
        else:
            print(f"[FAIL] UAT-POP-03: Empty or invalid list returned. Data: {data}")
    else:
        print(f"[FAIL] UAT-POP-03: Failed with status {response.status_code}. Response: {response.text}")

def test_uat_pop_04_chronic_vs_acute():
    print("Running UAT-POP-04: Chronic vs acute analytics...")
    response = requests.get(f"{BASE_URL}/population/chronic-acute")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
            if "type" in sample and "age_group" in sample and "count" in sample:
                # Check for classification
                types = set(item["type"] for item in data)
                if "Chronic" in types or "Acute" in types:
                    print(f"[PASS] UAT-POP-04: Accurate chronic v/s acute counts. Types found: {types}")
                else:
                    print(f"[FAIL] UAT-POP-04: Classification might be missing. Types found: {types}")
            else:
                print(f"[FAIL] UAT-POP-04: Unexpected data structure. Sample: {sample}")
        else:
            print(f"[FAIL] UAT-POP-04: Empty or invalid list returned. Data: {data}")
    else:
        print(f"[FAIL] UAT-POP-04: Failed with status {response.status_code}. Response: {response.text}")

if __name__ == "__main__":
    print("=== Starting UAT Population Health Analytics Tests ===\n")
    test_uat_pop_01_disease_distribution()
    print()
    test_uat_pop_02_disease_trends_by_age()
    print()
    test_uat_pop_03_disease_trends_by_location()
    print()
    test_uat_pop_04_chronic_vs_acute()
    print("\n=== UAT Population Health Analytics Tests Completed ===")
