from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    FirebaseAuthResponse,
    PasswordReset,
    UserResponse
)
from app.services.auth_service import AuthService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/register", response_model=FirebaseAuthResponse)
async def register(user_data: UserCreate):
    """
    Register a new user with email and password.
    Returns Firebase authentication tokens.
    """
    return await auth_service.create_user(user_data)

@router.post("/login", response_model=FirebaseAuthResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    Returns Firebase authentication tokens.
    """
    return await auth_service.login_user(credentials)

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """
    Send password reset email.
    """
    return await auth_service.reset_password(reset_data.email)

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_data: dict = Depends(firebase_auth)):
    """
    Get current authenticated user info.
    Requires Firebase ID token in Authorization header.
    """
    try:
        user = auth.get_user(user_data['uid'])
        return UserResponse(
            uid=user.uid,
            email=user.email,
            displayName=user.display_name,
            photoURL=user.photo_url,
            emailVerified=user.email_verified
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )