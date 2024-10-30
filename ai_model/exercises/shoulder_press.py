from utils import calculate_angle
import mediapipe as mp

def analyze_shoulder_press(landmarks):
    """
    Analisa a postura do exercício de Desenvolvimento de Ombro com base nos pontos do corpo.
    """
    
    left_shoulder = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
    left_wrist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
    left_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP]
    
    # Calcula o ângulo do cotovelo (extensão do braço)
    elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    
    # Calcula o ângulo do ombro em relação ao tronco (ombro com o quadril e cotovelo)
    shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
    
    # Calcula o ângulo do tronco em relação ao chão para verificar estabilidade (evitar inclinação excessiva)
    right_hip = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
    torso_angle = calculate_angle(left_hip, left_shoulder, right_hip)

    # Define feedbacks específicos em diferentes condições do movimento
    # Fase 1: Posição Inicial (cotovelos alinhados com os ombros)
    if elbow_angle < 90:
        return "Desça os pesos até a altura dos ombros para começar o movimento."

    # Fase 2: Verificação de alinhamento e estabilidade durante o movimento
    elif 90 <= elbow_angle < 160:
        if shoulder_angle < 70:
            return "Mantenha os cotovelos mais próximos ao tronco ao levantar os pesos."
        elif torso_angle < 80 or torso_angle > 100:
            return "Evite inclinar o tronco para frente ou para trás. Mantenha a postura reta."
        else:
            return "Levante os pesos de forma controlada, mantendo os cotovelos alinhados."

    # Fase 3: Extensão Completa dos Braços
    elif elbow_angle >= 160 and shoulder_angle > 70:
        if elbow_angle > 170:
            return "Braços totalmente estendidos acima da cabeça. Ótimo!"
        else:
            return "Estenda um pouco mais os braços para completar o movimento."

    # Feedback geral se nenhuma condição específica foi atendida
    else:
        return "Verifique a posição e faça o movimento completo para um desenvolvimento de ombro eficaz."
    
    return feedback, elbow_angle, shoulder_angle, torso_angle
