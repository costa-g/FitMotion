from fastapi import HTTPException, status
from app.schemas.achievement import (
    Achievement,
    UserAchievement,
    AchievementType,
    AchievementCriteria
)
from app.services.firebase_service import FirebaseService
from datetime import datetime, timedelta
from typing import List, Dict

class AchievementService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = 'achievements'
        self.user_achievements_collection = 'user_achievements'

    async def check_achievements(self, user_id: str) -> List[Achievement]:
        """Verifica e atualiza conquistas do usuário"""
        try:
            # Buscar todas as conquistas disponíveis
            achievements = await self.firebase.query_collection(self.collection)
            
            # Buscar progresso atual do usuário
            user_progress = await self.firebase.get_document('user_progress', user_id)
            user_achievements = await self.firebase.get_document(
                self.user_achievements_collection,
                user_id
            ) or {'achievements': []}

            # Conquistas já desbloqueadas
            unlocked_ids = [a['achievement_id'] for a in user_achievements['achievements']]
            newly_unlocked = []

            for achievement in achievements:
                if achievement['id'] not in unlocked_ids:
                    if await self._check_achievement_criteria(
                        achievement['criteria'],
                        user_progress,
                        user_id
                    ):
                        # Desbloquear nova conquista
                        new_achievement = UserAchievement(
                            achievement_id=achievement['id'],
                            unlocked_at=datetime.now(),
                            progress=100,
                            current_value=await self._get_current_value(
                                achievement['criteria'],
                                user_progress
                            )
                        )
                        
                        user_achievements['achievements'].append(
                            new_achievement.dict()
                        )
                        newly_unlocked.append(achievement)

            if newly_unlocked:
                # Atualizar conquistas do usuário
                await self.firebase.update_document(
                    self.user_achievements_collection,
                    user_id,
                    {'achievements': user_achievements['achievements']}
                )

            return newly_unlocked

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check achievements: {str(e)}"
            )

    async def _check_achievement_criteria(
        self,
        criteria: AchievementCriteria,
        user_progress: dict,
        user_id: str
    ) -> bool:
        """Verifica se um critério específico foi atingido"""
        try:
            current_value = await self._get_current_value(criteria, user_progress)
            
            if criteria.comparison == "gte":
                return current_value >= criteria.value
            elif criteria.comparison == "eq":
                return current_value == criteria.value
            elif criteria.comparison == "lte":
                return current_value <= criteria.value
            
            return False

        except Exception:
            return False

    async def _get_current_value(
        self,
        criteria: AchievementCriteria,
        user_progress: dict
    ) -> int:
        """Obtém o valor atual para um critério específico"""
        if criteria.type == AchievementType.WORKOUT_COUNT:
            return user_progress.get('total_workouts', 0)
            
        elif criteria.type == AchievementType.EXERCISE_MASTERY:
            exercise_stats = user_progress.get('exercises', {})
            return max(
                [ex.get('total_sets', 0) for ex in exercise_stats.values()],
                default=0
            )
            
        elif criteria.type == AchievementType.STREAK:
            return await self._calculate_streak(user_progress)
            
        elif criteria.type == AchievementType.PERFORMANCE:
            return int(user_progress.get('average_performance', 0) * 100)
            
        return 0

    async def _calculate_streak(self, user_progress: dict) -> int:
        """Calcula a sequência atual de dias de treino"""
        workout_dates = sorted(
            [w['date'] for w in user_progress.get('workout_history', [])],
            reverse=True
        )
        
        if not workout_dates:
            return 0

        streak = 1
        current_date = workout_dates[0].date()
        
        for date in workout_dates[1:]:
            date = date.date()
            if (current_date - date).days == 1:
                streak += 1
                current_date = date
            elif (current_date - date).days > 1:
                break
                
        return streak

    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Obtém o ranking de usuários baseado em pontos de conquistas"""
        try:
            users = await self.firebase.query_collection(
                self.user_achievements_collection,
                order_by=('total_points', 'DESCENDING'),
                limit=limit
            )

            leaderboard = []
            for idx, user in enumerate(users):
                user_data = await self.firebase.get_document('users', user['user_id'])
                leaderboard.append({
                    'rank': idx + 1,
                    'user_id': user['user_id'],
                    'name': user_data.get('full_name', 'Unknown User'),
                    'points': user['total_points'],
                    'achievements_count': len(user['achievements'])
                })

            return leaderboard

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get leaderboard: {str(e)}"
            )