from config import db
from bson.objectid import ObjectId

class PatientModel:
    def __init__(self):
        self.collection = db.get_db().patients

    def create(self, data):
        data["resourceType"] = "Patient"
        return self.collection.insert_one(data).inserted_id

    def find_all(self):
        return list(self.collection.find())

    def find_by_id(self, id):
        try:
            return self.collection.find_one({"_id": ObjectId(id), "resourceType": "Patient"}) or \
                   self.collection.find_one({"id": id, "resourceType": "Patient"}) # handle custom string IDs
        except:
            return None
    
    def update(self, id, data):
        try:
            return self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        except:
            return None

    def delete(self, id):
        try:
            return self.collection.delete_one({"_id": ObjectId(id)})
        except:
            return None

class ConditionModel:
    def __init__(self):
        self.collection = db.get_db().conditions

    def create(self, data):
        data["resourceType"] = "Condition"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id):
        # Support both 'Patient/ID' and 'ID' formats
        queries = [
            {"subject.reference": f"Patient/{patient_id}"},
            {"subject.reference": patient_id}
        ]
        return list(self.collection.find({"$or": queries}))

    def find_all(self):
        return list(self.collection.find())

class ObservationModel:
    def __init__(self):
        self.collection = db.get_db().observations

    def create(self, data):
        data["resourceType"] = "Observation"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id):
         # Support both 'Patient/ID' and 'ID' formats
        queries = [
            {"subject.reference": f"Patient/{patient_id}"},
            {"subject.reference": patient_id}
        ]
        return list(self.collection.find({"$or": queries}))

class MedicationModel:
    def __init__(self):
        self.collection = db.get_db().medications

    def create(self, data):
        data["resourceType"] = "MedicationRequest"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id):
        # Support both 'Patient/ID' and 'ID' formats
        queries = [
            {"subject.reference": f"Patient/{patient_id}"},
            {"subject.reference": patient_id}
        ]
        return list(self.collection.find({"$or": queries}))

    def find_all(self):
        return list(self.collection.find())

class UserModel:
    def __init__(self):
        self.collection = db.get_db().users

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def find_by_username(self, username):
        return self.collection.find_one({"username": username})

    def find_by_patient_id(self, patient_id):
        return self.collection.find_one({"patientId": patient_id})

