from motor.motor_asyncio import AsyncIOMotorClient

from config import secretENV


class Database:
    client: AsyncIOMotorClient = None

db = Database()

def connect_to_mongo():
    db.client = AsyncIOMotorClient(secretENV.DATABASE_URL)
    print("Connected to MongoDB")

def close_mongo_connection():
    db.client.close()
    print("Closed MongoDB connection")