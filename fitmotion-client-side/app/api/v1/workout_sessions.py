from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.schemas.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSessionResponse,
    ExerciseSet,
    SessionStatus
)
from app.services.workout_session_service import WorkoutSessionService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/workout-sessions", tags=["Workout Sessions"])
session_service = WorkoutSessionService()

@router.post("/", response_model=WorkoutSessionResponse)
async def create_session(
    session_data: WorkoutSessionCreate,
    user_data: dict = Depends(firebase_auth)
):
    """
    Create a new workout session.
    """
    return await session_service.create_session(session_data, user_data["uid"])

@router.post("/{session_id}/start", response_model=WorkoutSessionResponse)
async def start_session(
    session_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Start a workout session.
    """
    return await session_service.start_session(session_id, user_data["uid"])

@router.post("/{session_id}/exercises/{exercise_id}", response_model=WorkoutSessionResponse)
async def complete_exercise(
    session_id: str,
    exercise_id: str,
    set_data: ExerciseSet,
    user_data: dict = Depends(firebase_auth)
):
    """
    Record completed exercise set in a session.
    """
    return await session_service.complete_exercise(
        session_id,
        exercise_id,
        set_data,
        user_data["uid"]
    )

@router.post("/{session_id}/complete", response_model=WorkoutSessionResponse)
async def complete_session(
    session_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Complete a workout session.
    """
    return await session_service.complete_session(session_id, user_data["uid"])

@router.get("/progress", response_model=dict)
async def get_user_progress(
    user_data: dict = Depends(firebase_auth)
):
    """
    Get user's overall workout progress.
    """
    return await session_service.get_user_progress(user_data["uid"])

@router.get("/history", response_model=List[WorkoutSessionResponse])
async def get_session_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[SessionStatus] = None,
    limit: int = 10,
    offset: int = 0,
    user_data: dict = Depends(firebase_auth)
):
    """
    Get user's workout session history with optional filters.
    """
    return await session_service.get_session_history(
        user_data["uid"],
        start_date,
        end_date,
        status,
        limit,
        offset
    )

@router.get("/{session_id}", response_model=WorkoutSessionResponse)
async def get_session(
    session_id: str,
    user_data: dict = Depends(firebase_auth)
):
    """
    Get details of a specific workout session.
    """
    return await session_service.get_session(session_id, user_data["uid"])