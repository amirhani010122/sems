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
        """إحضار البيانات من الباكيند"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.backend_api_url}/api/internal/consumption",
                    params={"user_id": user_id},
                    headers={"X-Service-Key": "internal-service-key-change-in-production"},
                    timeout=30.0
                )
                return response.json() if response.status_code == 200 else []
            except Exception:
                return []

    async def analyze_consumption(self, user_id: str) -> Dict:
        data = await self.fetch_consumption_data(user_id)
        if len(data) < 5:  # الـ AI يحتاج على الأقل 5 سجلات ليعطي نتائج منطقية
            return {"status": "Need more data for AI analysis"}

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # --- الجزء الأول: اكتشاف الاستهلاك غير الطبيعي (Anomaly Detection) ---
        # الـ AI بيتعلم نمطك وبيدور على الأرقام اللي "مش راكبة" مع الباقي
        iso_forest = IsolationForest(contamination=0.1) # يفترض إن 10% من البيانات قد تكون أخطاء
        df['anomaly'] = iso_forest.fit_predict(df[['consumption_value']])
        anomalies_count = len(df[df['anomaly'] == -1])

        # --- الجزء الثاني: التنبؤ بالمستقبل (Future Prediction) ---
        # بنعلم الموديل العلاقة بين ترتيب الأيام وقيمة الاستهلاك
        df['day_num'] = np.arange(len(df)).reshape(-1, 1)
        model = LinearRegression()
        model.fit(df[['day_num']], df['consumption_value'])
        
        # توقع استهلاك بكره (اليوم التالي في الترتيب)
        next_day_index = np.array([[len(df)]])
        prediction = model.predict(next_day_index)[0]

        # --- الجزء الثالث: حسابات إحصائية ذكية ---
        total = df['consumption_value'].sum()
        peak_hour = df['timestamp'].dt.hour.value_counts().idxmax()

        return {
            "user_id": user_id,
            "ai_report": {
                "summary": "تم تحليل بياناتك باستخدام نماذج تعلم الآلة",
                "predicted_next_consumption": round(float(prediction), 2),
                "anomaly_alert": "نظامنا اكتشف استهلاكاً غير طبيعي" if anomalies_count > 0 else "استهلاكك مستقر",
                "anomalies_found": anomalies_count
            },
            "statistics": {
                "total_kwh": float(total),
                "peak_usage_hour": int(peak_hour),
                "confidence_score": "High" if len(data) > 20 else "Low"
            }
        }