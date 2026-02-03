from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from ..database import get_database
from ..schemas.plan import PlanCreate, PlanResponse, PlanSubscriptionCreate, PlanSubscriptionResponse
from ..utils.dependencies import get_current_user

router = APIRouter()

@router.post("/create", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(plan_data: PlanCreate):
    """Create a new energy plan (admin function)"""
    db = get_database()
    
    plan_dict = {
        "plan_name": plan_data.plan_name,
        "total_quota": plan_data.total_quota,
        "duration_days": plan_data.duration_days,
        "created_at": datetime.utcnow()
    }
    
    result = await db.plans.insert_one(plan_dict)
    plan_dict["_id"] = result.inserted_id
    
    return PlanResponse(
        id=str(plan_dict["_id"]),
        plan_name=plan_dict["plan_name"],
        total_quota=plan_dict["total_quota"],
        duration_days=plan_dict["duration_days"],
        created_at=plan_dict["created_at"]
    )

@router.get("/available", response_model=List[PlanResponse])
async def get_available_plans():
    """Get all available energy plans"""
    db = get_database()
    plans = await db.plans.find().to_list(length=100)
    
    return [
        PlanResponse(
            id=str(plan["_id"]),
            plan_name=plan["plan_name"],
            total_quota=plan["total_quota"],
            duration_days=plan["duration_days"],
            created_at=plan.get("created_at")
        )
        for plan in plans
    ]

@router.post("/subscribe", response_model=PlanSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_plan(
    subscription_data: PlanSubscriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Subscribe to an energy plan"""
    db = get_database()
    
    try:
        plan_id = ObjectId(subscription_data.plan_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID format"
        )
    
    plan = await db.plans.find_one({"_id": plan_id})
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Deactivate any existing active subscription
    await db.plan_subscriptions.update_many(
        {"user_id": str(current_user["id"]), "is_active": True},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    # Create new subscription
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan["duration_days"])
    
    subscription_dict = {
        "user_id": str(current_user["id"]),
        "plan_id": str(plan_id),
        "start_date": start_date,
        "end_date": end_date,
        "remaining_quota": plan["total_quota"],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.plan_subscriptions.insert_one(subscription_dict)
    subscription_dict["_id"] = result.inserted_id
    
    return PlanSubscriptionResponse(
        id=str(subscription_dict["_id"]),
        user_id=subscription_dict["user_id"],
        plan_id=subscription_dict["plan_id"],
        start_date=subscription_dict["start_date"],
        end_date=subscription_dict["end_date"],
        remaining_quota=subscription_dict["remaining_quota"],
        is_active=subscription_dict["is_active"],
        created_at=subscription_dict["created_at"],
        updated_at=subscription_dict["updated_at"]
    )

@router.get("/subscription", response_model=PlanSubscriptionResponse)
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """Get current active subscription with mapping for Flutter UI"""
    db = get_database()
    
    user_id_str = str(current_user["id"])
    
    subscription = await db.plan_subscriptions.find_one({
        "user_id": user_id_str,
        "is_active": True
    })
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # جلب تفاصيل الباقة الأصلية
    plan_details = await db.plans.find_one({"_id": ObjectId(subscription["plan_id"])})
    
    # بناء الرد النهائي ليوافق الـ Schema (FastAPI) والـ UI (Flutter)
    return {
        # 1. حقول الـ Schema الأساسية (لتجنب الـ ResponseValidationError)
        "id": str(subscription["_id"]),
        "user_id": str(subscription["user_id"]),
        "plan_id": str(subscription["plan_id"]),
        "start_date": subscription["start_date"],
        "end_date": subscription["end_date"],
        "remaining_quota": float(subscription["remaining_quota"]),
        "is_active": subscription["is_active"],
        "created_at": subscription.get("created_at", datetime.utcnow()),
        "updated_at": subscription.get("updated_at", datetime.utcnow()),
        
        # 2. الحقول السحرية التي تجعل الـ Dashboard تظهر البيانات فوراً
        # الموبايل في dashboard_page.dart يبحث عن 'name' و 'limit' و 'unit'
        "name": plan_details["plan_name"] if plan_details else "Basic Plan",
        "limit": float(plan_details["total_quota"]) if plan_details else 100.0,
        "unit": "kWh"
    }