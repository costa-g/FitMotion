from pydantic import BaseModel
from typing import List, Optional

class BodyAreaBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class BodyAreaCreate(BodyAreaBase):
    pass

class BodyAreaUpdate(BodyAreaBase):
    pass

class BodyAreaResponse(BodyAreaBase):
    id: str
    workoutCount: int