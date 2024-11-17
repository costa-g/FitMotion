from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.achievement import (
    Achievement,
    UserAchievement,
    UserAchievementProgress
)
from app.services.achievement_service import AchievementService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/achievements", tags=["Achievements"])
achievement_service = AchievementService()

@router.get("/check", response_model=List[Achievement])
async def check_achievements(
    user_data: dict = Depends(firebase_auth)
):
    """
    Check and unlock new achievements for the user.
    """
    return await achievement_service.check_achievements(user_data["uid"])

@router.get("/progress", response_model=UserAchievementProgress)
async def get_achievement_progress(
    user_data: dict = Depends(firebase_auth)
):
    """
    Get user's achievement progress.
    """
    return await achievement_service.get_user_progress(user_data["uid"])

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    _: dict = Depends(firebase_auth)
):
    """
    Get achievement leaderboard.
    """
    return await achievement_service.get_leaderboard(limit)

@router.get("/available", response_model=List[Achievement])
async def get_available_achievements(
    type: Optional[str] = None,
    _: dict = Depends(firebase_auth)
):
    """
    Get list of available achievements.
    """
    return await achievement_service.get_available_achievements(type)