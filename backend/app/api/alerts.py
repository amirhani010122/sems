from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..database import get_database
from ..schemas.alert import AlertResponse
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts for current user"""
    db = get_database()
    
    alerts = await db.alerts.find({"user_id": current_user["id"]}).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return [
        AlertResponse(
            id=str(alert["_id"]),
            user_id=alert["user_id"],
            alert_type=alert["alert_type"],
            message=alert["message"],
            threshold_percentage=alert["threshold_percentage"],
            current_usage_percentage=alert["current_usage_percentage"],
            created_at=alert["created_at"]
        )
        for alert in alerts
    ]
