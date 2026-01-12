import sys
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

# Add backend directory to sys.path to import services/models
sys.path.append(os.path.abspath('/home/harsh/Desktop/file/backend'))

from config import db
try:
    db.connect()
    client = db.client
    db_conn = db.get_db()
except:
    client = MongoClient("mongodb://localhost:27017")
    db_conn = client.healthcare_db

def calculate_age(dob_str):
    if not dob_str: return None
    try:
        # Try multiple date formats if needed, but FHIR is usually YYYY-MM-DD
        if isinstance(dob_str, datetime):
            dob = dob_str
        else:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
        return (datetime.now() - dob).days // 365
    except: return None

def get_risk_label(patient, conditions, observations, meds):
    score = 0
    weights = {"age": 30, "conditions": 40, "observations": 20, "medications": 10}
    
    # 1. Age
    age = calculate_age(patient.get("birthDate"))
    if age is not None:
        factor = 0
        if age > 60: factor = 1.0
        elif age > 45: factor = 0.66
        elif age > 30: factor = 0.33
        else: factor = 0.16
        score += factor * weights["age"]

    # 2. Conditions
    high_risk_keywords = ["diabetes", "hypertension", "heart", "cancer", "stroke", "asthma"]
    cond_raw = 0
    for c in conditions:
        text = c.get("code", {}).get("text", "").lower()
        if any(hr in text for hr in high_risk_keywords):
            cond_raw += 1.0
        else:
            cond_raw += 0.3
    score += min(cond_raw * 15, weights["conditions"])

    # 3. Observations
    obs_raw = 0
    for o in observations:
        text = o.get("code", {}).get("text", "").lower()
        val_obj = o.get("valueQuantity", {})
        val = val_obj.get("value", 0) if isinstance(val_obj, dict) else 0
        
        if (("blood pressure" in text or "systolic" in text) and val > 140) or \
           (("glucose" in text or "sugar" in text) and val > 180):
            obs_raw += 0.5
    score += min(obs_raw * 20, weights["observations"])

    # 4. Meds
    score += min(len(meds) * 0.5 * 10, weights["medications"])

    if score > 100: score = 100
    if score <= 30: return "Low"
    if score <= 60: return "Medium"
    return "High"

def audit():
    print("--- Analytics Audit ---")
    
    patients = list(db_conn.patients.find())
    print(f"Total Patients: {len(patients)}")
    
    risk_dist = {"Low": 0, "Medium": 0, "High": 0}
    total_conditions = 0
    abnormal_vitals = 0
    
    for p in patients:
        p_id = str(p["_id"])
        fhir_id = p.get("id")
        
        cond_query = {"$or": [
            {"subject.reference": f"Patient/{p_id}"},
            {"subject.reference": f"Patient/{fhir_id}"} if fhir_id else {"subject.reference": None}
        ]}
        conditions = list(db_conn.conditions.find(cond_query))
        total_conditions += len(conditions)
        
        obs_query = {"$or": [
            {"subject.reference": f"Patient/{p_id}"},
            {"subject.reference": f"Patient/{fhir_id}"} if fhir_id else {"subject.reference": None}
        ]}
        obs = list(db_conn.observations.find(obs_query))
        for o in obs:
            text = o.get("code", {}).get("text", "").lower()
            val_obj = o.get("valueQuantity", {})
            val = val_obj.get("value", 0) if isinstance(val_obj, dict) else 0
            
            if (("blood pressure" in text or "systolic" in text) and val > 140) or \
               (("glucose" in text or "sugar" in text) and val > 180):
                abnormal_vitals += 1
        
        med_query = {"$or": [
            {"subject.reference": f"Patient/{p_id}"},
            {"subject.reference": f"Patient/{fhir_id}"} if fhir_id else {"subject.reference": None}
        ]}
        meds = list(db_conn.medications.find(med_query))
        
        label = get_risk_label(p, conditions, obs, meds)
        risk_dist[label] += 1

    print(f"Risk Distribution: {risk_dist}")
    print(f"Total Active Conditions: {total_conditions}")
    print(f"Total Abnormal Vitals: {abnormal_vitals}")
    
    # Prevalent Conditions
    pipeline = [
        {"$group": {"_id": "$code.text", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    prevalent = list(db_conn.conditions.aggregate(pipeline))
    print("Prevalent Conditions:")
    for c in prevalent:
        print(f"  - {c['_id']}: {c['count']}")

if __name__ == "__main__":
    audit()
