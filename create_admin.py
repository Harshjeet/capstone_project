from config import db
from models.models import UserModel

def create_admin():
    db.connect()
    user_model = UserModel()
    
    username = "admin"
    password = "admin123"
    
    # Check if exists
    existing = user_model.find_by_username(username)
    if existing:
        print(f"Admin user '{username}' already exists. Updating password...")
        user_model.collection.update_one({"_id": existing["_id"]}, {"$set": {"password": password}})
        print("Password updated.")
        return

    admin_data = {
        "username": username,
        "password": password,
        "role": "admin",
        "name": "System Administrator",
        "patientId": None
    }
    
    user_model.create(admin_data)
    print(f"Admin user '{username}' created successfully.")

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    create_admin()
