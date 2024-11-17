from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.movement_analysis import (
    AnalysisRequest,
    MovementAnalysis,
    ExerciseMetrics
)
from app.services.movement_analysis_service import MovementAnalysisService
from app.core.middleware.auth import firebase_auth

router = APIRouter(prefix="/movement-analysis", tags=["Movement Analysis"])
analysis_service = MovementAnalysisService()

@router.post("/analyze", response_model=MovementAnalysis)
async def analyze_movement(
    request: AnalysisRequest,
    user_data: dict = Depends(firebase_auth)
):
    """
    Analyze movement in real-time and provide feedback.
    """
    request.user_id = user_data["uid"]
    return await analysis_service.analyze_movement(request)

@router.post("/metrics", response_model=ExerciseMetrics)
async def calculate_metrics(
    exercise_id: str,
    duration: float,
    form_analysis: dict,
    user_data: dict = Depends(firebase_auth)
):
    """
    Calculate exercise metrics based on the movement analysis.
    """
    return await analysis_service.calculate_exercise_metrics(
        user_id=user_data["uid"],
        exercise_id=exercise_id,
        duration=duration,
        form_analysis=form_analysis
    )