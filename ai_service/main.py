from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
from .config import settings
from .services.analysis_service import AnalysisService
from .services.prediction_service import PredictionService
from .services.recommendation_service import RecommendationService

app = FastAPI(
    title="SEMS AI Service",
    description="AI Analysis and Prediction Service for SEMS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analysis_service = AnalysisService(settings.backend_api_url)
prediction_service = PredictionService(settings.backend_api_url)
recommendation_service = RecommendationService(settings.backend_api_url)


@app.get("/")
async def root():
    return {"message": "SEMS AI Service"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/analysis")
async def get_analysis(user_id: str = Query(...)):
    """Analyze consumption patterns"""
    try:
        result = await analysis_service.analyze_consumption(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/prediction")
async def get_prediction(user_id: str = Query(...), days: int = Query(7)):
    """Predict future consumption"""
    try:
        result = await prediction_service.predict_consumption(user_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/plan-exhaustion")
async def get_plan_exhaustion(user_id: str = Query(...)):
    """Predict when plan will be exhausted"""
    try:
        result = await prediction_service.predict_plan_exhaustion(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recommendations")
async def get_recommendations(user_id: str = Query(...)):
    """Get energy-saving recommendations"""
    try:
        result = await recommendation_service.get_recommendations(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.ai_service_host, port=settings.ai_service_port)
