import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def seed_test_ai_data(user_id: str):
    # الاتصال بقاعدة البيانات
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.sems_db  
    collection = db.consumption # تأكد من اسم الكولكشن عندك (ممكن يكون consumption)

    # 1. مسح البيانات القديمة لليوزر ده عشان نبدأ على نظافة
    await collection.delete_many({"user_id": user_id})
    print(f"Done: Cleared old data for user {user_id}")

    test_data = []
    start_date = datetime.utcnow() - timedelta(days=20)

    # 2. توليد بيانات "مستقرة" بتزيد ببطء (عشان نختبر التوقع)
    for i in range(20):
        current_date = start_date + timedelta(days=i)
        
        # استهلاك طبيعي بيبدأ من 10 وبيزيد 0.5 كل يوم (10, 10.5, 11, ...)
        base_value = 10 + (i * 0.5) 
        
        # 3. زرع "الخديعة" (Anomaly) في اليوم العاشر
        if i == 10:
            base_value = 80  # رقم شاذ جداً بالنسبة للنمط
            print(f"Inserted Anomaly at day 10: {base_value} kWh")

        test_data.append({
            "user_id": user_id,
            "consumption_value": base_value,
            "timestamp": current_date,
            "device_id": "test_device_001"
        })

    # إدخال البيانات
    if test_data:
        await collection.insert_many(test_data)
        print(f"Successfully inserted {len(test_data)} records for testing! ✅")

if __name__ == "__main__":
    # حط الـ user_id بتاعك هنا
    USER_ID = "6984f33a8f92bbb3d5f23ae4"
    asyncio.run(seed_test_ai_data(USER_ID))