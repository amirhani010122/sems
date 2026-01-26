from datetime import datetime
from pydantic import BaseModel


class PlanCreate(BaseModel):
    plan_name: str
    total_quota: float  # kWh
    duration_days: int


class PlanResponse(BaseModel):
    id: str
    plan_name: str
    total_quota: float
    duration_days: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlanSubscriptionCreate(BaseModel):
    plan_id: str


class PlanSubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    start_date: datetime
    end_date: datetime
    remaining_quota: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
