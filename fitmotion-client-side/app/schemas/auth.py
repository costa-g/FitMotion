from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class FirebaseAuthResponse(BaseModel):
    idToken: str
    email: str
    refreshToken: str
    expiresIn: str
    localId: str
    registered: Optional[bool] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    uid: str
    email: EmailStr
    displayName: Optional[str] = None
    photoURL: Optional[str] = None
    emailVerified: bool

class PasswordReset(BaseModel):
    email: EmailStr