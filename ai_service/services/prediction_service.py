import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.linear_model import LinearRegression

class PredictionService:
    def __init__(self, backend_api_url: str):
        self.backend_api_url = backend_api_url
    
    async def fetch_consumption_data(self, user_id: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.backend_api_url}/api/internal/consumption",
                    params={"user_id": user_id},
                    headers={"X-Service-Key": "internal-service-key-change-in-production"},
                    timeout=30.0
                )
                return response.json() if response.status_code == 200 else []
            except Exception: return []

    async def fetch_subscription_data(self, user_id: str) -> Dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.backend_api_url}/api/internal/subscription",
                    params={"user_id": user_id},
                    headers={"X-Service-Key": "internal-service-key-change-in-production"},
                    timeout=30.0
                )
                return response.json() if response.status_code == 200 else None
            except Exception: return None

    async def predict_consumption(self, user_id: str, days: int = 7) -> Dict:
        """توقع الاستهلاك المستقبلي باستخدام الـ Linear Regression المطوّر"""
        data = await self.fetch_consumption_data(user_id)
        
        if not data or len(data) < 3:
            return {
                "user_id": user_id,
                "predicted_total_kwh": 5.0 * days, # قيمة افتراضية
                "confidence": "Very Low (Initial Phase)"
            }
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        daily = df.groupby(df['timestamp'].dt.date)['consumption_value'].sum().reset_index()
        daily.columns = ['date', 'consumption']
        
        # تحويل التاريخ لأرقام للتدريب
        X = np.arange(len(daily)).reshape(-1, 1)
        y = daily['consumption'].values
        
        # AI Model - التدريب
        model = LinearRegression()
        model.fit(X, y)
        
        # توقع الأيام القادمة
        future_X = np.arange(len(daily), len(daily) + days).reshape(-1, 1)
        predictions = model.predict(future_X)
        predictions = np.maximum(predictions, 0.5) # نمنع القيم الصفرية أو السالبة
        
        avg_predicted = float(np.mean(predictions))
        
        # قياس مدى دقة النموذج (لو الاستهلاك متذبذب جداً الدقة بتقل)
        variance = np.var(y)
        confidence = "High" if variance < 50 and len(daily) > 10 else "Medium"

        return {
            "user_id": user_id,
            "prediction_period_days": days,
            "predicted_daily_avg": round(avg_predicted, 2),
            "predicted_total_for_period": round(float(np.sum(predictions)), 2),
            "trend_slope": float(model.coef_[0]), # هل الاستهلاك بيزيد ولا بيقل مع الوقت؟
            "confidence": confidence
        }

    async def predict_plan_exhaustion(self, user_id: str) -> Dict:
        """توقع تاريخ انتهاء شحن العداد/الباقة"""
        sub = await self.fetch_subscription_data(user_id)
        if not sub:
            return {"message": "No active plan found"}

        remaining = sub.get('remaining_quota', 0)
        # نطلب توقع لـ 30 يوم عشان نعرف معدل الاستهلاك اليومي
        pred_data = await self.predict_consumption(user_id, days=30)
        daily_rate = pred_data['predicted_daily_avg']

        if daily_rate <= 0: daily_rate = 1.0 # حماية من القسمة على صفر
        
        days_left = remaining / daily_rate
        exhaustion_date = datetime.utcnow() + timedelta(days=days_left)
        
        # ذكاء إضافي: تحديد مستوى الاستعجال
        status = "Healthy"
        if days_left < 3: status = "Urgent / Critical"
        elif days_left < 7: status = "Warning"

        return {
            "user_id": user_id,
            "current_balance_kwh": remaining,
            "estimated_days_remaining": round(days_left, 1),
            "estimated_exhaustion_date": exhaustion_date.strftime("%Y-%m-%d"),
            "system_status": status,
            "ai_advice": f"بناءً على معدل استهلاكك ({daily_rate} kWh/يوم)، يرجى إعادة الشحن قبل {exhaustion_date.strftime('%m/%d')}."
        }