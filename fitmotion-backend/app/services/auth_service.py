from firebase_admin import auth
from fastapi import HTTPException, status
from app.schemas.auth import UserCreate, UserLogin
from app.services.firebase_service import FirebaseService
import asyncio

class AuthService:
    def __init__(self):
        self.firebase = FirebaseService()

    async def create_user(self, user_data: UserCreate) -> dict:
        try:
            # Criar usuário no Firebase Auth
            user = auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.full_name
            )

            # Criar documento do usuário no Firestore
            await self.firebase.db.collection('users').document(user.uid).set({
                'email': user_data.email,
                'full_name': user_data.full_name,
                'photo_url': user.photo_url,
                'created_at': self.firebase.timestamp(),
                'updated_at': self.firebase.timestamp()
            })

            # Gerar token personalizado
            token = await self.create_custom_token(user.uid)

            return {
                'access_token': token,
                'token_type': 'bearer',
                'user_id': user.uid
            }

        except auth.EmailAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def login_user(self, credentials: UserLogin) -> dict:
        try:
            # Verificar credenciais no Firebase Auth
            user = auth.get_user_by_email(credentials.email)
            
            # Gerar token personalizado
            token = await self.create_custom_token(user.uid)

            return {
                'access_token': token,
                'token_type': 'bearer',
                'user_id': user.uid
            }

        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def create_custom_token(self, user_id: str) -> str:
        try:
            return auth.create_custom_token(user_id).decode('utf-8')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating custom token: {str(e)}"
            )

    async def verify_token(self, token: str) -> dict:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    async def reset_password(self, email: str) -> dict:
        try:
            reset_link = auth.generate_password_reset_link(email)
            # Aqui você poderia enviar o email com o link
            return {"message": "Password reset link sent successfully"}
        except auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )