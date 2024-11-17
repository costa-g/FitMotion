from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user_profile import (
    UserProfileUpdate,
    UserProfileResponse,
    UserPreferences,
    UserPhysicalInfo
)
from app.services.user_profile_service import UserProfileService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/profile", tags=["User Profile"])
profile_service = UserProfileService()

@router.get("/", response_model=UserProfileResponse)
async def get_profile(user_data: dict = Depends(firebase_auth)):
    """
    Get current user's profile.
    """
    return await profile_service.get_profile(user_data["uid"])

@router.put("/", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Update user's profile information.
    """
    return await profile_service.update_profile(
        user_data["uid"],
        profile_data
    )

@router.put("/preferences", response_model=UserProfileResponse)
async def update_preferences(
    preferences: UserPreferences,
    user_data: dict = Depends(firebase_auth)
):
    """
    Update user's preferences.
    """
    return await profile_service.update_preferences(
        user_data["uid"],
        preferences
    )

@router.put("/physical-info", response_model=UserProfileResponse)
async def update_physical_info(
    physical_info: UserPhysicalInfo,
    user_data: dict = Depends(firebase_auth)
):
    """
    Update user's physical information.
    """
    return await profile_service.update_physical_info(
        user_data["uid"],
        physical_info
    )