from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, TYPE_CHECKING
from .config import settings
from backend.app.models.consumption import DailyConsumption  # Import the DailyConsumption model
from backend.app.models.base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    # Test connection
    await mongodb.client.admin.command('ping')

    # Ensure important indexes for performance and uniqueness
    try:
        db = mongodb.client[settings.mongodb_db_name]
        # Unique per-user device_id
        await db.devices.create_index([("user_id", 1), ("device_id", 1)], unique=True)
        # Index last_seen for devices to speed up active checks
        await db.devices.create_index([("last_seen", -1)])
        # Fast lookup of consumption by device (latest timestamp)
        await db.consumption.create_index([("device_id", 1), ("timestamp", -1)])
        print("Connected to MongoDB and ensured indexes")
    except Exception as e:
        # Log index creation errors but keep the connection (so devs can inspect logs)
        print(f"Connected to MongoDB but failed ensuring indexes: {e}")


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")


def get_database():
    """Get database instance"""
    return mongodb.client[settings.mongodb_db_name]


# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mongodb.client)


def get_db():
    """Provide a database session for dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
