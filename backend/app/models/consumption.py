from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from .user import PyObjectId
from sqlalchemy import Column, String, Float, Date
from backend.app.models.base import Base


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


class DailyConsumption(Base):
    __tablename__ = "daily_consumption"

    device_id = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    consumption = Column(Float, nullable=False)
