from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse
)
from app.services.exercise_service import ExerciseService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/exercises", tags=["Exercises"])
exercise_service = ExerciseService()

@router.post("/", response_model=ExerciseResponse)
async def create_exercise(
    exercise: ExerciseCreate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Create a new exercise.
    Only admin users can create exercises.
    """
    if not user_data.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create exercises"
        )
    return await exercise_service.create_exercise(exercise)

@router.get("/", response_model=List[ExerciseResponse])
async def list_exercises(
    muscle_group: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    _: dict = Depends(firebase_auth)
):
    """
    List exercises with optional filters.
    """
    return await exercise_service.list_exercises(
        muscle_group=muscle_group,
        difficulty=difficulty,
        limit=limit,
        offset=offset
    )

@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    _: dict = Depends(firebase_auth)
):
    """
    Get exercise by ID.
    """
    return await exercise_service.get_exercise(exercise_id)

@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: str,
    exercise: ExerciseUpdate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Update exercise by ID.
    Only admin users can update exercises.
    """
    if not user_data.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update exercises"
        )
    return await exercise_service.update_exercise(exercise_id, exercise)

@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Delete exercise by ID.
    Only admin users can delete exercises.
    """
    if not user_data.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete exercises"
        )
    await exercise_service.delete_exercise(exercise_id)
    return {"message": "Exercise deleted successfully"}