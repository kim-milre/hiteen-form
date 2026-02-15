import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "amicom_template")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]