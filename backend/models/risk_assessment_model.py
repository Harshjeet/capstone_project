from config import db
from bson.objectid import ObjectId

class RiskAssessmentModel:
    def __init__(self):
        self.collection = db.get_db().risk_assessments

    def create(self, data):
        data["resourceType"] = "RiskAssessment"
        return self.collection.insert_one(data).inserted_id

    def find_latest_by_patient(self, patient_id):
        # Sort by date (assuming we store 'occurrenceDateTime' or created timestamp)
        return self.collection.find_one(
            {"subject.reference": f"Patient/{patient_id}"},
            sort=[("_id", -1)]
        )

    def find_all(self):
        return list(self.collection.find())
