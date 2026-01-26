from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query, Header, Depends
from typing import List, Optional
from ..database import get_database
from ..schemas.consumption import ConsumptionResponse
from ..schemas.plan import PlanSubscriptionResponse
from ..config import settings

router = APIRouter()

# Simple service key for internal API calls (in production, use proper service authentication)
SERVICE_KEY = "internal-service-key-change-in-production"


async def verify_service_key(x_service_key: str = Header(..., alias="X-Service-Key")):
    """Verify service key for internal API calls"""
    if x_service_key != SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service key"
        )
    return True


@router.get("/consumption", response_model=List[ConsumptionResponse])
async def get_consumption_by_user_id(
    user_id: str = Query(...),
    device_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(1000, le=10000),
    _: bool = Depends(verify_service_key)
):
    """Internal endpoint to get consumption data by user_id"""
    db = get_database()
    
    query = {"user_id": user_id}
    
    if device_id:
        query["device_id"] = device_id
    
    if start_date:
        query["timestamp"] = {"$gte": start_date}
    
    if end_date:
        if "timestamp" in query:
            query["timestamp"]["$lte"] = end_date
        else:
            query["timestamp"] = {"$lte": end_date}
    
    consumptions = await db.consumption.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    return [
        ConsumptionResponse(
            id=str(cons["_id"]),
            device_id=cons["device_id"],
            user_id=cons["user_id"],
            consumption_value=cons["consumption_value"],
            timestamp=cons["timestamp"]
        )
        for cons in consumptions
    ]


@router.get("/subscription", response_model=PlanSubscriptionResponse)
async def get_subscription_by_user_id(
    user_id: str = Query(...),
    _: bool = Depends(verify_service_key)
):
    """Internal endpoint to get subscription data by user_id"""
    db = get_database()
    
    subscription = await db.plan_subscriptions.find_one({
        "user_id": user_id,
        "is_active": True
    })
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return PlanSubscriptionResponse(
        id=str(subscription["_id"]),
        user_id=subscription["user_id"],
        plan_id=subscription["plan_id"],
        start_date=subscription["start_date"],
        end_date=subscription["end_date"],
        remaining_quota=subscription["remaining_quota"],
        is_active=subscription["is_active"],
        created_at=subscription.get("created_at"),
        updated_at=subscription.get("updated_at")
    )
