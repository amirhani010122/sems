from datetime import datetime
from bson import ObjectId
from ..database import get_database

async def deduct_quota_and_check_alerts(user_id: str, consumption_value: float):
    """خصم الاستهلاك من الباقة والتحقق من التنبيهات"""
    db = get_database()
    
    # البحث عن الاشتراك النشط
    subscription = await db.plan_subscriptions.find_one({
        "user_id": user_id,
        "is_active": True
    })
    
    if not subscription:
        return
    
    # حساب المتبقي الجديد
    new_remaining = subscription["remaining_quota"] - consumption_value
    if new_remaining < 0:
        new_remaining = 0
    
    # تحديث قيمة الباقة في قاعدة البيانات
    await db.plan_subscriptions.update_one(
        {"_id": subscription["_id"]},
        {
            "$set": {
                "remaining_quota": new_remaining,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # تحديث الكائن subscription بالقيمة الجديدة لاستخدامه في التحقق من التنبيهات
    subscription["remaining_quota"] = new_remaining
    await check_and_create_alerts(user_id, subscription)


async def check_and_create_alerts(user_id: str, subscription: dict):
    """التحقق من تخطي حد الاستهلاك وإنشاء تنبيه"""
    db = get_database()
    
    # جلب تفاصيل الخطة لمعرفة الحد الأقصى (Total Quota)
    plan_id = subscription["plan_id"]
    if isinstance(plan_id, str):
        try: plan_id = ObjectId(plan_id)
        except: pass
    
    plan = await db.plans.find_one({"_id": plan_id})
    if not plan:
        return
    
    total_quota = plan.get("total_quota", 0)
    remaining_quota = subscription["remaining_quota"]
    used_quota = total_quota - remaining_quota
    
    # حساب النسبة المئوية للاستهلاك
    usage_percentage = (used_quota / total_quota) * 100 if total_quota > 0 else 0
    
    # المستويات اللي عندها هنبعت تنبيه
    thresholds = [
        {"percentage": 70, "alert_type": "70%"},
        {"percentage": 90, "alert_type": "90%"},
        {"percentage": 100, "alert_type": "100%"}
    ]
    
    for threshold in thresholds:
        if usage_percentage >= threshold["percentage"]:
            # التأكد إن التنبيه متبعثش قبل كدة في نفس دورة الاشتراك الحالية
            existing_alert = await db.alerts.find_one({
                "user_id": user_id,
                "alert_type": threshold["alert_type"],
                "created_at": {"$gte": subscription.get("start_date", datetime.utcnow())}
            })
            
            if not existing_alert:
                # إعداد رسالة التنبيه
                message = f"لقد استهلكت {threshold['percentage']}% من سعة باقتك."
                if threshold["percentage"] == 100:
                    message = "تحذير: لقد استهلكت باقتك بالكامل (100%)."
                
                # إنشاء كائن التنبيه مع إضافة حقل created_at المهم جداً
                alert_dict = {
                    "user_id": user_id,
                    "alert_type": threshold["alert_type"],
                    "message": message,
                    "threshold_percentage": float(threshold["percentage"]),
                    "current_usage_percentage": float(usage_percentage),
                    "created_at": datetime.utcnow()  # الحقل ده هو اللي كان ناقص وبيسبب الـ 500 Error
                }
                
                await db.alerts.insert_one(alert_dict)
                print(f"🚨 Alert Created: {threshold['percentage']}% for user {user_id}")