import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List


class AnalysisService:
    def __init__(self, backend_api_url: str):
        self.backend_api_url = backend_api_url
    
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
    
    async def analyze_consumption(self, user_id: str) -> Dict:
        """Analyze consumption patterns"""
        data = await self.fetch_consumption_data(user_id)
        
        if not data:
            return {
                "user_id": user_id,
                "analysis": "No consumption data available",
                "patterns": {},
                "statistics": {}
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate statistics
        total_consumption = df['consumption_value'].sum()
        avg_daily = df.groupby(df['timestamp'].dt.date)['consumption_value'].sum().mean()
        max_daily = df.groupby(df['timestamp'].dt.date)['consumption_value'].sum().max()
        min_daily = df.groupby(df['timestamp'].dt.date)['consumption_value'].sum().min()
        
        # Identify patterns
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['date'] = df['timestamp'].dt.date
        
        hourly_pattern = df.groupby('hour')['consumption_value'].mean().to_dict()
        daily_pattern = df.groupby('day_of_week')['consumption_value'].sum().to_dict()
        
        # Peak hours
        peak_hour = max(hourly_pattern.items(), key=lambda x: x[1])[0]
        
        # Trend analysis (simple linear trend)
        daily_consumption = df.groupby('date')['consumption_value'].sum().reset_index()
        daily_consumption['day_num'] = range(len(daily_consumption))
        
        if len(daily_consumption) > 1:
            trend_coef = np.polyfit(daily_consumption['day_num'], daily_consumption['consumption_value'], 1)[0]
            trend_direction = "increasing" if trend_coef > 0 else "decreasing"
        else:
            trend_direction = "stable"
        
        return {
            "user_id": user_id,
            "analysis": "Consumption pattern analysis completed",
            "statistics": {
                "total_consumption_kwh": float(total_consumption),
                "average_daily_kwh": float(avg_daily),
                "max_daily_kwh": float(max_daily),
                "min_daily_kwh": float(min_daily),
                "data_points": len(data)
            },
            "patterns": {
                "peak_hour": int(peak_hour),
                "hourly_distribution": {str(k): float(v) for k, v in hourly_pattern.items()},
                "daily_distribution": {str(k): float(v) for k, v in daily_pattern.items()},
                "trend": trend_direction
            }
        }
