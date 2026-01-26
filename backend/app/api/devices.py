from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from ..database import get_database
from ..schemas.device import DeviceCreate, DeviceResponse
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: DeviceCreate,
    current_user: dict = Depends(get_current_user)
):
    """Register a new IoT device"""
    db = get_database()
    
    # Check if device_id already exists
    existing_device = await db.devices.find_one({"device_id": device_data.device_id})
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID already registered"
        )
    
    # Create device
    device_dict = {
        "device_id": device_data.device_id,
        "device_name": device_data.device_name,
        "user_id": current_user["id"]
    }
    
    result = await db.devices.insert_one(device_dict)
    device_dict["_id"] = result.inserted_id
    
    return DeviceResponse(
        id=str(device_dict["_id"]),
        device_id=device_dict["device_id"],
        device_name=device_dict["device_name"],
        user_id=device_dict["user_id"],
        created_at=device_dict.get("created_at")
    )


@router.get("", response_model=List[DeviceResponse])
async def get_user_devices(current_user: dict = Depends(get_current_user)):
    """Get all devices for current user"""
    db = get_database()
    
    devices = await db.devices.find({"user_id": current_user["id"]}).to_list(length=100)
    
    return [
        DeviceResponse(
            id=str(device["_id"]),
            device_id=device["device_id"],
            device_name=device["device_name"],
            user_id=device["user_id"],
            created_at=device.get("created_at")
        )
        for device in devices
    ]


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific device"""
    db = get_database()
    
    device = await db.devices.find_one({
        "device_id": device_id,
        "user_id": current_user["id"]
    })
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return DeviceResponse(
        id=str(device["_id"]),
        device_id=device["device_id"],
        device_name=device["device_name"],
        user_id=device["user_id"],
        created_at=device.get("created_at")
    )
