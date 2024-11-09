from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from firebase_admin import auth
from typing import Optional

class FirebaseAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(FirebaseAuth, self).__init__(auto_error=auto_error)
        self.auth_service = AuthService()

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )

        try:
            decoded_token = await self.auth_service.verify_token(credentials.credentials)
            request.state.user = decoded_token
            return credentials.credentials
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )

firebase_auth = FirebaseAuth()