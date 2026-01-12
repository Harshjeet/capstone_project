from pymongo import MongoClient
import random
import json
from datetime import datetime
import os

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/fhir_db"))
db = client["fhir_db"]

# Clear existing data
db.patients.delete_many({})
db.conditions.delete_many({})
db.observations.delete_many({})

print("Cleared existing data.")

# Create Admin User
admin_user = db.users.find_one({"username": "admin"})
if not admin_user:
    db.users.insert_one({
        "username": "admin",
        "password": "admin123", # Plain text for demo as requested, ideally hashed
        "role": "admin",
        "name": "Administrator"
    })
    print("Created default admin user: admin/admin123")


CONDITIONS = [
    "Acute upper respiratory infection", "Fever", "Cough", "Headache", # Basic
    "Hypertension", "Allergic rhinitis", # Standard
    "Diabetes mellitus", "Asthma", # Gold
    "Coronary heart disease", "Fracture" # Platinum
]

# Load patients from JSON
patients_file = os.path.join(os.path.dirname(__file__), 'data', 'patients.json')
with open(patients_file, 'r') as f:
    PATIENTS = json.load(f)

print(f"Propulating {len(PATIENTS)} patients from file...")
patient_id_map = {}

for p_data in PATIENTS:
    # Use 'id' as key if present
    custom_id = p_data.get("id")
    if custom_id:
        existing = db.patients.find_one({"id": custom_id})
        if not existing:
             db.patients.insert_one(p_data)
        # Verify it exists now
        # We don't need to do much else, the references in conditions use "Patient/{id}"
    else:
        db.patients.insert_one(p_data)

# Ensure p001-p030 exist for the new data
for i in range(1, 40):
    pid = f"p{i:03d}"
    if not db.patients.find_one({"id": pid}):
        db.patients.insert_one({
            "resourceType": "Patient",
            "id": pid,
            "name": [{"text": f"Simulated Patient {pid}"}],
            "gender": "unknown",
            "birthDate": "1980-01-01"
        })

# Load Conditions
conditions_file = os.path.join(os.path.dirname(__file__), 'data', 'conditions.json')
if os.path.exists(conditions_file):
    with open(conditions_file, 'r') as f:
        conditions_data = json.load(f)
    if conditions_data:
        db.conditions.insert_many(conditions_data)
        print(f"Seeded {len(conditions_data)} conditions.")

# Load Observations
observations_file = os.path.join(os.path.dirname(__file__), 'data', 'observations.json')
if os.path.exists(observations_file):
    with open(observations_file, 'r') as f:
        observations_data = json.load(f)
    if observations_data:
        db.observations.insert_many(observations_data)
        print(f"Seeded {len(observations_data)} observations.")

print("Database seeded successfully!")

