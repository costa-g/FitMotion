from fastapi import HTTPException, status
from app.schemas.workout import WorkoutCreate, WorkoutUpdate
from app.services.firebase_service import FirebaseService
from app.services.exercise_service import ExerciseService
from typing import List, Optional
from datetime import datetime

class WorkoutService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = 'workouts'
        self.exercise_service = ExerciseService()

    async def create_workout(self, workout: WorkoutCreate, user_id: str) -> dict:
        try:
            for exercise in workout.exercises:
                await self.exercise_service.get_exercise(exercise.exerciseId)

            workout_dict = workout.model_dump()
            workout_dict.update({
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'userId': user_id,
                'status': 'active'
            })
            
            doc_ref = self.firebase.db.collection(self.collection).document()
            workout_dict['id'] = doc_ref.id
            await self.firebase.set_document(self.collection, doc_ref.id, workout_dict)
            return workout_dict

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create workout: {str(e)}"
            )

    async def get_workout(self, workout_id: str, user_id: str) -> dict:
        workout = await self.firebase.get_document(self.collection, workout_id)
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workout not found"
            )
        
        if workout.get('userId') != user_id and not workout.get('isPublic', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return workout

    async def update_workout(self, workout_id: str, workout: WorkoutUpdate, user_id: str) -> dict:
        try:
            current_workout = await self.get_workout(workout_id, user_id)
            
            if current_workout['userId'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own workouts"
                )

            if workout.exercises:
                for exercise in workout.exercises:
                    await self.exercise_service.get_exercise(exercise.exerciseId)

            update_data = workout.model_dump(exclude_unset=True)
            update_data['updatedAt'] = datetime.utcnow()
            
            await self.firebase.update_document(self.collection, workout_id, update_data)
            return await self.get_workout(workout_id, user_id)

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update workout: {str(e)}"
            )

    async def delete_workout(self, workout_id: str, user_id: str):
        try:
            workout = await self.get_workout(workout_id, user_id)
            
            if workout['userId'] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own workouts"
                )

            await self.firebase.delete_document(self.collection, workout_id)
            return {"message": "Workout deleted successfully"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete workout: {str(e)}"
            )

    async def list_workouts(
        self,
        user_id: str,
        body_area: Optional[str] = None,
        difficulty: Optional[str] = None,
        featured: Optional[bool] = None,
        is_public: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        try:
            filters = []
                
            if is_public is not None:
                if is_public:
                    filters.append(('isPublic', '==', True))
                else:
                    filters.append(('userId', '==', user_id))
            else:
                filters.append(('isPublic', '==', True))

            if body_area:
                filters.append(('bodyArea', '==', body_area))
            if difficulty:
                filters.append(('difficulty', '==', difficulty))
            if featured is not None:
                filters.append(('featured', '==', featured))

            workouts = await self.firebase.query_collection(
                self.collection,
                filters=filters,
                order_by=('createdAt', 'DESCENDING'),
                limit=limit,
                offset=offset
            )

            for workout in workouts:
                exercises_details = []
                for exercise in workout.get('exercises', []):
                    try:
                        exercise_data = await self.exercise_service.get_exercise(
                            exercise['exerciseId']
                        )
                        exercises_details.append({
                            **exercise,
                            'details': exercise_data
                        })
                    except HTTPException:
                        exercises_details.append(exercise)
                        
                workout['exercises'] = exercises_details

            return workouts

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list workouts: {str(e)}"
            )

    async def get_featured_workouts(self, limit: int = 5) -> List[dict]:
        try:
            filters = [
                ('featured', '==', True),
                ('isPublic', '==', True)
            ]

            workouts = await self.firebase.query_collection(
                self.collection,
                filters=filters,
                order_by=('createdAt', 'DESCENDING'),
                limit=limit
            )

            for workout in workouts:
                exercises_details = []
                for exercise in workout['exercises']:
                    exercise_data = await self.exercise_service.get_exercise(
                        exercise['exerciseId']
                    )
                    exercises_details.append({
                        **exercise,
                        'details': exercise_data
                    })
                workout['exercises'] = exercises_details

            return workouts

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get featured workouts: {str(e)}"
            )

    async def get_workouts_by_body_area(
        self,
        body_area: str,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[dict]:
        try:
            filters = [
                ('bodyArea', '==', body_area),
                ('isPublic', '==', True)
            ]

            if difficulty:
                filters.append(('difficulty', '==', difficulty))

            workouts = await self.firebase.query_collection(
                self.collection,
                filters=filters,
                order_by=('createdAt', 'DESCENDING'),
                limit=limit
            )

            for workout in workouts:
                exercises_details = []
                for exercise in workout['exercises']:
                    exercise_data = await self.exercise_service.get_exercise(
                        exercise['exerciseId']
                    )
                    exercises_details.append({
                        **exercise,
                        'details': exercise_data
                    })
                workout['exercises'] = exercises_details

            return workouts

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get workouts by body area: {str(e)}"
            )