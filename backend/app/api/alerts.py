from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from datetime import datetime
from ..database import get_database
from ..schemas.alert import AlertResponse
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user)
):
    """
    Get alerts for the current user with improved error handling and efficiency.
    """
    try:
        db = get_database()

        # Fetch alerts from the database for the current user
        alerts = await db.alerts.find({"user_id": current_user["id"]})\
            .sort("created_at", -1)\
            .limit(limit)\
            .to_list(length=limit)

        # Ensure alerts are properly formatted and provide defaults for missing fields
        return [
            AlertResponse(
                id=str(alert.get("_id", "")),
                user_id=alert.get("user_id", current_user["id"]),
                alert_type=alert.get("alert_type", "usage_warning"),
                message=alert.get("message", "تنبيه جديد"),
                threshold_percentage=alert.get("threshold_percentage", 0.0),
                current_usage_percentage=alert.get("current_usage_percentage", 0.0),
                created_at=alert.get("created_at", datetime.utcnow())
            )
            for alert in alerts
        ]

    except Exception as e:
        # Log the error and raise an HTTP exception
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")