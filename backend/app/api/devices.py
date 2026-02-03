from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from ..database import get_database
from ..schemas.device import DeviceCreate, DeviceResponse
from ..utils.dependencies import get_current_user
from datetime import datetime, timedelta
import pytz

router = APIRouter()

# إعدادات الوقت
LOCAL_TIMEZONE = pytz.timezone("Africa/Cairo") 

# --- وظيفة المراقب (The Watchdog) ---
async def update_offline_status_background(db, user_id: str):
    """
    وظيفة خلفية: بتبص على الأجهزة اللي مبعتتش داتا من أكتر من 60 ثانية
    وتحولها لـ False في المونجو عشان التطبيق يقرأ الحالة صح.
    """
    threshold = datetime.utcnow() - timedelta(seconds=3)
    await db.devices.update_many(
        {
            "user_id": user_id, 
            "last_seen": {"$lt": threshold}, 
            "is_active": True
        },
        {"$set": {"is_active": False}}
    )

def construct_device_response(device):
    """تحويل بيانات المونجو لتنسيق الرد مع ضبط توقيت مصر للعرض فقط"""
    last_seen = device.get("last_seen")
    created_at = device.get("created_at")

    if last_seen and isinstance(last_seen, datetime):
        last_seen = last_seen.replace(tzinfo=pytz.utc).astimezone(LOCAL_TIMEZONE)
    if created_at and isinstance(created_at, datetime):
        created_at = created_at.replace(tzinfo=pytz.utc).astimezone(LOCAL_TIMEZONE)

    return DeviceResponse(
        id=str(device["_id"]),
        device_id=device["device_id"],
        device_name=device.get("device_name") or device.get("name") or "Unknown Device",
        user_id=device["user_id"],
        is_active=device.get("is_active", False), # نثق في القيمة المخزنة
        last_seen=last_seen,
        created_at=created_at
    )

# 1. جلب جميع الأجهزة (مع مراقبة الحالة في الخلفية)
@router.get("", response_model=List[DeviceResponse])
async def get_user_devices(
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    
    # تشغيل المراقب لتحديث أي جهاز فصل سيموليتره
    background_tasks.add_task(update_offline_status_background, db, current_user["id"])
    
    devices = await db.devices.find({"user_id": current_user["id"]}).to_list(length=None)
    return [construct_device_response(d) for d in devices]

# 2. تسجيل جهاز جديد
@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(device_data: DeviceCreate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    if await db.devices.find_one({"device_id": device_data.device_id, "user_id": current_user["id"]}):
        raise HTTPException(status_code=400, detail="Device ID already registered")

    device_dict = {
        "device_id": device_data.device_id,
        "device_name": device_data.device_name,
        "user_id": current_user["id"],
        "is_active": False,
        "last_seen": datetime.utcnow(),
        "value": 0.0,
        "created_at": datetime.utcnow()
    }
    result = await db.devices.insert_one(device_dict)
    device_dict["_id"] = result.inserted_id
    return construct_device_response(device_dict)

# 3. جلب جهاز معين (مع تحديث الحالة برضه)
@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    background_tasks.add_task(update_offline_status_background, db, current_user["id"])

    try:
        query = {"_id": ObjectId(device_id), "user_id": current_user["id"]}
    except InvalidId:
        query = {"device_id": device_id, "user_id": current_user["id"]}

    device = await db.devices.find_one(query)
    if not device: 
        raise HTTPException(status_code=404, detail="Device not found")
    
    return construct_device_response(device)

# 4. حذف جهاز
@router.delete("/{device_id}")
async def delete_device(device_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    try:
        query = {"_id": ObjectId(device_id), "user_id": current_user["id"]}
    except InvalidId:
        query = {"device_id": device_id, "user_id": current_user["id"]}
        
    result = await db.devices.delete_one(query)
    if result.deleted_count == 0: 
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "success"}