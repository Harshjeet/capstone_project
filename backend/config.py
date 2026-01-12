from pymongo import MongoClient
import os

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        from utils.logger import logger
        if not self.client:
            try:
                uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/fhir_db")
                self.client = MongoClient(uri)
                self.db = self.client.fhir_db
                # Trigger a command to verify connection
                self.client.admin.command('ping')
                logger.info(f"Connected to MongoDB at {uri.split('@')[-1]}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise e

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

db = Database()
