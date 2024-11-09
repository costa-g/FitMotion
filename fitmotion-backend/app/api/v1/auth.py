from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, PasswordReset
from app.services.auth_service import AuthService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    return await auth_service.create_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password.
    """
    return await auth_service.login_user(credentials)

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """
    Send password reset email.
    """
    return await auth_service.reset_password(reset_data.email)

@router.get("/me")
async def get_current_user(token: str = Depends(firebase_auth)):
    """
    Get current authenticated user info.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        user = auth.get_user(decoded_token['uid'])
        return {
            "id": user.uid,
            "email": user.email,
            "full_name": user.display_name,
            "photo_url": user.photo_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )