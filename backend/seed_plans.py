from config import db
from models.insurance_plan_model import InsurancePlanModel

PLANS = [
    {
        "id": "basic",
        "name": "Basic Care",
        "cost": 50,
        "description": "Covers basic seasonal illnesses like cold, fever, and minor infections.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache"]
    },
    {
        "id": "standard",
        "name": "Standard Care",
        "cost": 100,
        "description": "Includes Basic coverage plus common chronic conditions management (early stage).",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis"]
    },
    {
        "id": "gold",
        "name": "Gold Premium",
        "cost": 200,
        "description": "Comprehensive coverage including diabetes management and moderate conditions.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis", "Diabetes mellitus", "Asthma"]
    },
    {
        "id": "platinum",
        "name": "Platinum Elite",
        "cost": 350,
        "description": "Full coverage for serious chronic conditions, cardiac issues, and surgeries.",
        "coverage": ["Acute upper respiratory infection", "Fever", "Cough", "Headache", "Hypertension", "Allergic rhinitis", "Diabetes mellitus", "Asthma", "Coronary heart disease", "Fracture"]
    },
    {
        "id": "comprehensive",
        "name": "Universal Comprehensive",
        "cost": 500,
        "description": "Total coverage for all known conditions, rare diseases, and long-term care.",
        "coverage": ["ALL"]
    }
]

def seed_plans():
    model = InsurancePlanModel()
    existing = model.find_all()
    if not existing:
        print("Seeding Insurance Plans...")
        for p in PLANS:
            model.create(p)
        print("Done.")
    else:
        print("Insurance Plans already exist.")

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    db.connect()
    seed_plans()
