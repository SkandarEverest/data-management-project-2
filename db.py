# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file in the project root
load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    client = MongoClient(uri)
    return client[db_name]
