from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["Rag-impliment"]
users_collection = db["users"]
