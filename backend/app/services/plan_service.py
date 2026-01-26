from datetime import datetime
from bson import ObjectId
from ..database import get_database


async def deduct_quota_and_check_alerts(user_id: str, consumption_value: float):
    """Deduct consumption from active plan and check for alerts"""
    db = get_database()
    
    # Find active plan subscription
    subscription = await db.plan_subscriptions.find_one({
        "user_id": user_id,
        "is_active": True
    })
    
    if not subscription:
        # No active plan, skip deduction
        return
    
    # Deduct from remaining quota
    new_remaining = subscription["remaining_quota"] - consumption_value
    if new_remaining < 0:
        new_remaining = 0
    
    # Update subscription
    await db.plan_subscriptions.update_one(
        {"_id": subscription["_id"]},
        {
            "$set": {
                "remaining_quota": new_remaining,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Check for alerts
    await check_and_create_alerts(user_id, subscription)


async def check_and_create_alerts(user_id: str, subscription: dict):
    """Check usage thresholds and create alerts if needed"""
    db = get_database()
    
    # Get plan details
    plan_id = subscription["plan_id"]
    # Handle both ObjectId and string plan_id
    if isinstance(plan_id, str):
        try:
            plan_id = ObjectId(plan_id)
        except:
            pass
    
    plan = await db.plans.find_one({"_id": plan_id})
    if not plan:
        return
    
    total_quota = plan["total_quota"]
    remaining_quota = subscription["remaining_quota"]
    used_quota = total_quota - remaining_quota
    usage_percentage = (used_quota / total_quota) * 100 if total_quota > 0 else 0
    
    # Define thresholds
    thresholds = [
        {"percentage": 70, "alert_type": "70%"},
        {"percentage": 90, "alert_type": "90%"},
        {"percentage": 100, "alert_type": "100%"}
    ]
    
    for threshold in thresholds:
        # Check if we've crossed this threshold
        if usage_percentage >= threshold["percentage"]:
            # Check if alert already exists for this threshold
            existing_alert = await db.alerts.find_one({
                "user_id": user_id,
                "alert_type": threshold["alert_type"],
                "created_at": {
                    "$gte": subscription["start_date"]
                }
            })
            
            if not existing_alert:
                # Create new alert
                message = f"Energy usage has reached {threshold['percentage']}% of your plan quota"
                if threshold["percentage"] == 100:
                    message = "Energy usage has reached 100% of your plan quota. Plan exhausted!"
                
                alert_dict = {
                    "user_id": user_id,
                    "alert_type": threshold["alert_type"],
                    "message": message,
                    "threshold_percentage": threshold["percentage"],
                    "current_usage_percentage": usage_percentage
                }
                
                await db.alerts.insert_one(alert_dict)
