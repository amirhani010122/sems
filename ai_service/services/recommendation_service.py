import httpx
import pandas as pd
from datetime import datetime
from typing import Dict, List
from .analysis_service import AnalysisService

class RecommendationService:
    def __init__(self, backend_api_url: str):
        self.backend_api_url = backend_api_url
        self.analysis_service = AnalysisService(backend_api_url)
    
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

    async def get_recommendations(self, user_id: str) -> Dict:
        """توليد توصيات ذكية جداً بناءً على تحليل الـ AI"""
        # جلب التحليل المتطور من الـ AnalysisService اللي طورناه سوا
        analysis_result = await self.analysis_service.analyze_consumption(user_id)
        subscription = await self.fetch_subscription_data(user_id)
        
        recommendations = []

        # 1. تحليل الشذوذ (Anomaly) - أولوية قصوى
        if analysis_result.get("forecast", {}).get("anomalies_detected", 0) > 0:
            recommendations.append({
                "type": "emergency",
                "priority": "CRITICAL",
                "title": "فحص فوري للأجهزة",
                "description": "لقد اكتشف الذكاء الاصطناعي قفزة غير طبيعية في استهلاكك. قد يكون هناك عطل في أحد الأجهزة أو تسريب كهربائي.",
                "action": "تأكد من إطفاء الأجهزة غير المستخدمة حالياً وفحص التوصيلات."
            })

        # 2. تحليل ساعة الذروة (Peak Hour) - أولوية عالية
        peak_hour = analysis_result.get("energy_profile", {}).get("peak_usage_hour_24h")
        if peak_hour is not None:
            time_str = f"{peak_hour}:00"
            recommendations.append({
                "type": "optimization",
                "priority": "HIGH",
                "title": "تغيير وقت الاستخدام الكثيف",
                "description": f"معظم استهلاكك يتركز الساعة {time_str}. نقل استخدام الأجهزة الثقيلة (غسالة، سخان) إلى وقت مبكر سيوفر لك في الشريحة.",
                "estimated_savings": "12% من قيمة الفاتورة"
            })

        # 3. تحليل الاتجاه (Trend)
        trend = analysis_result.get("forecast", {}).get("trend_direction")
        if trend == "Upward":
            recommendations.append({
                "type": "alert",
                "priority": "MEDIUM",
                "title": "منحنى الاستهلاك في تصاعد",
                "description": "استهلاكك يزداد يومياً بشكل تدريجي. ننصحك بمراجعة إعدادات التكييف أو السخان لتقليل هذا النمو.",
                "estimated_savings": "50-100 جنيه شهرياً"
            })

        # 4. نصيحة الباقة (Subscription)
        if subscription:
            remaining = subscription.get("remaining_quota", 0)
            if remaining < 50:
                recommendations.append({
                    "type": "budget",
                    "priority": "HIGH",
                    "title": "اقتراب نفاذ الرصيد",
                    "description": f"باقي لديك {round(remaining, 1)} كيلوواط فقط. فعل 'وضع التوفير' الآن لضمان استمرار الخدمة ليومين إضافيين.",
                    "action": "إعادة شحن الرصيد"
                })

        # 5. نصيحة ذكية عامة (بناءً على التوقعات)
        prediction = analysis_result.get("forecast", {}).get("next_reading_estimate", 0)
        if prediction > 30: # لو التوقع عالي
            recommendations.append({
                "type": "general",
                "priority": "LOW",
                "title": "نصيحة الصيف/الشتاء",
                "description": "توقعاتنا تشير لاستهلاك عالٍ غداً. تأكد من ضبط التكييف على 24 درجة لتوفير الطاقة.",
                "estimated_savings": "20%"
            })

        return {
            "user_id": user_id,
            "status": analysis_result.get("ai_insight", {}).get("status", "Healthy"),
            "top_recommendation": recommendations[0] if recommendations else None,
            "all_recommendations": sorted(recommendations, key=lambda x: x['priority'] == 'CRITICAL', reverse=True),
            "generated_at": datetime.utcnow().isoformat()
        }