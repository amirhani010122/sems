from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceCreate(BaseModel):
    device_id: str
    device_name: str

class DeviceResponse(BaseModel):
    id: str
    device_id: str
    device_name: str
    user_id: str
    is_active: bool = True  # الحقل المضاف لربط الحالة
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True