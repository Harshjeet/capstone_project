
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client.fhir_db
patient = db.patients.find_one(sort=[("_id", -1)])
print(json.dumps(patient, indent=2, default=str))
