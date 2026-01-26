from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    user_id: str
    alert_type: str
    message: str
    threshold_percentage: float
    current_usage_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True
