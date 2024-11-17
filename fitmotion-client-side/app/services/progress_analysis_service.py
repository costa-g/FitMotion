from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np

class ProgressAnalysisService:
    def __init__(self):
        self.firebase = FirebaseService()

    async def get_performance_trends(
        self,
        user_id: str,
        exercise_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict:
        """Analisa tendências de performance ao longo do tempo"""
        try:
            start_date = datetime.now() - timedelta(days=period_days)
            
            # Buscar sessões do período
            sessions = await self.firebase.query_collection(
                'workout_sessions',
                filters=[
                    ('user_id', '==', user_id),
                    ('created_at', '>=', start_date),
                    ('status', '==', 'completed')
                ]
            )

            performance_data = []
            dates = []

            for session in sessions:
                if exercise_id:
                    # Análise específica do exercício
                    exercise = next(
                        (e for e in session['exercises'] if e['exercise_id'] == exercise_id),
                        None
                    )
                    if exercise and exercise['sets']:
                        avg_performance = np.mean([s['performance_score'] for s in exercise['sets']])
                        performance_data.append(avg_performance)
                        dates.append(session['created_at'])
                else:
                    # Análise geral da sessão
                    performance_data.append(session['average_performance'])
                    dates.append(session['created_at'])

            if not performance_data:
                return {
                    'trend': 'neutral',
                    'improvement_rate': 0,
                    'average_performance': 0,
                    'best_performance': 0,
                    'performance_data': [],
                    'dates': []
                }

            # Calcular métricas
            improvement_rate = (performance_data[-1] - performance_data[0]) / performance_data[0] * 100
            trend = 'improving' if improvement_rate > 5 else 'declining' if improvement_rate < -5 else 'neutral'

            return {
                'trend': trend,
                'improvement_rate': improvement_rate,
                'average_performance': np.mean(performance_data),
                'best_performance': max(performance_data),
                'performance_data': performance_data,
                'dates': dates
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze performance trends: {str(e)}"
            )

    async def get_workout_statistics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict:
        """Gera estatísticas gerais dos treinos"""
        try:
            start_date = datetime.now() - timedelta(days=period_days)
            
            sessions = await self.firebase.query_collection(
                'workout_sessions',
                filters=[
                    ('user_id', '==', user_id),
                    ('created_at', '>=', start_date),
                    ('status', '==', 'completed')
                ]
            )

            total_workouts = len(sessions)
            if total_workouts == 0:
                return {
                    'total_workouts': 0,
                    'total_duration': 0,
                    'total_calories': 0,
                    'average_duration': 0,
                    'average_performance': 0,
                    'most_frequent_exercises': [],
                    'best_performing_exercises': []
                }

            # Calcular estatísticas
            total_duration = sum(s['duration'] for s in sessions)
            total_calories = sum(s['calories_burned'] for s in sessions)

            # Análise de exercícios
            exercise_frequency = {}
            exercise_performances = {}

            for session in sessions:
                for exercise in session['exercises']:
                    ex_id = exercise['exercise_id']
                    exercise_frequency[ex_id] = exercise_frequency.get(ex_id, 0) + 1
                    
                    if exercise['sets']:
                        avg_perf = np.mean([s['performance_score'] for s in exercise['sets']])
                        if ex_id not in exercise_performances:
                            exercise_performances[ex_id] = []
                        exercise_performances[ex_id].append(avg_perf)

            # Encontrar exercícios mais frequentes
            most_frequent = sorted(
                exercise_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Encontrar exercícios com melhor performance
            best_performing = sorted(
                [(k, np.mean(v)) for k, v in exercise_performances.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]

            return {
                'total_workouts': total_workouts,
                'total_duration': total_duration,
                'total_calories': total_calories,
                'average_duration': total_duration / total_workouts,
                'average_performance': np.mean([s['average_performance'] for s in sessions]),
                'most_frequent_exercises': most_frequent,
                'best_performing_exercises': best_performing
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate workout statistics: {str(e)}"
            )