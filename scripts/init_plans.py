"""
Script to initialize sample energy plans in the database
Run this after starting the backend and MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "sems_db"

# Sample plans
PLANS = [
    {
        "plan_name": "Basic Plan",
        "total_quota": 100.0,  # kWh
        "duration_days": 30
    },
    {
        "plan_name": "Standard Plan",
        "total_quota": 250.0,  # kWh
        "duration_days": 30
    },
    {
        "plan_name": "Premium Plan",
        "total_quota": 500.0,  # kWh
        "duration_days": 30
    },
    {
        "plan_name": "Weekly Plan",
        "total_quota": 50.0,  # kWh
        "duration_days": 7
    }
]


async def init_plans():
    """Initialize sample plans"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    
    print("Initializing energy plans...")
    
    for plan_data in PLANS:
        # Check if plan already exists
        existing = await db.plans.find_one({"plan_name": plan_data["plan_name"]})
        if existing:
            print(f"  [OK] Plan '{plan_data['plan_name']}' already exists")
            continue
        
        plan_data["created_at"] = datetime.utcnow()
        result = await db.plans.insert_one(plan_data)
        print(f"  [OK] Created plan: {plan_data['plan_name']} (ID: {result.inserted_id})")
    
    print("\n[OK] Plans initialization complete!")
    client.close()


if __name__ == "__main__":
    asyncio.run(init_plans())
