from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WorkoutExercise(BaseModel):
    exerciseId: str
    sets: int
    reps: Optional[int] = None
    duration: Optional[int] = None  # "seconds"
    restTime: int  # "seconds"
    order: int

class WorkoutBase(BaseModel):
    name: str
    description: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    bodyArea: str
    estimatedTime: int  # "minutes"
    calories: int
    featured: bool = False

class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExercise]

class WorkoutUpdate(WorkoutBase):
    exercises: Optional[List[WorkoutExercise]] = None

class WorkoutResponse(WorkoutBase):
    id: str
    exercises: List[WorkoutExercise]
    thumbnail: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime