import numpy as np
from fastapi import HTTPException, status
from app.schemas.movement_analysis import (
    AnalysisRequest,
    MovementAnalysis,
    MovementFeedback,
    ExerciseMetrics
)
from app.services.exercise_service import ExerciseService
import tensorflow as tf
import mediapipe as mp

class MovementAnalysisService:
    def __init__(self):
        self.exercise_service = ExerciseService()
        self.pose_detector = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Inicializar MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

    async def initialize_models(self):
        """Inicializa ou carrega modelos necessários"""
        try:
            # Aqui você carregaria seus modelos treinados
            # self.form_analysis_model = tf.keras.models.load_model('path_to_model')
            pass
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize models: {str(e)}"
            )

    async def analyze_movement(self, request: AnalysisRequest) -> MovementAnalysis:
        try:
            # Obter dados do exercício
            exercise = await self.exercise_service.get_exercise(request.exercise_id)
            
            # Processar frames
            processed_frames = await self._process_frames(request.frames)
            
            # Analisar forma
            form_analysis = await self._analyze_form(
                processed_frames,
                exercise['correctPositions']
            )
            
            # Contar repetições
            rep_count = await self._count_reps(processed_frames)
            
            # Gerar feedback
            feedback = await self._generate_feedback(
                processed_frames,
                form_analysis,
                exercise
            )

            return MovementAnalysis(
                exercise_id=request.exercise_id,
                accuracy=form_analysis['accuracy'],
                current_phase=form_analysis['current_phase'],
                rep_count=rep_count,
                duration=len(request.frames) / 30,  # assumindo 30 fps
                feedback=feedback,
                form_score=form_analysis['form_score'],
                recommendations=form_analysis['recommendations']
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze movement: {str(e)}"
            )

    async def _process_frames(self, frames: list[dict]) -> list[dict]:
        """Processa os frames usando MediaPipe Pose"""
        processed_frames = []
        
        for frame in frames:
            results = self.pose_detector.process(frame['image'])
            if results.pose_landmarks:
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                processed_frames.append({
                    'landmarks': landmarks,
                    'timestamp': frame['timestamp']
                })

        return processed_frames

    async def _analyze_form(self, processed_frames: list[dict], correct_positions: dict) -> dict:
        """Analisa a forma do exercício"""
        try:
            # Comparar com posições corretas
            form_scores = []
            current_phase = "preparation"
            recommendations = []

            for frame in processed_frames:
                # Calcular similaridade com posições corretas
                similarity_scores = await self._calculate_pose_similarity(
                    frame['landmarks'],
                    correct_positions
                )
                form_scores.append(max(similarity_scores))

                # Determinar fase do movimento
                current_phase = await self._determine_movement_phase(
                    frame['landmarks'],
                    correct_positions
                )

                # Gerar recomendações específicas
                frame_recommendations = await self._generate_recommendations(
                    frame['landmarks'],
                    correct_positions
                )
                recommendations.extend(frame_recommendations)

            # Calcular métricas finais
            average_accuracy = np.mean(form_scores)
            form_score = await self._calculate_form_score(form_scores)

            return {
                'accuracy': float(average_accuracy),
                'form_score': float(form_score),
                'current_phase': current_phase,
                'recommendations': list(set(recommendations))  # remove duplicatas
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze form: {str(e)}"
            )

    async def _calculate_pose_similarity(self, landmarks: list[dict], correct_positions: dict) -> list[float]:
        """Calcula a similaridade entre a pose atual e as posições corretas"""
        similarities = []
        
        for correct_position in [correct_positions['startPosition'], correct_positions['endPosition']]:
            similarity = await self._calculate_landmarks_similarity(landmarks, correct_position)
            similarities.append(similarity)
            
        return similarities

    async def _calculate_landmarks_similarity(self, landmarks1: list[dict], landmarks2: list[dict]) -> float:
        """Calcula a similaridade entre dois conjuntos de landmarks"""
        if len(landmarks1) != len(landmarks2):
            return 0.0

        total_distance = 0
        valid_points = 0

        for l1, l2 in zip(landmarks1, landmarks2):
            if l1['visibility'] > 0.5 and l2['visibility'] > 0.5:
                distance = np.sqrt(
                    (l1['x'] - l2['x'])**2 +
                    (l1['y'] - l2['y'])**2 +
                    (l1['z'] - l2['z'])**2
                )
                total_distance += distance
                valid_points += 1

        if valid_points == 0:
            return 0.0

        average_distance = total_distance / valid_points
        similarity = 1 / (1 + average_distance)
        return float(similarity)

    async def calculate_exercise_metrics(
        self,
        user_id: str,
        exercise_id: str,
        duration: float,
        form_analysis: dict
    ) -> ExerciseMetrics:
        """Calcula métricas do exercício"""
        try:
            exercise = await self.exercise_service.get_exercise(exercise_id)
            
            # Calcular calorias queimadas (exemplo simplificado)
            # Em um caso real, você usaria dados do usuário e MET do exercício
            calories_burned = duration * 5  # exemplo: 5 calorias por minuto
            
            return ExerciseMetrics(
                total_reps=form_analysis.get('rep_count', 0),
                total_duration=duration,
                average_accuracy=form_analysis['accuracy'],
                calories_burned=calories_burned,
                form_score=form_analysis['form_score']
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate metrics: {str(e)}"
            )