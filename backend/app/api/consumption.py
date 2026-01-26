from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..database import get_database
from ..schemas.consumption import ConsumptionCreate, ConsumptionResponse
from ..utils.dependencies import get_current_user
from ..services.plan_service import deduct_quota_and_check_alerts

router = APIRouter()


@router.post("", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED)
async def create_consumption(
    consumption_data: ConsumptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Record energy consumption (can be called by IoT simulator)"""
    db = get_database()
    
    # Verify device belongs to user
    device = await db.devices.find_one({
        "device_id": consumption_data.device_id,
        "user_id": current_user["id"]
    })
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or does not belong to user"
        )
    
    # Create consumption record
    timestamp = consumption_data.timestamp or datetime.utcnow()
    consumption_dict = {
        "device_id": consumption_data.device_id,
        "user_id": current_user["id"],
        "consumption_value": consumption_data.consumption_value,
        "timestamp": timestamp
    }
    
    result = await db.consumption.insert_one(consumption_dict)
    consumption_dict["_id"] = result.inserted_id
    
    # Deduct from plan quota and check alerts
    await deduct_quota_and_check_alerts(
        current_user["id"],
        consumption_data.consumption_value
    )
    
    return ConsumptionResponse(
        id=str(consumption_dict["_id"]),
        device_id=consumption_dict["device_id"],
        user_id=consumption_dict["user_id"],
        consumption_value=consumption_dict["consumption_value"],
        timestamp=consumption_dict["timestamp"]
    )


@router.get("", response_model=List[ConsumptionResponse])
async def get_consumption_history(
    device_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Get consumption history for current user"""
    db = get_database()
    
    query = {"user_id": current_user["id"]}
    
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
