from config import db
from bson.objectid import ObjectId

class CoverageModel:
    def __init__(self):
        self.collection = db.get_db().coverage

    def create(self, data):
        data["resourceType"] = "Coverage"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id):
        return list(self.collection.find({"beneficiary.reference": f"Patient/{patient_id}"}))

    def update(self, coverage_id, data):
        return self.collection.update_one({"_id": ObjectId(coverage_id)}, {"$set": data})

    def delete(self, coverage_id):
        return self.collection.delete_one({"_id": ObjectId(coverage_id)})

