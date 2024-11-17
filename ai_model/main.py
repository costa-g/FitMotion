import cv2
import mediapipe as mp
import time
import os
from datetime import datetime

# Exercises
from exercises.shoulder_press import analyze_shoulder_press, INITIAL_POSITION

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

def process_exercise(exercise_type, landmarks, frame_width, frame_height, prev_angles, prev_time, phase):
    """
    Executa a função de análise do exercício e retorna o feedback e dados de análise.
    """
    if exercise_type == "shoulder_press":
        return analyze_shoulder_press(landmarks, frame_width, frame_height, prev_angles, prev_time, phase)
    else:
        # Retorna um dicionário padrão caso o exercício não seja suportado
        return {
            "feedback": "Exercise not supported.",
            "phase": phase,
            "elbow_angle": 0,
            "shoulder_angle": 0,
            "torso_angle": 0,
            "symmetry": False,
            "stability": False,
            "angular_velocity": 0,
            "time": prev_time,
            "total_repetitions": 0
        }

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

def log_feedback(result, exercise_type):
    """
    Salva o feedback em um arquivo de log específico para o exercício e a data, incluindo detalhes de ângulos.
    """
    log_file_path = get_log_file_path(exercise_type)
    with open(log_file_path, "a") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] Feedback: {result['feedback']}\n")
        f.write(f"   Fase: {result['phase']}\n")
        f.write(f"   Ângulos - Cotovelo: {result['elbow_angle']:.2f}, Ombro: {result['shoulder_angle']:.2f}, Tronco: {result['torso_angle']:.2f}\n")
        f.write(f"   Simetria: {result['symmetry']}, Estabilidade: {result['stability']}\n")
        f.write(f"   Velocidade Angular: {result['angular_velocity']:.2f}\n")
        f.write(f"   Total de Repetições: {result['total_repetitions']}\n")

def capture_video(pose, exercise_type, feedback_interval=1.0):
    """
    Captura vídeo da câmera e processa a pose para o tipo de exercício especificado.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Não foi possível acessar a câmera. Verifique a conexão.")

    # Define resolução para reduzir o "zoom" e obter uma melhor visão do exercício
    desired_width = 1280
    desired_height = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

    # Inicializa variáveis de fase e controle de feedback
    mp_drawing = mp.solutions.drawing_utils
    last_feedback_time = time.time()
    previous_angles = None
    current_phase = INITIAL_POSITION
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
                mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                current_time = time.time()
                if current_time - last_feedback_time >= feedback_interval:
                    landmarks = result.pose_landmarks
                    frame_width, frame_height = frame.shape[1], frame.shape[0]

                    # Processa o exercício e obtém dados de análise, incluindo fase atual
                    result = process_exercise(
                        exercise_type,
                        landmarks,
                        frame_width,
                        frame_height,
                        prev_angles=previous_angles if previous_angles else {},
                        prev_time=last_feedback_time,
                        phase=current_phase
                    )

                    # Atualiza a fase e o feedback com base no resultado
                    current_phase = result["phase"]
                    print(result["feedback"])

                    # Atualiza ângulos e tempo para controle
                    previous_angles = {
                        "elbow_angle": result['elbow_angle'],
                        "shoulder_angle": result['shoulder_angle'],
                        "torso_angle": result['torso_angle']
                    }
                    last_feedback_time = current_time
                    
                    # Exibe o feedback no vídeo
                    cv2.putText(frame, result["feedback"], (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    
                    # Exibe a contagem de repetições e fase atual no vídeo
                    cv2.putText(frame, f"Repetições: {result['total_repetitions']}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"Fase: {result['phase']}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)

                    log_feedback(result, exercise_type)

            # Calcula e exibe a taxa de quadros (FPS)
            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

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
