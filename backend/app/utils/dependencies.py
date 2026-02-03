from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..database import get_database
from ..utils.auth import verify_token
from ..models.user import User
from typing import Optional

security = HTTPBearer(auto_error=False)


async def get_current_user(
#     credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
# ) -> dict:
#     """Get current authenticated user from JWT token"""
#     token = credentials.credentials
#     payload = verify_token(token)
    
#     if payload is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    
    # 3. فحص يدوي: لو مفيش Token، ارمي 401 بدل 403 المبهمة
    if not credentials:
        print("DEBUG: No Authorization header found!") # هتظهر لك في الـ Terminal
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )

    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        print(f"DEBUG: Token verification failed for token: {token[:10]}...") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        

    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db = get_database()
    user = await db.users.find_one({"email": email})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"]
    }
