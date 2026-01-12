from pymongo import MongoClient
import os

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        if not self.client:
            self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/fhir_db"))
            self.db = self.client.fhir_db

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

db = Database()
