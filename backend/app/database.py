from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    # Test connection
    await mongodb.client.admin.command('ping')
    print("Connected to MongoDB")


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get database instance"""
    return mongodb.client[settings.mongodb_db_name]
