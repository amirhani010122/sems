from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from .user import PyObjectId


class Plan(BaseModel):
    id: Optional[PyObjectId] = None
    plan_name: str
    total_quota: float  # kWh
    duration_days: int
    created_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = "plans"


class PlanSubscription(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: str
    plan_id: str
    start_date: datetime
    end_date: datetime
    remaining_quota: float  # kWh
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = "plan_subscriptions"
