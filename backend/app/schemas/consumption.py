from datetime import datetime
from pydantic import BaseModel


class ConsumptionCreate(BaseModel):
    device_id: str
    consumption_value: float  # kWh
    timestamp: datetime = None


class ConsumptionResponse(BaseModel):
    id: str
    device_id: str
    user_id: str
    consumption_value: float
    timestamp: datetime

    class Config:
        from_attributes = True
