
import os
import sys
import datetime
from bson import ObjectId

# Ensure we can import from backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from config import db
from models.models import ConditionModel, PatientModel

def verify_robust_data_retrieval():
    print("🚀 Starting Robust Data Retrieval Verification...")
    condition_model = ConditionModel()
    patient_model = PatientModel()
    
    # 1. Create a test patient
    p_data = {
        "resourceType": "Patient",
        "name": [{"text": "Robust Test Patient"}]
    }
    patient_id = patient_model.create(p_data)
    patient_id_str = str(patient_id)
    print(f"✅ Created Patient: {patient_id_str}")
    
    try:
        # 2. Test Case: mixed case status and Patient/ prefix
        c1_data = {
            "resourceType": "Condition",
            "clinicalStatus": {"text": "active"}, # Lowercase
            "code": {"text": "Test Condition 1"},
            "subject": {"reference": f"Patient/{patient_id_str}"}
        }
        condition_model.create(c1_data)
        
        # 3. Test Case: coding.code status and no prefix
        c2_data = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [{"code": "ACTIVE"}] # Uppercase
            },
            "code": {"text": "Test Condition 2"},
            "subject": {"reference": patient_id_str} # No prefix
        }
        condition_model.create(c2_data)
        
        print("🔍 Querying with 'Active' (Mixed case)...")
        results = condition_model.find_by_patient(patient_id_str, status="Active")
        
        print(f"Found {len(results)} results.")
        for r in results:
            print(f" - {r['code']['text']} (Status: {r.get('clinicalStatus', {})})")
            
        assert len(results) == 2, f"Expected 2 results, found {len(results)}"
        print("✅ VERIFICATION SUCCESSFUL: Robust query logic handles schema and case variations.")
        
    finally:
        # Cleanup
        db.get_db().patients.delete_one({"_id": patient_id})
        db.get_db().conditions.delete_many({"subject.reference": {"$in": [f"Patient/{patient_id_str}", patient_id_str]}})
        print("🧹 Cleanup complete.")

if __name__ == "__main__":
    verify_robust_data_retrieval()
