from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from ..database import get_database
from ..schemas.auth import UserRegister, UserLogin, Token
from ..utils.auth import get_password_hash, verify_password, create_access_token
from ..config import settings

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = {
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hashed_password
    }
    
    result = await db.users.insert_one(user_dict)
    
    return {
        "id": str(result.inserted_id),
        "email": user_data.email,
        "username": user_data.username,
        "message": "User registered successfully"
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login and get access token"""
    db = get_database()
    
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
