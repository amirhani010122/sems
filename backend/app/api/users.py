from fastapi import APIRouter, Depends
from ..schemas.user import UserResponse
from ..utils.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
