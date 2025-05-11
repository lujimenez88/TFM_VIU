# core/caracterizacion.py

import math

def calcular_resolucion_espacial(resolucion_px, altura_m, fov_grados):
    """
    Calcula la resolución espacial aproximada (px/m) usando la fórmula:

    resolución_px_por_m = resolución_px / (2 * altura_m * tan(FOV/2))

    Args:
        resolucion_px (int): Número de píxeles horizontales.
        altura_m (float): Altura de vuelo del dron en metros.
        fov_grados (float): Campo de visión horizontal de la cámara en grados.

    Returns:
        float: resolución en píxeles por metro (px/m).
    """
    try:
        fov_radianes = math.radians(fov_grados)
        return resolucion_px / (2 * altura_m * math.tan(fov_radianes / 2))
    except ZeroDivisionError:
        return 0.0


def calcular_gsd(sensor_mm, altura_m, resolucion_px, focal_mm):
    """
    Calcula el Ground Sampling Distance (GSD), que es el tamaño del píxel en cm en el suelo.

    GSD = (altura * tamaño sensor) / (focal * resolución)

    Args:
        sensor_mm (float): Tamaño del sensor (en mm).
        altura_m (float): Altura de vuelo (en metros).
        resolucion_px (int): Número de píxeles (ancho o alto).
        focal_mm (float): Distancia focal de la cámara (en mm).

    Returns:
        float: Tamaño del píxel en centímetros.
    """
    try:
        gsd_metros = (altura_m * sensor_mm) / (focal_mm * resolucion_px)
        return gsd_metros * 100  # Convertir a cm
    except ZeroDivisionError:
        return 0.0
