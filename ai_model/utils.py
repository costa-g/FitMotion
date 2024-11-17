import math
import time

def normalize_coordinates(point, frame_width, frame_height):
    """
    Normaliza as coordenadas de um ponto com base na largura e altura do frame.
    """
    return point.x * frame_width, point.y * frame_height

def calculate_angle(point1, point2, point3, frame_width=None, frame_height=None):
    """
    Calcula o ângulo entre três pontos (ex: ombro, cotovelo, pulso).
    Normaliza as coordenadas se frame_width e frame_height forem fornecidos.
    """
    if frame_width and frame_height:
        x1, y1 = normalize_coordinates(point1, frame_width, frame_height)
        x2, y2 = normalize_coordinates(point2, frame_width, frame_height)
        x3, y3 = normalize_coordinates(point3, frame_width, frame_height)
    else:
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y
        x3, y3 = point3.x, point3.y

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    return abs(angle)

def calculate_distance(point1, point2, frame_width=None, frame_height=None):
    """
    Calcula a distância entre dois pontos. Se frame_width e frame_height forem fornecidos, 
    normaliza as coordenadas antes de calcular a distância.
    """
    if frame_width and frame_height:
        x1, y1 = normalize_coordinates(point1, frame_width, frame_height)
        x2, y2 = normalize_coordinates(point2, frame_width, frame_height)
    else:
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def check_symmetry(left_point, right_point, frame_width=None, frame_height=None, tolerance=0.05):
    """
    Verifica se dois pontos (esquerdo e direito) estão simétricos em relação ao eixo vertical.
    A tolerância define o limite de diferença aceitável entre as posições x dos pontos.
    """
    if frame_width and frame_height:
        left_x, _ = normalize_coordinates(left_point, frame_width, frame_height)
        right_x, _ = normalize_coordinates(right_point, frame_width, frame_height)
    else:
        left_x, right_x = left_point.x, right_point.x

    return abs(left_x - right_x) <= tolerance * frame_width

def check_stability(torso_angle, lower_bound=85, upper_bound=95):
    """
    Verifica se o ângulo do tronco está dentro dos limites aceitáveis (posição reta).
    """
    return lower_bound <= torso_angle <= upper_bound

def calculate_angular_velocity(angle1, angle2, time_elapsed):
    """
    Calcula a velocidade angular entre dois ângulos em um intervalo de tempo.
    """
    if time_elapsed > 0:
        return abs(angle2 - angle1) / time_elapsed
    return 0

def is_within_amplitude(angle, min_angle, max_angle):
    """
    Verifica se o ângulo está dentro da amplitude de movimento esperada.
    """
    return min_angle <= angle <= max_angle

def calculate_center_of_mass(landmarks, relevant_points, frame_width=None, frame_height=None):
    """
    Calcula o centro de massa aproximado com base nos pontos relevantes.
    """
    x_sum, y_sum = 0, 0
    for point in relevant_points:
        x, y = (landmarks[point].x, landmarks[point].y)
        if frame_width and frame_height:
            x, y = normalize_coordinates(landmarks[point], frame_width, frame_height)
        x_sum += x
        y_sum += y
    count = len(relevant_points)
    return x_sum / count, y_sum / count

def check_head_alignment(head, torso, tolerance=0.1):
    """
    Verifica o alinhamento da cabeça em relação ao torso.
    """
    head_x, head_y = head.x, head.y
    torso_x, torso_y = torso.x, torso.y
    return abs(head_x - torso_x) <= tolerance and abs(head_y - torso_y) <= tolerance

def calculate_inclination(torso, hips, frame_width=None, frame_height=None):
    """
    Calcula a inclinação do torso em relação à linha dos quadris.
    """
    if frame_width and frame_height:
        torso_x, torso_y = normalize_coordinates(torso, frame_width, frame_height)
        hips_x, hips_y = normalize_coordinates(hips, frame_width, frame_height)
    else:
        torso_x, torso_y = torso.x, torso.y
        hips_x, hips_y = hips.x, hips.y

    # Inclinação em relação ao eixo vertical
    angle = math.degrees(math.atan2(torso_y - hips_y, torso_x - hips_x))
    return abs(angle)

def analyze_posture(landmarks, frame_width, frame_height, prev_angles=None, prev_time=None):
    """
    Realiza uma análise detalhada da postura, incluindo ângulos, simetria, estabilidade, 
    velocidade angular, alinhamento da cabeça e inclinação do torso.
    """
    if prev_angles is None:
        prev_angles = {}

    # Cálculos de ângulos e distâncias
    shoulder_angle = calculate_angle(landmarks['left_hip'], landmarks['left_shoulder'], landmarks['left_elbow'], frame_width, frame_height)
    elbow_angle = calculate_angle(landmarks['left_shoulder'], landmarks['left_elbow'], landmarks['left_wrist'], frame_width, frame_height)
    torso_angle = calculate_angle(landmarks['left_hip'], landmarks['left_shoulder'], landmarks['right_hip'], frame_width, frame_height)
    head_torso_alignment = calculate_distance(landmarks['left_shoulder'], landmarks['right_shoulder'], frame_width, frame_height)
    
    # Verificação de simetria, estabilidade e alinhamento da cabeça
    symmetrical = check_symmetry(landmarks['left_shoulder'], landmarks['right_shoulder'], frame_width, frame_height)
    stable = check_stability(torso_angle)
    head_aligned = check_head_alignment(landmarks['head'], landmarks['torso'])

    # Cálculo de velocidade angular
    current_time = time.time()
    time_elapsed = current_time - prev_time if prev_time else 0
    angular_velocity = calculate_angular_velocity(prev_angles.get('elbow_angle', elbow_angle), elbow_angle, time_elapsed)

    # Cálculo de inclinação do torso
    torso_inclination = calculate_inclination(landmarks['torso'], landmarks['hips'], frame_width, frame_height)

    # Cálculo de centro de massa
    relevant_points = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']
    center_of_mass = calculate_center_of_mass(landmarks, relevant_points, frame_width, frame_height)

    # Resultados de análise
    return {
        "shoulder_angle": shoulder_angle,
        "elbow_angle": elbow_angle,
        "torso_angle": torso_angle,
        "symmetry": symmetrical,
        "stability": stable,
        "angular_velocity": angular_velocity,
        "head_torso_alignment": head_torso_alignment,
        "center_of_mass": center_of_mass,
        "torso_inclination": torso_inclination,
        "head_aligned": head_aligned,
        "time": current_time
    }
