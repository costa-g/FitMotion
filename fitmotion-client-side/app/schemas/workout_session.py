from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ExerciseSet(BaseModel):
    reps: Optional[int] = None
    duration: Optional[int] = None  # em segundos
    weight: Optional[float] = None
    performance_score: float
    form_score: float
    feedback: List[str]

class SessionExercise(BaseModel):
    exercise_id: str
    sets: List[ExerciseSet]
    completed: bool = False
    notes: Optional[str] = None

class WorkoutSessionCreate(BaseModel):
    workout_id: str
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None

class WorkoutSessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    notes: Optional[str] = None

class ExerciseProgress(BaseModel):
    exercise_id: str
    total_sets: int
    total_reps: int
    average_performance: float
    average_form_score: float
    improvement_rate: float
    best_performance: float
    last_performance: float

class WorkoutSessionResponse(BaseModel):
    id: str
    workout_id: str
    user_id: str
    status: SessionStatus
    exercises: List[SessionExercise]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]  # em segundos
    calories_burned: Optional[float]
    total_exercises: int
    completed_exercises: int
    average_performance: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime