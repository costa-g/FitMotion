from utils import (
    calculate_angle, check_symmetry, check_stability, 
    calculate_angular_velocity, is_within_amplitude, calculate_distance
)
import mediapipe as mp
import time

# Estados do exercício
INITIAL_POSITION = "Posição Inicial"
ELEVATION_PHASE = "Movimento de Elevação"
DESCENT_PHASE = "Descida Controlada"
COMPLETED_REPETITION = "Repetição Completa"

# Variáveis de progresso e motivação
total_repetitions = 0
last_rep_completed = False

# Configurações de tempo e limites
MIN_REP_DURATION = 1.5  # Tempo mínimo em segundos para uma repetição ser considerada válida
previous_time = time.time()

def analyze_shoulder_press(landmarks, frame_width, frame_height, prev_angles=None, prev_time=None, phase=INITIAL_POSITION):
    """
    Analisa o exercício de Desenvolvimento de Ombro em etapas com feedback para cada fase do movimento.
    Inclui progressão, motivação, ajuste postural, indicadores visuais e histórico de repetições.
    """
    global total_repetitions, last_rep_completed, previous_time

    if prev_angles is None:
        prev_angles = {}
    if prev_time is None:
        prev_time = time.time()

    # Pontos principais para o exercício de desenvolvimento de ombro
    left_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
    left_wrist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
    right_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]

    # Ângulos articulares
    elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist, frame_width, frame_height)
    shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow, frame_width, frame_height)
    torso_angle = calculate_angle(left_hip, left_shoulder, right_hip, frame_width, frame_height)

    # Critérios de análise
    symmetrical = check_symmetry(left_shoulder, right_shoulder, frame_width, frame_height)
    stable = check_stability(torso_angle)
    current_time = time.time()
    time_elapsed = current_time - prev_time
    angular_velocity = calculate_angular_velocity(prev_angles.get("elbow_angle", elbow_angle), elbow_angle, time_elapsed)

    # Feedback e ajustes para fases
    feedback = ""
    if phase == INITIAL_POSITION:
        if elbow_angle < 100 and 85 <= shoulder_angle <= 95 and stable:
            feedback = "Posição inicial correta. Prepare-se para a elevação."
            phase = ELEVATION_PHASE
            last_rep_completed = False
        else:
            feedback = "Ajuste para a posição inicial: cotovelos a 90 graus e alinhados com os ombros."

    elif phase == ELEVATION_PHASE:
        if 160 <= elbow_angle <= 180 and angular_velocity < 10:
            feedback = "Elevação completa! Agora, desça os halteres de forma controlada."
            phase = DESCENT_PHASE
        elif angular_velocity > 15:
            feedback = "Movimento muito rápido. Controle a elevação."
        elif elbow_angle < 160:
            feedback = f"Continue a elevação de forma controlada. Faltam {180 - elbow_angle:.1f} graus."
        else:
            feedback = "Mantenha a postura e controle o ritmo."

    elif phase == DESCENT_PHASE:
        if elbow_angle < 100 and 85 <= shoulder_angle <= 95 and stable:
            if not last_rep_completed:
                rep_duration = time.time() - previous_time
                if rep_duration >= MIN_REP_DURATION:
                    total_repetitions += 1
                    last_rep_completed = True
                    previous_time = time.time()
                    feedback = f"Repetição {total_repetitions} completa. Excelente! Volte à posição inicial."
                else:
                    feedback = "Repetição rápida demais. Desça lentamente para maior controle."
            phase = INITIAL_POSITION
        elif angular_velocity > 15:
            feedback = "Movimento muito rápido. Desça os pesos lentamente."
        else:
            feedback = "Desça de forma lenta e controlada, mantendo o alinhamento dos cotovelos com os ombros."

    elif phase == COMPLETED_REPETITION:
        feedback = "Repetição completa. Volte à posição inicial para iniciar a próxima repetição."
        phase = INITIAL_POSITION

    # Verificações adicionais de alinhamento e estabilidade
    if not stable:
        feedback += " | Mantenha o tronco estável e evite inclinar para frente ou para trás."
    elif not symmetrical:
        feedback += " | Ajuste o alinhamento dos ombros para garantir simetria."

    # Indicadores visuais para motivação
    if phase == COMPLETED_REPETITION and total_repetitions > 0:
        feedback += f" | Excelente trabalho! Total de repetições: {total_repetitions}"

    # Retorna feedback e informações de análise detalhada, incluindo a fase atual e repetições
    return {
        "feedback": feedback,
        "phase": phase,
        "elbow_angle": elbow_angle,
        "shoulder_angle": shoulder_angle,
        "torso_angle": torso_angle,
        "symmetry": symmetrical,
        "stability": stable,
        "angular_velocity": angular_velocity,
        "total_repetitions": total_repetitions,
        "time": current_time
    }
