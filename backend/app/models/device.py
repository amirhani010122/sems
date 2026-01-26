from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from .user import PyObjectId


class Device(BaseModel):
    id: Optional[PyObjectId] = None
    device_id: str
    device_name: str
    user_id: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        collection = "devices"
