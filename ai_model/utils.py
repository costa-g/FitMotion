import math

def calculate_angle(point1, point2, point3):
    """
    Calcula o ângulo entre três pontos (ex: ombro, cotovelo, pulso).
    """
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y
    x3, y3 = point3.x, point3.y

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    return abs(angle)
