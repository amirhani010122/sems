import httpx
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest

class AnalysisService:
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

    def generate_ai_recommendation(self, prediction: float, trend: float, anomalies: int) -> str:
        """محرك نصائح ذكي بناءً على نتائج الـ AI"""
        if anomalies > 0:
            return "تنبيه: تم رصد سحب مفاجئ وغير معتاد. يرجى التحقق من الأجهزة التي تعمل حالياً أو فحص التوصيلات."
        
        if trend > 0.5:
            return f"نلاحظ زيادة مستمرة في استهلاكك. نتوقع أن يرتفع استهلاكك غداً إلى {round(prediction, 1)} كيلوواط. حاول تقليل الأحمال غير الضرورية."
        
        if prediction < 10:
            return "أداء ممتاز! استهلاكك منخفض ومستقر حالياً. استمر في هذا النمط لتوفير المزيد في فاتورتك القادمة."
        
        return "استهلاكك في الحدود الطبيعية. ننصحك دائماً بفصل الأجهزة في ساعات الذروة."

    async def analyze_consumption(self, user_id: str) -> Dict:
        data = await self.fetch_consumption_data(user_id)
        if len(data) < 5:
            return {"status": "Waiting for more data points..."}

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # 1. كشف الشذوذ (Anomaly Detection)
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        df['anomaly'] = iso_forest.fit_predict(df[['consumption_value']])
        anomalies_count = int((df['anomaly'] == -1).sum())

        # 2. التنبؤ بالاستهلاك القادم (Regression)
        df['day_index'] = np.arange(len(df)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(df[['day_index']], df['consumption_value'])
        
        trend = model.coef_[0] # معامل الميل (هل بيزيد ولا بيقل؟)
        prediction = model.predict([[len(df)]])[0]

        # 3. استخراج ساعة الذروة (Peak Hour)
        df['hour'] = df['timestamp'].dt.hour
        peak_hour = int(df.groupby('hour')['consumption_value'].mean().idxmax())

        # 4. توليد النصيحة الذكية
        recommendation = self.generate_ai_recommendation(prediction, trend, anomalies_count)

        return {
            "user_id": user_id,
            "ai_insight": {
                "summary": "تقرير الذكاء الاصطناعي اليومي",
                "recommendation": recommendation,
                "status": "Warning" if anomalies_count > 0 or trend > 1 else "Healthy"
            },
            "forecast": {
                "next_reading_estimate": round(float(prediction), 2),
                "trend_direction": "Upward" if trend > 0 else "Downward",
                "anomalies_detected": anomalies_count
            },
            "energy_profile": {
                "peak_hour_24h": peak_hour,
                "total_usage": round(float(df['consumption_value'].sum()), 2)
            }
        }