from PIL import Image, ImageOps
import numpy as np
from ultralytics import YOLO
from app.core.caracterizacion import calcular_resolucion_espacial

def inferir_imagen_yolo_por_parches(image: Image.Image, modelo: YOLO, altura_m: float, fov: float,
                                    resolucion_h_px: int, objetivo_cm: float = 15.0, threshold: float = 0.5,
                                    input_size: int = 640) -> tuple[list, Image.Image]:
    """
    Realiza inferencia sobre una imagen usando parcheo y escalado compatible con detección de objetos.

    Retorna una lista de detecciones y la imagen escalada.

    Cada detección tiene formato: [x1, y1, x2, y2, class_name, class_conf]
    """
    width, height = image.size
    detecciones = []

    resolucion_px_por_m = calcular_resolucion_espacial(resolucion_h_px, altura_m, fov)
    pixeles_hoja = (resolucion_px_por_m * objetivo_cm) / 100
    escala = input_size / pixeles_hoja
    escala = min(max(escala, 0.2), 2.5)

    nuevo_ancho = int(width * escala)
    nuevo_alto = int(height * escala)
    imagen_escalada = image.resize((nuevo_ancho, nuevo_alto), Image.BICUBIC)

    stride = int(input_size * 0.8)

    for y in range(0, nuevo_alto, stride):
        for x in range(0, nuevo_ancho, stride):
            patch = imagen_escalada.crop((x, y, x + input_size, y + input_size))
            if patch.size != (input_size, input_size):
                patch = ImageOps.pad(patch, (input_size, input_size), color=(0, 0, 0))

            # Ejecutar inferencia con Ultralytics
            resultados = modelo.predict(patch, imgsz=input_size, conf=threshold)[0]

            for i in range(len(resultados.boxes)):
                box = resultados.boxes.xyxy[i].cpu().numpy()
                class_id = int(resultados.boxes.cls[i].item())
                confidence = float(resultados.boxes.conf[i].item())
                class_name = modelo.names[class_id]

                x1, y1, x2, y2 = box
                detecciones.append([x + x1, y + y1, x + x2, y + y2, class_name, confidence])

    return detecciones, imagen_escalada
