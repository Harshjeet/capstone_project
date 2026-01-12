from config import db
from bson.objectid import ObjectId

class InsurancePlanModel:
    def __init__(self):
        self.collection = db.get_db().insurance_plans

    def create(self, data):
        data["_id"] = ObjectId()
        self.collection.insert_one(data)
        return data["_id"]

    def find_all(self):
        return list(self.collection.find())

    def find_by_id(self, plan_id):
        try:
            return self.collection.find_one({"_id": ObjectId(plan_id)})
        except:
            return None

    def update(self, plan_id, data):
        try:
            self.collection.update_one({"_id": ObjectId(plan_id)}, {"$set": data})
            return True
        except:
            return False

    def delete(self, plan_id):
        try:
            self.collection.delete_one({"_id": ObjectId(plan_id)})
            return True
        except:
            return False
