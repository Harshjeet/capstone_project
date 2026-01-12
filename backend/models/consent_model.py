from config import db
from bson.objectid import ObjectId

class ConsentModel:
    def __init__(self):
        self.collection = db.get_db().consents

    def create(self, data):
        data["resourceType"] = "Consent"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id):
        # Check active consents for data access
        return self.collection.find_one({
            "patient.reference": f"Patient/{patient_id}",
            "status": "active"
        })

    def find_all(self):
        return list(self.collection.find())
