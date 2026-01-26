import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.linear_model import LinearRegression
from .analysis_service import AnalysisService


class PredictionService:
    def __init__(self, backend_api_url: str):
        self.backend_api_url = backend_api_url
        self.analysis_service = AnalysisService(backend_api_url)
    
    async def fetch_consumption_data(self, user_id: str) -> List[Dict]:
        """Fetch consumption data from backend API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.backend_api_url}/api/internal/consumption",
                params={"user_id": user_id},
                headers={"X-Service-Key": "internal-service-key-change-in-production"},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            return []
    
    async def fetch_subscription_data(self, user_id: str) -> Dict:
        """Fetch subscription data from backend API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.backend_api_url}/api/internal/subscription",
                params={"user_id": user_id},
                headers={"X-Service-Key": "internal-service-key-change-in-production"},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            return None
    
    async def predict_consumption(self, user_id: str, days: int = 7) -> Dict:
        """Predict future consumption"""
        data = await self.fetch_consumption_data(user_id)
        
        if not data or len(data) < 2:
            # Not enough data, use average
            avg_daily = 5.0  # Default estimate
            return {
                "user_id": user_id,
                "prediction_days": days,
                "predicted_total_kwh": avg_daily * days,
                "predicted_daily_avg_kwh": avg_daily,
                "method": "default_average",
                "confidence": "low"
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate daily consumption
        daily_consumption = df.groupby(df['timestamp'].dt.date)['consumption_value'].sum().reset_index()
        daily_consumption.columns = ['date', 'consumption']
        daily_consumption = daily_consumption.sort_values('date')
        
        # Simple linear regression for trend
        daily_consumption['day_num'] = range(len(daily_consumption))
        
        if len(daily_consumption) >= 2:
            X = daily_consumption[['day_num']].values
            y = daily_consumption['consumption'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next N days
            last_day = daily_consumption['day_num'].max()
            future_days = np.array([[last_day + i + 1] for i in range(days)])
            predictions = model.predict(future_days)
            
            # Ensure non-negative predictions
            predictions = np.maximum(predictions, 0)
            
            total_predicted = float(predictions.sum())
            avg_predicted = float(predictions.mean())
            
            # Calculate confidence based on data quality
            if len(daily_consumption) >= 7:
                confidence = "high"
            elif len(daily_consumption) >= 3:
                confidence = "medium"
            else:
                confidence = "low"
            
            return {
                "user_id": user_id,
                "prediction_days": days,
                "predicted_total_kwh": total_predicted,
                "predicted_daily_avg_kwh": avg_predicted,
                "daily_predictions": [float(p) for p in predictions],
                "method": "linear_regression",
                "confidence": confidence
            }
        else:
            # Fallback to average
            avg_daily = daily_consumption['consumption'].mean()
            return {
                "user_id": user_id,
                "prediction_days": days,
                "predicted_total_kwh": float(avg_daily * days),
                "predicted_daily_avg_kwh": float(avg_daily),
                "method": "average",
                "confidence": "low"
            }
    
    async def predict_plan_exhaustion(self, user_id: str) -> Dict:
        """Predict when plan will be exhausted"""
        subscription = await self.fetch_subscription_data(user_id)
        
        if not subscription:
            return {
                "user_id": user_id,
                "message": "No active subscription found",
                "exhaustion_date": None
            }
        
        remaining_quota = subscription.get('remaining_quota', 0)
        
        if remaining_quota <= 0:
            return {
                "user_id": user_id,
                "message": "Plan already exhausted",
                "exhaustion_date": datetime.utcnow().isoformat(),
                "remaining_quota_kwh": 0
            }
        
        # Get consumption prediction
        # Use 30 days prediction to estimate daily average
        prediction = await self.predict_consumption(user_id, days=30)
        daily_avg = prediction.get('predicted_daily_avg_kwh', 5.0)
        
        if daily_avg <= 0:
            return {
                "user_id": user_id,
                "message": "Cannot predict - no consumption pattern detected",
                "exhaustion_date": None,
                "remaining_quota_kwh": remaining_quota
            }
        
        # Calculate days until exhaustion
        days_until_exhaustion = remaining_quota / daily_avg
        exhaustion_date = datetime.utcnow() + timedelta(days=int(days_until_exhaustion))
        
        return {
            "user_id": user_id,
            "remaining_quota_kwh": remaining_quota,
            "predicted_daily_consumption_kwh": daily_avg,
            "days_until_exhaustion": int(days_until_exhaustion),
            "exhaustion_date": exhaustion_date.isoformat(),
            "confidence": prediction.get('confidence', 'low')
        }
