from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/fhir_db")
client = MongoClient(MONGO_URI)
db = client.get_database()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

FILES_TO_COLLECTIONS = {
    "patients.json": "patients",
    "conditions.json": "conditions",
    "observations.json": "observations",
    "medications.json": "medications"
}

def seed_data():
    for filename, collection_name in FILES_TO_COLLECTIONS.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping.")
            continue
        
        print(f"Processing {filename}...")
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding {filename}: {e}")
                continue

            if not isinstance(data, list):
                print(f"Error: Data in {filename} is not a list. Skipping.")
                continue

            collection = db[collection_name]
            total = len(data)
            processed = 0
            
            for record in data:
                if "id" not in record:
                    # If no ID, we can't easily prevent duplicates without more logic.
                    # Assuming FHIR resources have IDs as per research.
                    collection.insert_one(record)
                    processed += 1
                else:
                    # Upsert based on the FHIR 'id'
                    collection.update_one(
                        {"id": record["id"]},
                        {"$set": record},
                        upsert=True
                    )
                    processed += 1
            
            print(f"Finished {filename}: Processed {processed}/{total} records.")

if __name__ == "__main__":
    seed_data()
    print("\nData ingestion complete.")
    
    # Final count summary
    print("\nDatabase Summary:")
    for col in FILES_TO_COLLECTIONS.values():
        count = db[col].count_documents({})
        print(f"- {col}: {count} records")
