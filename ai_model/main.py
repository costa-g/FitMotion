import cv2
import mediapipe as mp
import time
import os
from datetime import datetime

# Exercises
from exercises.shoulder_press import analyze_shoulder_press

mp_pose = mp.solutions.pose

def initialize_pose(detection_confidence=0.7, tracking_confidence=0.7, enable_segmentation=False, model_complexity=1):
    """
    Inicializa o modelo de pose do Mediapipe com parâmetros configuráveis.
    """
    return mp_pose.Pose(
        static_image_mode=False,
        model_complexity=model_complexity,
        enable_segmentation=enable_segmentation,
        min_detection_confidence=detection_confidence,
        min_tracking_confidence=tracking_confidence
    )

def provide_initial_instructions(exercise_type):
    """
    Exibe instruções iniciais para o usuário com base no tipo de exercício.
    """
    if exercise_type == "shoulder_press":
        print("Instruções para o exercício Desenvolvimento de Ombro:")
        print("Posicione os pesos na altura dos ombros, mantenha o tronco ereto e pés firmes no chão.")
        print("Evite inclinar o corpo para frente ou para os lados durante o movimento.")
    else:
        print("Instruções para o exercício não estão disponíveis.")

def process_exercise(exercise_type, landmarks):
    """
    Seleciona e executa a função de análise de exercício com base no tipo de exercício.
    """
    analysis_function = globals().get(f"analyze_{exercise_type}")
    if analysis_function:
        result = analysis_function(landmarks)
        if isinstance(result, tuple) and len(result) == 4:
            return result  # feedback, elbow_angle, shoulder_angle, torso_angle
        else:
            # Caso a função retorne apenas o feedback, preenche os ângulos com None
            return result, None, None, None
    else:
        return "Exercise not supported.", None, None, None


def get_log_file_path(exercise_type):
    """
    Retorna o caminho do arquivo de log para o exercício e data especificados.
    """
    feedback_folder = "feedbacks"
    if not os.path.exists(feedback_folder):
        os.mkdir(feedback_folder)
    
    exercise_folder = os.path.join(feedback_folder, exercise_type)
    if not os.path.exists(exercise_folder):
        os.mkdir(exercise_folder)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file_path = os.path.join(exercise_folder, f"{date_str}.txt")
    return log_file_path

def log_feedback(feedback, exercise_type, elbow_angle=None, shoulder_angle=None, torso_angle=None):
    """
    Salva o feedback em um arquivo de log específico para o exercício e a data, incluindo detalhes de ângulos.
    """
    log_file_path = get_log_file_path(exercise_type)
    with open(log_file_path, "a") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] Feedback: {feedback}\n")
        if elbow_angle is not None and shoulder_angle is not None and torso_angle is not None:
            f.write(f"   Ângulos - Cotovelo: {elbow_angle:.2f}, Ombro: {shoulder_angle:.2f}, Tronco: {torso_angle:.2f}\n")

def capture_video(pose, exercise_type, feedback_interval=1.0):
    """
    Captura vídeo da câmera e processa a pose para o tipo de exercício especificado.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Não foi possível acessar a câmera. Verifique a conexão.")

    mp_drawing = mp.solutions.drawing_utils
    last_feedback_time = time.time()
    previous_angles = None
    start_time = time.time()  # Usado para calcular o FPS
    frame_count = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Erro ao capturar vídeo. Verifique a conexão com a câmera.")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(frame_rgb)
            if result.pose_landmarks:
                # Desenha a pose detectada
                mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Adiciona a máscara de segmentação se estiver disponível
                if result.segmentation_mask is not None:
                    mask_3d = cv2.cvtColor((result.segmentation_mask * 255).astype("uint8"), cv2.COLOR_GRAY2BGR)
                    frame = cv2.addWeighted(frame, 1, mask_3d, 0.7, 0)

                # Controle de feedback com base em mudanças nos ângulos
                current_time = time.time()
                if current_time - last_feedback_time >= feedback_interval:
                    feedback, elbow_angle, shoulder_angle, torso_angle = process_exercise(exercise_type, result.pose_landmarks)
                    
                    # Verifica se os ângulos foram retornados corretamente
                    if elbow_angle is not None and shoulder_angle is not None and torso_angle is not None:
                        # Verifica se houve uma mudança significativa nos ângulos para fornecer novo feedback
                        if previous_angles is None or \
                           abs(elbow_angle - previous_angles[0]) > 5 or \
                           abs(shoulder_angle - previous_angles[1]) > 5 or \
                           abs(torso_angle - previous_angles[2]) > 5:
                            
                            print(feedback)
                            log_feedback(feedback, exercise_type, elbow_angle, shoulder_angle, torso_angle)
                            previous_angles = (elbow_angle, shoulder_angle, torso_angle)
                            last_feedback_time = current_time
                    
                    # Adiciona o feedback diretamente no frame do vídeo
                    cv2.putText(frame, feedback, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

            # Calcula e exibe a taxa de quadros (FPS)
            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            cv2.imshow('FitMotion - Pose Detection with Segmentation', frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


def run_exercise_analysis(exercise_type="shoulder_press", detection_confidence=0.7, tracking_confidence=0.7, feedback_interval=1.0, enable_segmentation=True, model_complexity=1):
    """
    Função de orquestração que inicializa o modelo, configura os parâmetros e inicia a captura de vídeo.
    """
    # Fornece instruções iniciais para o exercício
    provide_initial_instructions(exercise_type)

    # Inicializa o modelo de pose com os parâmetros fornecidos
    pose = initialize_pose(
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
        enable_segmentation=enable_segmentation,
        model_complexity=model_complexity
    )

    # Inicia a captura de vídeo e o processamento de feedback para o exercício especificado
    capture_video(pose=pose, exercise_type=exercise_type, feedback_interval=feedback_interval)

if __name__ == "__main__":
    run_exercise_analysis(
        exercise_type="shoulder_press",
        detection_confidence=0.7,
        tracking_confidence=0.7,
        feedback_interval=1.0,
        enable_segmentation=False,
        model_complexity=1
    )
