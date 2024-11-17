from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from enum import Enum
from datetime import date

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class FitnessLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class WorkoutGoal(str, Enum):
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    FLEXIBILITY = "flexibility"
    OVERALL_FITNESS = "overall_fitness"

class UserPreferences(BaseModel):
    language: str = "en"
    theme: str = "light"
    notifications_enabled: bool = True
    workout_reminders: bool = True
    achievement_notifications: bool = True
    sound_enabled: bool = True
    metrics_system: str = "metric"  # "metric" or "imperial"

class UserPhysicalInfo(BaseModel):
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[HttpUrl] = None
    fitness_level: Optional[FitnessLevel] = None
    workout_goals: Optional[List[WorkoutGoal]] = None
    bio: Optional[str] = None
    physical_info: Optional[UserPhysicalInfo] = None
    preferences: Optional[UserPreferences] = None

class UserProfileResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    photo_url: Optional[HttpUrl] = None
    fitness_level: FitnessLevel
    workout_goals: List[WorkoutGoal]
    bio: Optional[str] = None
    physical_info: UserPhysicalInfo
    preferences: UserPreferences
    created_at: date
    updated_at: date