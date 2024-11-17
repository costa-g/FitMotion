from fastapi import HTTPException, status
from app.schemas.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    SessionStatus,
    ExerciseSet
)
from app.services.firebase_service import FirebaseService
from app.services.workout_service import WorkoutService
from datetime import datetime, timezone
from typing import List, Optional

class WorkoutSessionService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.workout_service = WorkoutService()
        self.collection = 'workout_sessions'

    async def create_session(
        self,
        session_data: WorkoutSessionCreate,
        user_id: str
    ) -> dict:
        try:
            # Verificar se o workout existe
            workout = await self.workout_service.get_workout(
                session_data.workout_id,
                user_id
            )

            # Criar estrutura inicial da sessão
            session = {
                'workout_id': session_data.workout_id,
                'user_id': user_id,
                'status': SessionStatus.PENDING,
                'exercises': [
                    {
                        'exercise_id': exercise['exerciseId'],
                        'sets': [],
                        'completed': False
                    }
                    for exercise in workout['exercises']
                ],
                'start_time': None,
                'end_time': None,
                'duration': 0,
                'calories_burned': 0,
                'total_exercises': len(workout['exercises']),
                'completed_exercises': 0,
                'average_performance': 0,
                'notes': session_data.notes,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }

            # Salvar no Firestore
            doc_ref = self.firebase.db.collection(self.collection).document()
            session['id'] = doc_ref.id
            await self.firebase.set_document(self.collection, doc_ref.id, session)

            return session

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create workout session: {str(e)}"
            )

    async def start_session(self, session_id: str, user_id: str) -> dict:
        try:
            session = await self.get_session(session_id, user_id)
            
            if session['status'] != SessionStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session can only be started from PENDING status"
                )

            update_data = {
                'status': SessionStatus.IN_PROGRESS,
                'start_time': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }

            await self.firebase.update_document(
                self.collection,
                session_id,
                update_data
            )

            return await self.get_session(session_id, user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start workout session: {str(e)}"
            )

    async def complete_exercise(
        self,
        session_id: str,
        exercise_id: str,
        set_data: ExerciseSet,
        user_id: str
    ) -> dict:
        try:
            session = await self.get_session(session_id, user_id)
            
            if session['status'] != SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only add sets to in-progress sessions"
                )

            # Encontrar o exercício na sessão
            exercise = next(
                (ex for ex in session['exercises'] if ex['exercise_id'] == exercise_id),
                None
            )

            if not exercise:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exercise not found in session"
                )

            # Adicionar o novo set
            exercise['sets'].append(set_data.dict())

            # Atualizar estatísticas
            await self._update_session_stats(session_id, user_id)

            return await self.get_session(session_id, user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete exercise: {str(e)}"
            )

    async def complete_session(self, session_id: str, user_id: str) -> dict:
        try:
            session = await self.get_session(session_id, user_id)
            
            if session['status'] != SessionStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only complete in-progress sessions"
                )

            end_time = datetime.now(timezone.utc)
            duration = (end_time - session['start_time']).total_seconds()

            update_data = {
                'status': SessionStatus.COMPLETED,
                'end_time': end_time,
                'duration': duration,
                'updated_at': datetime.now(timezone.utc)
            }

            await self.firebase.update_document(
                self.collection,
                session_id,
                update_data
            )

            # Atualizar progresso do usuário
            await self._update_user_progress(session)

            return await self.get_session(session_id, user_id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to complete session: {str(e)}"
            )

    async def _update_session_stats(self, session_id: str, user_id: str):
        """Atualizar estatísticas da sessão"""
        session = await self.get_session(session_id, user_id)
        
        total_performance = 0
        completed_exercises = 0

        for exercise in session['exercises']:
            if exercise['sets']:
                total_performance += sum(s['performance_score'] for s in exercise['sets'])
                if len(exercise['sets']) >= exercise.get('target_sets', 1):
                    completed_exercises += 1
                    exercise['completed'] = True

        update_data = {
            'completed_exercises': completed_exercises,
            'average_performance': total_performance / len(session['exercises']) if session['exercises'] else 0,
            'updated_at': datetime.now(timezone.utc)
        }

        await self.firebase.update_document(
            self.collection,
            session_id,
            update_data
        )

    async def _update_user_progress(self, session: dict):
        """Atualizar progresso geral do usuário"""
        try:
            progress_ref = self.firebase.db.collection('user_progress').document(session['user_id'])
            
            # Atualizar estatísticas gerais
            progress_update = {
                'total_workouts': self.firebase.increment(1),
                'total_duration': self.firebase.increment(session['duration']),
                'total_calories': self.firebase.increment(session['calories_burned']),
                'last_workout_date': session['end_time'],
                'updated_at': datetime.now(timezone.utc)
            }

            # Atualizar progresso por exercício
            for exercise in session['exercises']:
                exercise_key = f"exercises.{exercise['exercise_id']}"
                total_sets = len(exercise['sets'])
                average_performance = sum(s['performance_score'] for s in exercise['sets']) / total_sets if total_sets > 0 else 0
                
                progress_update[f"{exercise_key}.total_sets"] = self.firebase.increment(total_sets)
                progress_update[f"{exercise_key}.last_performance"] = average_performance
                progress_update[f"{exercise_key}.history"] = self.firebase.array_union([{
                    'date': session['end_time'],
                    'performance': average_performance,
                    'sets': total_sets
                }])

            await progress_ref.set(progress_update, merge=True)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user progress: {str(e)}"
            )

    async def get_user_progress(self, user_id: str) -> dict:
        """Obter progresso geral do usuário"""
        try:
            progress = await self.firebase.get_document('user_progress', user_id)
            if not progress:
                return {
                    'total_workouts': 0,
                    'total_duration': 0,
                    'total_calories': 0,
                    'exercises': {}
                }
            return progress

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user progress: {str(e)}"
            )