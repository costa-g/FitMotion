from fastapi import HTTPException, status
from app.schemas.user_profile import (
    UserProfileUpdate,
    UserProfileResponse,
    UserPreferences,
    UserPhysicalInfo
)
from app.services.firebase_service import FirebaseService
from datetime import datetime
from typing import Optional
import firebase_admin.auth as auth

class UserProfileService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = 'user_profiles'

    async def get_profile(self, user_id: str) -> UserProfileResponse:
        try:
            # Buscar dados do Auth
            auth_user = auth.get_user(user_id)
            
            # Buscar perfil do Firestore
            profile = await self.firebase.get_document(self.collection, user_id)
            
            if not profile:
                # Criar perfil padrão se não existir
                profile = await self._create_default_profile(auth_user)

            return UserProfileResponse(
                id=user_id,
                full_name=auth_user.display_name,
                email=auth_user.email,
                photo_url=auth_user.photo_url,
                **profile
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user profile: {str(e)}"
            )

    async def update_profile(
        self,
        user_id: str,
        profile_data: UserProfileUpdate
    ) -> UserProfileResponse:
        try:
            # Atualizar dados no Auth se necessário
            auth_update = {}
            if profile_data.full_name:
                auth_update['display_name'] = profile_data.full_name
            if profile_data.photo_url:
                auth_update['photo_url'] = str(profile_data.photo_url)
            
            if auth_update:
                auth.update_user(user_id, **auth_update)

            # Atualizar dados no Firestore
            update_data = profile_data.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.now()
            
            await self.firebase.update_document(
                self.collection,
                user_id,
                update_data
            )

            return await self.get_profile(user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user profile: {str(e)}"
            )

    async def update_preferences(
        self,
        user_id: str,
        preferences: UserPreferences
    ) -> UserProfileResponse:
        try:
            await self.firebase.update_document(
                self.collection,
                user_id,
                {'preferences': preferences.dict()}
            )
            return await self.get_profile(user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update preferences: {str(e)}"
            )

    async def update_physical_info(
        self,
        user_id: str,
        physical_info: UserPhysicalInfo
    ) -> UserProfileResponse:
        try:
            # Salvar histórico de medidas
            history_update = {
                'physical_info': physical_info.dict(),
                'physical_info_history': self.firebase.array_union([{
                    'date': datetime.now(),
                    **physical_info.dict(exclude_unset=True)
                }])
            }
            
            await self.firebase.update_document(
                self.collection,
                user_id,
                history_update
            )

            return await self.get_profile(user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update physical info: {str(e)}"
            )

    async def _create_default_profile(self, auth_user) -> dict:
        """Cria um perfil padrão para novo usuário"""
        default_profile = {
            'fitness_level': 'beginner',
            'workout_goals': ['overall_fitness'],
            'preferences': UserPreferences().dict(),
            'physical_info': UserPhysicalInfo().dict(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        await self.firebase.set_document(
            self.collection,
            auth_user.uid,
            default_profile
        )

        return default_profile