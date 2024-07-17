from motor.motor_asyncio import AsyncIOMotorClient
from app.config import DB_URL

client = AsyncIOMotorClient(DB_URL)
user_db = client["user_database"]
job_db = client["job_database"]
