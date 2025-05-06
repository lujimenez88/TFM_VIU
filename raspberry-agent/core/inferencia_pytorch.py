import numpy as np
from PIL import Image, ImageOps
import torch
import os
from dotenv import load_dotenv
from core.caracterizacion import calcular_resolucion_espacial

MODEL_PATH = os.getenv("TORCH_MODEL_PATH", "modelos/mi_modelo.pt")
LABELS_PATH = os.getenv("LABELS_PATH", "modelos/labels.txt")

# Cargar modelo TorchScript
model = torch.jit.load(MODEL_PATH)
model.eval()

input_size = 640  # o leerlo desde el modelo si es dinámico

# Leer etiquetas desde archivo
with open(LABELS_PATH, "r") as f:
    class_names = [line.strip() for line in f.readlines()]

def preprocess_image_torch(image, input_size):
    image = image.resize((input_size, input_size))
    img_array = np.array(image) / 255.0
    img_tensor = torch.tensor(img_array, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
    return img_tensor

def inferir_en_imagen_torch(image, input_size, threshold, class_names):
    image_tensor = preprocess_image_torch(image, input_size)
    with torch.no_grad():
        output = model(image_tensor)
    predictions = output.squeeze().numpy()
    print("Las dimensiones son: ", predictions.shape)
    detecciones = []
    for pred in predictions:
        x1, y1, x2, y2 = pred[0:4]
        class_probs = pred[4:]
        class_id = np.argmax(class_probs)
        class_conf = class_probs[class_id]
        if class_conf > threshold:
            class_name = class_names[class_id]
            detecciones.append([x1, y1, x2, y2, class_name, class_conf])
    return detecciones

def procesar_parches_o_redimensionar_pytorch(image, threshold, altura, fov, resolucion_h, objetivo_cm=15, return_image=False):
    width, height = image.size
    detecciones = []
    resolucion_px_por_m = calcular_resolucion_espacial(resolucion_h, altura, fov)

    # Escalado global de la imagen de entrada
    pixeles_hoja = (resolucion_px_por_m * objetivo_cm) / 100
    escala = input_size / pixeles_hoja
    #Ayuda a que no haya imágenes muy pequeñas o muy grandes
    escala = min(max(escala, 0.2), 2.5)  # evita imágenes extremadamente pequeñas o grandes

    nuevo_ancho = int(width * escala)
    nuevo_alto = int(height * escala)
    imagen_escalada = image.resize((nuevo_ancho, nuevo_alto), Image.BICUBIC)

    # Recorrido por parches solapados
    stride = int(input_size * 0.8)  # 20% de solapamiento

    for y in range(0, nuevo_alto, stride):
        for x in range(0, nuevo_ancho, stride):
            patch = imagen_escalada.crop((x, y, x + input_size, y + input_size))
            if patch.size != (input_size, input_size):
                patch = ImageOps.pad(patch, (input_size, input_size), color=(0, 0, 0))

            resultados = inferir_en_imagen_torch(patch, input_size, threshold, class_names)
            for r in resultados:
                # Ajustar coordenadas del parche a la imagen escalada
                r[0] += x
                r[1] += y
                r[2] += x
                r[3] += y
                detecciones.append(r)

    return (detecciones, imagen_escalada) if return_image else detecciones