from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from ..database import get_database
from ..schemas.consumption import ConsumptionCreate, ConsumptionResponse
from ..utils.dependencies import get_current_user
from ..services.plan_service import deduct_quota_and_check_alerts

router = APIRouter()

# --- 1. إحصائيات الاستهلاك (الرسم البياني) ---

@router.get("/daily")
async def get_daily_consumption(current_user: dict = Depends(get_current_user)):
    """حساب الاستهلاك اليومي لآخر 7 أيام - يعتمد عليه الرسم البياني"""
    db = get_database()
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    pipeline = [
        {
            "$match": {
                "user_id": current_user["id"],
                "timestamp": {"$gte": seven_days_ago}
            }
        },
        {
            "$group": {
                "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" } },
                "total": { "$sum": "$consumption_value" }
            }
        },
        { "$sort": { "_id": 1 } }
    ]
    
    cursor = db.consumption.aggregate(pipeline)
    result = await cursor.to_list(length=7)
    return [{"date": item["_id"], "value": round(item["total"], 2)} for item in result]


@router.get("/summary")
async def get_consumption_summary(current_user: dict = Depends(get_current_user)):
    """حساب إجمالي الاستهلاك للباقة النشطة (تصفير العداد)"""
    db = get_database()
    subscription = await db.plan_subscriptions.find_one({
        "user_id": current_user["id"],
        "is_active": True
    })
    
    if not subscription:
        return {"total_consumption": 0.0, "remaining_quota": 0.0, "message": "No active plan"}

    start_date = subscription["start_date"]
    pipeline = [
        {
            "$match": {
                "user_id": current_user["id"],
                "timestamp": {"$gte": start_date}
            }
        },
        {"$group": {"_id": None, "total": {"$sum": "$consumption_value"}}}
    ]
    
    cursor = db.consumption.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    total = result[0]["total"] if result else 0.0
    
    return {
        "total_consumption": float(total),
        "remaining_quota": float(subscription.get("remaining_quota", 0)),
        "unit": "kWh"
    }

# --- 2. العملية الأساسية (Core Logic) ---

@router.post("", response_model=ConsumptionResponse, status_code=status.HTTP_201_CREATED)
async def create_consumption(
    consumption_data: ConsumptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """العملية الموحدة: تسجيل الاستهلاك، تحديث حالة الجهاز، وخصم الرصيد"""
    db = get_database()
    user_id = current_user["id"]
    timestamp = datetime.utcnow() 

    # 1. تحديد حالة الجهاز (Active لو القيمة > 0)
    status_active = consumption_data.consumption_value > 0

    # 2. تحديث جدول الأجهزة (أو إنشاؤه لو أول مرة)
    await db.devices.update_one(
        {"device_id": consumption_data.device_id, "user_id": user_id},
        {
            "$set": {
                "last_seen": timestamp,
                "is_active": status_active,
                "value": consumption_data.consumption_value
            },
            "$setOnInsert": {
                "device_name": f"Device {consumption_data.device_id}",
                "created_at": timestamp
            }
        },
        upsert=True # دي بتغنيك عن الـ if/else وتعمل insert لو مش موجود
    )

    # 3. حفظ السجل الخام (التاريخ)
    consumption_dict = {
        "device_id": consumption_data.device_id,
        "user_id": user_id,
        "consumption_value": consumption_data.consumption_value,
        "timestamp": timestamp
    }
    result = await db.consumption.insert_one(consumption_dict)
    
    # 4. خصم الكوتا وفحص التنبيهات
    await deduct_quota_and_check_alerts(user_id, consumption_data.consumption_value)
    
    consumption_dict["id"] = str(result.inserted_id)
    return consumption_dict


@router.get("/monthly")

async def get_monthly_consumption(current_user: dict = Depends(get_current_user)):

    """حساب الاستهلاك الشهري لآخر 6 أشهر"""

    db = get_database()

    pipeline = [

        { "$match": { "user_id": current_user["id"] } },

        {

            "$group": {

                "_id": { "$dateToString": { "format": "%Y-%m", "date": "$timestamp" } },

                "total": { "$sum": "$consumption_value" }

            }

        },

        { "$sort": { "_id": 1 } }

    ]

   

    cursor = db.consumption.aggregate(pipeline)

    result = await cursor.to_list(length=6)

    return [{"month": item["_id"], "value": round(item["total"], 2)} for item in result]


# @router.get("", response_model=List[ConsumptionResponse])
# async def get_consumption_history(
#     device_id: Optional[str] = Query(None),
#     limit: int = Query(50),
#     current_user: dict = Depends(get_current_user)
# ):
#     """جلب قائمة آخر القراءات"""
#     db = get_database()
#     query = {"user_id": current_user["id"]}
#     if device_id: query["device_id"] = device_id
        
#     cursor = db.consumption.find(query).sort("timestamp", -1).limit(limit)
#     consumptions = await cursor.to_list(length=limit)
#     return [
#         ConsumptionResponse(
#             id=str(c["_id"]),
#             device_id=c["device_id"],
#             user_id=c["user_id"],
#             consumption_value=c["consumption_value"],
#             timestamp=c["timestamp"] 
#         ) for c in consumptions
#     ]
@router.get("/per-device-daily")
async def get_total_consumption_per_day_per_device(
    current_user: dict = Depends(get_current_user)
):
    """حساب إجمالي الاستهلاك لكل يوم لكل جهاز على حدة"""
    db = get_database()
    
    pipeline = [
        # 1. تصفية البيانات الخاصة بالمستخدم الحالي فقط
        { "$match": { "user_id": current_user["id"] } },
        
        # 2. تجميع البيانات بناءً على (تاريخ اليوم + الـ device_id)
        {
            "$group": {
                "_id": {
                    "date": { "$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" } },
                    "device_id": "$device_id"
                },
                "total_daily_value": { "$sum": "$consumption_value" }
            }
        },
        
        # 3. ترتيب النتائج حسب التاريخ (الأحدث أولاً) ثم اسم الجهاز
        { "$sort": { "_id.date": -1, "_id.device_id": 1 } },
        
        # 4. تجميل شكل البيانات الخارجة (Projection)
        {
            "$project": {
                "_id": 0,
                "date": "$_id.date",
                "device_id": "$_id.device_id",
                "total_consumption": { "$round": ["$total_daily_value", 2] }
            }
        }
    ]
    
    cursor = db.consumption.aggregate(pipeline)
    result = await cursor.to_list(length=None)
    return result