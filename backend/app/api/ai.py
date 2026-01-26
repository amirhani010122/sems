from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import httpx
from ..config import settings
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("/analysis")
async def get_consumption_analysis(current_user: dict = Depends(get_current_user)):
    """Get AI analysis of consumption patterns"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ai_service_url}/api/v1/analysis",
                params={"user_id": current_user["id"]},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable"
        )


@router.get("/prediction")
async def get_consumption_prediction(
    days: Optional[int] = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get AI prediction of future consumption"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ai_service_url}/api/v1/prediction",
                params={"user_id": current_user["id"], "days": days},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable"
        )


@router.get("/plan-exhaustion")
async def get_plan_exhaustion_prediction(current_user: dict = Depends(get_current_user)):
    """Get AI prediction of when plan will be exhausted"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ai_service_url}/api/v1/plan-exhaustion",
                params={"user_id": current_user["id"]},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable"
        )


@router.get("/recommendations")
async def get_energy_recommendations(current_user: dict = Depends(get_current_user)):
    """Get AI-generated energy-saving recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ai_service_url}/api/v1/recommendations",
                params={"user_id": current_user["id"]},
                timeout=30.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service unavailable"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable"
        )
