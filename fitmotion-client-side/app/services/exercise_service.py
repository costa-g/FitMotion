from fastapi import HTTPException, status
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate
from app.services.firebase_service import FirebaseService
from typing import List, Optional

class ExerciseService:
    def __init__(self):
        self.firebase = FirebaseService()
        self.collection = 'exercises'

    async def create_exercise(self, exercise: ExerciseCreate) -> dict:
        try:
            exercise_dict = exercise.model_dump()
            doc_ref = self.firebase.db.collection(self.collection).document()
            exercise_dict['id'] = doc_ref.id
            await self.firebase.set_document(self.collection, doc_ref.id, exercise_dict)
            return exercise_dict
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create exercise: {str(e)}"
            )

    async def get_exercise(self, exercise_id: str) -> dict:
        exercise = await self.firebase.get_document(self.collection, exercise_id)
        if not exercise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found"
            )
        return exercise

    async def update_exercise(self, exercise_id: str, exercise: ExerciseUpdate) -> dict:
        try:
            current_exercise = await self.get_exercise(exercise_id)
            update_data = exercise.model_dump(exclude_unset=True)
            await self.firebase.update_document(self.collection, exercise_id, update_data)
            return await self.get_exercise(exercise_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update exercise: {str(e)}"
            )

    async def delete_exercise(self, exercise_id: str):
        try:
            await self.firebase.delete_document(self.collection, exercise_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete exercise: {str(e)}"
            )

    async def list_exercises(
        self,
        muscle_group: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[dict]:
        try:
            filters = []
            if muscle_group:
                filters.append(('muscleGroups', 'array_contains', muscle_group))
            if difficulty:
                filters.append(('difficulty', '==', difficulty))

            exercises = await self.firebase.query_collection(
                self.collection,
                filters=filters,
                order_by=('name', 'ASCENDING'),
                limit=limit
            )
            return exercises
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list exercises: {str(e)}"
            )