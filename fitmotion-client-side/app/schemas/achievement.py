from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class AchievementType(str, Enum):
    WORKOUT_COUNT = "workout_count"
    EXERCISE_MASTERY = "exercise_mastery"
    STREAK = "streak"
    PERFORMANCE = "performance"
    MILESTONE = "milestone"
    SPECIAL = "special"

class AchievementTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class AchievementCriteria(BaseModel):
    type: AchievementType
    value: int
    comparison: str  # "gte", "eq", "lte"
    period_days: Optional[int] = None

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    type: AchievementType
    tier: AchievementTier
    icon_url: str
    points: int
    criteria: AchievementCriteria
    is_secret: bool = False

class UserAchievement(BaseModel):
    achievement_id: str
    unlocked_at: datetime
    progress: float  # 0 to 100
    current_value: int

class UserAchievementProgress(BaseModel):
    user_id: str
    achievements: List[UserAchievement]
    total_points: int
    rank: Optional[str] = None