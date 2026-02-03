import asyncio
import httpx
import random
from datetime import datetime, timezone # تأكد من استيراد timezone
import os

# --- الإعدادات ---
BACKEND_URL = "http://127.0.0.1:8000"
DEVICE_ID = "ESP32_02"  
DEVICE_NAME = "Living Room Meter"
USER_EMAIL = "a@test.com"
USER_PASSWORD = "123"
SEND_INTERVAL = 2 

class IoTSimulator:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BACKEND_URL)
        self.token = None

    async def login(self):
        """تسجيل الدخول للحصول على Token"""
        print(f"🔑 Attempting login for {USER_EMAIL}...")
        try:
            response = await self.client.post("/api/v1/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Login Successful!")
                return True
            else:
                print(f"❌ Login Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return False

    async def send_data(self):
        """إرسال بيانات استهلاك عشوائية وتوقيت الجهاز الحالي"""
        val = round(random.uniform(0.5, 3.5), 2)
        
        # توحيد التوقيت: نأخذ توقيت جهازك الحالي ونحوله لـ UTC
        current_time_utc = datetime.now(timezone.utc).isoformat()
        
        payload = {
            "device_id": DEVICE_ID,
            "consumption_value": val, # تأكد أن الـ Backend يقرأ هذا الاسم
            "timestamp": current_time_utc
        }
        
        try:
            # إرسال البيانات للـ Backend
            response = await self.client.post("/api/v1/consumption", json=payload)
            if response.status_code in [200, 201]:
                print(f"🚀 [SENT] Device: {DEVICE_ID} | Value: {val} kWh | Time: {current_time_utc}")
            else:
                print(f"⚠️ [ERROR] Status: {response.status_code} | Info: {response.text}")
        except Exception as e:
            print(f"📡 [FAILED] Could not connect to server: {e}")

    async def start(self):
        if await self.login():
            print(f"⚙️ Simulator started. Sending data every {SEND_INTERVAL}s...")
            try:
                while True:
                    await self.send_data()
                    await asyncio.sleep(SEND_INTERVAL)
            except KeyboardInterrupt:
                print("\n🛑 Simulator stopped by user.")
        
        await self.client.aclose()

if __name__ == "__main__":
    simulator = IoTSimulator()
    asyncio.run(simulator.start())