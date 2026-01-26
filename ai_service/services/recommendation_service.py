import httpx
import pandas as pd
from datetime import datetime
from typing import Dict, List
from .analysis_service import AnalysisService


class RecommendationService:
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
    
    async def get_recommendations(self, user_id: str) -> Dict:
        """Generate personalized energy-saving recommendations"""
        # Get analysis
        analysis = await self.analysis_service.analyze_consumption(user_id)
        subscription = await self.fetch_subscription_data(user_id)
        
        recommendations = []
        
        # Analyze patterns and generate recommendations
        if 'patterns' in analysis:
            patterns = analysis['patterns']
            
            # Peak hour recommendation
            peak_hour = patterns.get('peak_hour', None)
            if peak_hour is not None:
                if peak_hour >= 18 and peak_hour <= 22:
                    recommendations.append({
                        "type": "peak_hour_usage",
                        "priority": "high",
                        "title": "Reduce Peak Hour Usage",
                        "description": f"Your peak consumption is between {peak_hour}:00. Consider shifting heavy appliance usage to off-peak hours (late night or early morning) to reduce costs.",
                        "estimated_savings": "10-15%"
                    })
            
            # Trend recommendation
            trend = patterns.get('trend', 'stable')
            if trend == 'increasing':
                recommendations.append({
                    "type": "increasing_trend",
                    "priority": "medium",
                    "title": "Consumption Trend Alert",
                    "description": "Your energy consumption is showing an increasing trend. Review your usage patterns and identify appliances consuming excessive energy.",
                    "estimated_savings": "5-10%"
                })
        
        # Usage percentage recommendation
        if subscription:
            remaining = subscription.get('remaining_quota', 0)
            # We need total quota - would need to fetch plan details
            # For now, use a generic recommendation
            if remaining < 100:  # Assuming low remaining
                recommendations.append({
                    "type": "quota_warning",
                    "priority": "high",
                    "title": "Plan Quota Running Low",
                    "description": f"You have {remaining:.2f} kWh remaining. Consider reducing non-essential usage to extend your plan duration.",
                    "estimated_savings": "Extend plan by 2-3 days"
                })
        
        # General recommendations
        recommendations.extend([
            {
                "type": "appliance_efficiency",
                "priority": "medium",
                "title": "Upgrade to Energy-Efficient Appliances",
                "description": "Consider replacing old appliances with ENERGY STAR certified models. They consume 10-50% less energy.",
                "estimated_savings": "15-30%"
            },
            {
                "type": "smart_thermostat",
                "priority": "low",
                "title": "Use Smart Thermostat",
                "description": "A programmable thermostat can help optimize heating and cooling, reducing energy waste.",
                "estimated_savings": "10-15%"
            },
            {
                "type": "unplug_devices",
                "priority": "low",
                "title": "Unplug Unused Devices",
                "description": "Many devices consume energy even when turned off. Unplug chargers and electronics when not in use.",
                "estimated_savings": "5-10%"
            }
        ])
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "generated_at": datetime.utcnow().isoformat()
        }
