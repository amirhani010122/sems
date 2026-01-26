from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from .user import PyObjectId


class Consumption(BaseModel):
    id: Optional[PyObjectId] = None
    device_id: str
    user_id: str
    consumption_value: float  # kWh
    timestamp: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = "consumption"
