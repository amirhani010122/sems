from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from .user import PyObjectId


class Alert(BaseModel):
    id: Optional[PyObjectId] = None
    user_id: str
    alert_type: str  # "70%", "90%", "100%"
    message: str
    threshold_percentage: float
    current_usage_percentage: float
    created_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = "alerts"
