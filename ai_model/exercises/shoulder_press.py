from utils import calculate_angle, check_symmetry, check_stability, calculate_angular_velocity, is_within_amplitude, calculate_distance
import mediapipe as mp
import time

def analyze_shoulder_press(landmarks, frame_width, frame_height, prev_angles=None, prev_time=None):
    """
    Analisa a postura do exercício de Desenvolvimento de Ombro aplicando vários critérios.
    """
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
    head = landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE]

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

    # Distância relativa entre ombro e cotovelo para verificar extensão
    shoulder_elbow_distance = calculate_distance(left_shoulder, left_elbow, frame_width, frame_height)

    # Análise de amplitude de movimento
    full_range_reached = is_within_amplitude(elbow_angle, 160, 180)

    # Progressão do exercício (início, meio e fim)
    if elbow_angle < 90:
        phase = "Início"
    elif 90 <= elbow_angle < 160:
        phase = "Meio"
    else:
        phase = "Fim"

    # Feedback com base nos critérios
    if not stable:
        feedback = "Mantenha o tronco reto. Evite inclinar-se para frente ou para trás."
    elif not symmetrical:
        feedback = "Verifique o alinhamento dos ombros. Mantenha ambos os ombros alinhados."
    elif elbow_angle < 90:
        feedback = "Desça os pesos até a altura dos ombros para começar o movimento."
    elif 90 <= elbow_angle < 160:
        if shoulder_angle < 70:
            feedback = "Mantenha os cotovelos próximos ao tronco ao levantar os pesos."
        elif angular_velocity > 10:
            feedback = "Movimento muito rápido. Execute o exercício com mais controle."
        else:
            feedback = "Continue levantando os pesos de forma controlada e alinhada."
    elif elbow_angle >= 160 and full_range_reached:
        feedback = "Braços totalmente estendidos acima da cabeça. Excelente!"
    else:
        feedback = "Verifique a posição e refaça o movimento para um desenvolvimento de ombro eficaz."

    # Retorna feedback e informações de análise detalhada como um dicionário
    return {
        "feedback": feedback,
        "phase": phase,
        "elbow_angle": elbow_angle,
        "shoulder_angle": shoulder_angle,
        "torso_angle": torso_angle,
        "symmetry": symmetrical,
        "stability": stable,
        "angular_velocity": angular_velocity,
        "shoulder_elbow_distance": shoulder_elbow_distance,
        "time": current_time
    }
