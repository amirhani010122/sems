from datetime import datetime
from pydantic import BaseModel


class DeviceCreate(BaseModel):
    device_id: str
    device_name: str


class DeviceResponse(BaseModel):
    id: str
    device_id: str
    device_name: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
