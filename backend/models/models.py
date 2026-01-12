from config import db
from bson.objectid import ObjectId

class PatientModel:
    def __init__(self):
        self.collection = db.get_db().patients

    def create(self, data):
        data["resourceType"] = "Patient"
        if "id" in data:
            # Atomic upsert to prevent duplicates under concurrency
            res = self.collection.update_one(
                {"id": data["id"], "resourceType": "Patient"},
                {"$setOnInsert": data},
                upsert=True
            )
            if res.upserted_id:
                return res.upserted_id
            # If not upserted, it means it already exists
            existing = self.collection.find_one({"id": data["id"], "resourceType": "Patient"})
            return existing["_id"]
        
        return self.collection.insert_one(data).inserted_id

    def find_all(self):
        return list(self.collection.find())

    def find_paginated(self, page, limit, search=None):
        skip = (page - 1) * limit
        query = {"resourceType": "Patient"}
        if search:
            query["name.text"] = {"$regex": search, "$options": "i"}
        
        items = list(self.collection.find(query).skip(skip).limit(limit))
        total = self.collection.count_documents(query)
        return items, total

    def find_by_id(self, id):
        # Try finding by ObjectId first
        try:
            if ObjectId.is_valid(id):
                doc = self.collection.find_one({"_id": ObjectId(id), "resourceType": "Patient"})
                if doc: return doc
        except:
            pass
            
        # Fallback to custom string ID (e.g., "p001")
        return self.collection.find_one({"id": id, "resourceType": "Patient"})
    
    def update(self, id, data):
        try:
            # Handle both ObjectId and string ID
            if ObjectId.is_valid(id):
                return self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
            return self.collection.update_one({"id": id}, {"$set": data})
        except:
            return None

    def delete(self, id):
        try:
            if ObjectId.is_valid(id):
                return self.collection.delete_one({"_id": ObjectId(id)})
            return self.collection.delete_one({"id": id})
        except:
            return None

class HistoryModel:
    def __init__(self):
        self.collection = db.get_db().clinical_history

    def create(self, original_id, resource_type, data):
        import datetime
        history_entry = {
            "original_id": str(original_id),
            "resourceType": resource_type,
            "data": data,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        return self.collection.insert_one(history_entry).inserted_id

    def find_by_original_id(self, original_id):
        return list(self.collection.find({"original_id": str(original_id)}).sort("timestamp", -1))

class ClinicalVersionModel:
    def __init__(self):
        self.collection = db.get_db().clinical_versions

    def create(self, patient_id, conditions, vitals, version_num, medications=None):
        import datetime
        snapshot = {
            "patientId": str(patient_id),
            "conditions": conditions,
            "vitals": vitals,
            "medications": medications or [],
            "versionNum": version_num,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        return self.collection.insert_one(snapshot).inserted_id

    def get_latest(self, patient_id):
        return self.collection.find_one({"patientId": str(patient_id)}, sort=[("versionNum", -1)])

    def get_history(self, patient_id):
        return list(self.collection.find({"patientId": str(patient_id)}).sort("versionNum", -1))

class ConditionModel:
    def __init__(self):
        self.collection = db.get_db().conditions

    def create(self, data):
        if "id" in data:
            existing = self.collection.find_one({"id": data["id"], "resourceType": "Condition"})
            if existing:
                return existing["_id"]
        data["resourceType"] = "Condition"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id, status=None):
        # Support both 'Patient/ID' and 'ID' formats
        patient_refs = [
            f"Patient/{patient_id}",
            str(patient_id),
            patient_id.replace("Patient/", "") if isinstance(patient_id, str) and patient_id.startswith("Patient/") else patient_id
        ]
        
        query = {"subject.reference": {"$in": patient_refs}}
        
        if status:
            status_regex = {"$regex": f"^{status}$", "$options": "i"}
            # Condition specific status fields
            query = {
                "$and": [
                    {"subject.reference": {"$in": patient_refs}},
                    {"$or": [
                        {"clinicalStatus.text": status_regex},
                        {"clinicalStatus.coding.code": status_regex}
                    ]}
                ]
            }
        return list(self.collection.find(query))

    def find_all(self):
        return list(self.collection.find())

    def find_by_id(self, id):
        try:
            if ObjectId.is_valid(id):
                return self.collection.find_one({"_id": ObjectId(id)})
            return self.collection.find_one({"id": id})
        except:
            return None

    def update(self, id, data):
        try:
            if ObjectId.is_valid(id):
                return self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
            return self.collection.update_one({"id": id}, {"$set": data})
        except:
            return None

    def update_many(self, filter_query, update_data):
        return self.collection.update_many(filter_query, {"$set": update_data})

    def delete(self, id):
        try:
            if ObjectId.is_valid(id):
                return self.collection.delete_one({"_id": ObjectId(id)})
            return self.collection.delete_one({"id": id})
        except:
            return None

class ObservationModel:
    def __init__(self):
        self.collection = db.get_db().observations

    def create(self, data):
        if "id" in data:
            existing = self.collection.find_one({"id": data["id"], "resourceType": "Observation"})
            if existing:
                return existing["_id"]
        data["resourceType"] = "Observation"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id, status=None):
         # Support both 'Patient/ID' and 'ID' formats
        patient_refs = [
            f"Patient/{patient_id}",
            str(patient_id),
            patient_id.replace("Patient/", "") if isinstance(patient_id, str) and patient_id.startswith("Patient/") else patient_id
        ]
        
        query = {"subject.reference": {"$in": patient_refs}}
        
        if status:
            query = {
                "$and": [
                    {"subject.reference": {"$in": patient_refs}},
                    {"status": {"$regex": f"^{status}$", "$options": "i"}}
                ]
            }
        return list(self.collection.find(query))

    def find_all(self):
        return list(self.collection.find())

    def find_by_id(self, id):
        try:
            if ObjectId.is_valid(id):
                return self.collection.find_one({"_id": ObjectId(id)})
            return self.collection.find_one({"id": id})
        except:
            return None

    def update(self, id, data):
        try:
            if ObjectId.is_valid(id):
                return self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
            return self.collection.update_one({"id": id}, {"$set": data})
        except:
            return None

    def update_many(self, filter_query, update_data):
        return self.collection.update_many(filter_query, {"$set": update_data})

class MedicationModel:
    def __init__(self):
        self.collection = db.get_db().medications

    def create(self, data):
        if "id" in data:
            existing = self.collection.find_one({"id": data["id"], "resourceType": "MedicationRequest"})
            if existing:
                return existing["_id"]
        data["resourceType"] = "MedicationRequest"
        return self.collection.insert_one(data).inserted_id

    def find_by_patient(self, patient_id, status=None):
        # Support both 'Patient/ID' and 'ID' formats
        patient_refs = [
            f"Patient/{patient_id}",
            str(patient_id),
            patient_id.replace("Patient/", "") if isinstance(patient_id, str) and patient_id.startswith("Patient/") else patient_id
        ]
        
        query = {"subject.reference": {"$in": patient_refs}}
        
        if status:
            query = {
                "$and": [
                    {"subject.reference": {"$in": patient_refs}},
                    {"status": {"$regex": f"^{status}$", "$options": "i"}}
                ]
            }
        return list(self.collection.find(query))

    def find_all(self):
        return list(self.collection.find())

    def find_by_id(self, id):
        try:
            if ObjectId.is_valid(id):
                return self.collection.find_one({"_id": ObjectId(id)})
            return self.collection.find_one({"id": id})
        except:
            return None

    def update(self, id, data):
        try:
            if ObjectId.is_valid(id):
                return self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
            return self.collection.update_one({"id": id}, {"$set": data})
        except:
            return None

    def update_many(self, filter_query, update_data):
        return self.collection.update_many(filter_query, {"$set": update_data})

class UserModel:
    def __init__(self):
        self.collection = db.get_db().users

    def create(self, data):
        return self.collection.insert_one(data).inserted_id

    def find_all(self):
        return list(self.collection.find())

    def find_paginated(self, page, limit, search=None):
        skip = (page - 1) * limit
        query = {}
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        items = list(self.collection.find(query).skip(skip).limit(limit))
        total = self.collection.count_documents(query)
        return items, total

    def find_by_username(self, username):
        return self.collection.find_one({"username": username})

    def find_by_patient_id(self, patient_id):
        return self.collection.find_one({"patientId": patient_id})

    def find_by_id(self, id):
        try:
            return self.collection.find_one({"_id": ObjectId(id)})
        except:
            return None

    def delete(self, id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except:
            return False
