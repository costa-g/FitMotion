from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.workout import (
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutResponse
)
from app.services.workout_service import WorkoutService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/workouts", tags=["Workouts"])
workout_service = WorkoutService()

@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout: WorkoutCreate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Create a new workout.
    """
    return await workout_service.create_workout(workout, user_data["uid"])

@router.get("/", response_model=List[WorkoutResponse])
async def list_workouts(
    body_area: Optional[str] = None,
    difficulty: Optional[str] = None,
    featured: Optional[bool] = None,
    is_public: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
    user_data: dict = Depends(firebase_auth)
):
    """
    List workouts with optional filters.
    """
    return await workout_service.list_workouts(
        user_id=user_data["uid"],
        body_area=body_area,
        difficulty=difficulty,
        featured=featured,
        is_public=is_public,
        limit=limit,
        offset=offset
    )

@router.get("/featured", response_model=List[WorkoutResponse])
async def get_featured_workouts(
    limit: int = 5,
    _: dict = Depends(firebase_auth)
):
    """
    Get featured workouts.
    """
    return await workout_service.get_featured_workouts(limit)

@router.get("/body-area/{body_area}", response_model=List[WorkoutResponse])
async def get_workouts_by_body_area(
    body_area: str,
    difficulty: Optional[str] = None,
    limit: int = 10,
    _: dict = Depends(firebase_auth)
):
    """
    Get workouts by body area.
    """
    return await workout_service.get_workouts_by_body_area(
        body_area=body_area,
        difficulty=difficulty,
        limit=limit
    )

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Get workout by ID.
    """
    return await workout_service.get_workout(workout_id, user_data["uid"])

@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: str,
    workout: WorkoutUpdate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Update workout by ID.
    Only the owner can update the workout.
    """
    return await workout_service.update_workout(
        workout_id,
        workout,
        user_data["uid"]
    )

@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Delete workout by ID.
    Only the owner can delete the workout.
    """
    return await workout_service.delete_workout(workout_id, user_data["uid"])