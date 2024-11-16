from pydantic import BaseModel
from typing import List, Optional

class KeyPoint(BaseModel):
    description: str
    importance: str  # "high", "medium", "low"

class Position(BaseModel):
    x: float
    y: float
    z: float

class CorrectPositions(BaseModel):
    startPosition: Position
    endPosition: Position
    keyFrames: List[Position]

class ExerciseBase(BaseModel):
    name: str
    description: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    muscleGroups: List[str]
    keyPoints: List[KeyPoint]
    duration: Optional[int] = None  # "seconds"
    reps: Optional[int] = None 
    sets: Optional[int] = None
    restTime: Optional[int] = None  # "seconds"

class ExerciseCreate(ExerciseBase):
    correctPositions: CorrectPositions
    mediaUrls: List[str] = None

class ExerciseUpdate(ExerciseBase):
    correctPositions: Optional[CorrectPositions] = None
    mediaUrls: List[str] = None

class ExerciseResponse(ExerciseBase):
    id: str
    correctPositions: CorrectPositions
    mediaUrls: List[str] = None