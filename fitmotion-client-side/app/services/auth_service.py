from firebase_admin import auth
from fastapi import HTTPException, status
from app.schemas.auth import UserCreate, UserLogin, FirebaseAuthResponse
from app.services.firebase_service import FirebaseService
import httpx
from app.core.config.settings import settings

class AuthService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.api_key = settings.FIREBASE_API_KEY

    async def create_user(self, user_data: UserCreate) -> FirebaseAuthResponse:
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "email": user_data.email,
                    "password": user_data.password,
                    "returnSecureToken": True
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("error", {}).get("message")
                    )

                auth_data = FirebaseAuthResponse(**response.json())

                await self.update_user_profile(auth_data.localId, user_data.full_name)

                await self.firebase.set_document('users', auth_data.localId, {
                    'email': user_data.email,
                    'full_name': user_data.full_name,
                    'created_at': self.firebase.timestamp(),
                    'updated_at': self.firebase.timestamp()
                })

                return auth_data

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def login_user(self, credentials: UserLogin) -> FirebaseAuthResponse:
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "email": credentials.email,
                    "password": credentials.password,
                    "returnSecureToken": True
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("error", {}).get("message")
                    )

                return FirebaseAuthResponse(**response.json())

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_user_profile(self, user_id: str, display_name: str) -> None:
        try:
            auth.update_user(
                user_id,
                display_name=display_name
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def verify_id_token(self, id_token: str) -> dict:
        try:
            return auth.verify_id_token(id_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    async def reset_password(self, email: str) -> dict:
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "requestType": "PASSWORD_RESET",
                    "email": email
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json().get("error", {}).get("message")
                    )

                return {"message": "Password reset email sent successfully"}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )