from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class Point(BaseModel):
    x: float
    y: float
    confidence: float

class Keypoint(BaseModel):
    name: str
    point: Point

class Frame(BaseModel):
    keypoints: List[Keypoint]
    timestamp: float

class MovementPhase(str, Enum):
    PREPARATION = "preparation"
    EXECUTION = "execution"
    COMPLETION = "completion"

class FeedbackType(str, Enum):
    FORM = "form"
    PACE = "pace"
    RANGE = "range"
    STABILITY = "stability"

class MovementFeedback(BaseModel):
    type: FeedbackType
    message: str
    confidence: float
    timestamp: float
    keypoints: Optional[List[str]] = None

class AnalysisRequest(BaseModel):
    exercise_id: str
    frames: List[Frame]
    user_id: str

class MovementAnalysis(BaseModel):
    exercise_id: str
    accuracy: float
    current_phase: MovementPhase
    rep_count: Optional[int]
    duration: Optional[float]
    feedback: List[MovementFeedback]
    form_score: float
    recommendations: List[str]

class ExerciseMetrics(BaseModel):
    total_reps: int
    total_duration: float
    average_accuracy: float
    calories_burned: float
    form_score: float