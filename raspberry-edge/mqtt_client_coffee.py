import paho.mqtt.client as mqtt
import base64
import tflite_runtime.interpreter as tflite
import numpy as np
import io
from PIL import Image, ImageOps
import json
import numpy
import sqlite3
 
# Parámetros
CONFIDENCE_THRESHOLD = 0.5  # Umbral de confianza
IOU_THRESHOLD = 0.4  # Umbral para Non-Max Suppression (NMS)
CLASS_NAMES = ['cerscospora', 'healthy', 'miner', 'phoma', 'rust','Falta-de-boro', 'Falta-de-boro', 'Falta-de-calcio', 'Falta-de-fosforo', 'Falta-de-hierro','Falta-de-magnesio','Falta-de-manganeso','Falta-de-potasio','Falta-nitrogeno']  # Ejemplo de clases (ajusta según tu modelo)

# Cargar el modelo
interpreter = tflite.Interpreter(model_path="mi_modelo.tflite")
interpreter.allocate_tensors()

# Obtener detalles del tensor de entrada
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Tamaño de entrada del modelo (1024x1024)
input_size = input_details[0]['shape'][2]
#print(input_details[0]['shape'][1])
#print(input_details[0]['shape'][2])
#print(input_details[0]['shape'][0])
labels_path="/home/raspi/Documents/Python/Coffee/labels.txt"

def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]
        
def preprocess_image(image):
    image = image.resize((input_size, input_size))  # Redimensionar
    #image = image.resize((640, 640))
    img_array = np.array(image) / 255.0
    # Reordenar las dimensiones a (3, 640, 640) en lugar de (640, 640, 3)
    img_array = np.transpose(img_array, (2, 0, 1))  # Mover canales de color a la segunda dimensión
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
    return img_array
    
# Aplicar Non-Max Suppression (NMS) para eliminar cajas redundantes
def non_max_suppression(boxes, iou_threshold):
    if len(boxes) == 0:
        return []

    # Ordenar cajas por confianza
    boxes = sorted(boxes, key=lambda x: x[4], reverse=True)
    selected_boxes = []

    while boxes:
        chosen_box = boxes.pop(0)
        selected_boxes.append(chosen_box)

        boxes = [box for box in boxes if iou(chosen_box, box) < iou_threshold]

    return selected_boxes

# Función para calcular el IoU (Intersection over Union)
def iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0    
def insertar_deteccion(class_name, confidence, bbox, geolocation, image_path):
    conn = sqlite3.connect("detecciones.db")
    cursor = conn.cursor()

    sql = """
    INSERT INTO detecciones (class_name, confidence, x1, y1, x2, y2, geolocation, image_path, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """
    
    cursor.execute(sql, (class_name, float(confidence), float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]), 
                         str(geolocation), image_path))
    conn.commit()
    conn.close()

    print(f"    ✅ Detección almacenada en SQLite: {class_name} ({confidence:.2f})")
    
def on_message(client, userdata, msg):
    """
    Función que se ejecuta cuando se recibe un mensaje MQTT con una imagen en base64.
    """
    data = json.loads(msg.payload.decode())
    image_data = base64.b64decode(data['imagen'])
    geolocalizacion = data['coordenadas']  # Coordenadas del dron
    nombre_archivo = data['nombre_archivo']
    image = Image.open(io.BytesIO(image_data))

    width, height = image.size  # Dimensiones originales
    detections = []  # Lista para almacenar las detecciones

    # 🔹 **Dividir la imagen en parches de 1024x1024**
    for y in range(0, height, input_size):
        for x in range(0, width, input_size):
            # Extraer el parche de la imagen grande
            patch = image.crop((x, y, x + input_size, y + input_size))

            # Si el parche es más pequeño (bordes), agregar padding
            if patch.size[0] < input_size or patch.size[1] < input_size:
                patch = ImageOps.expand(patch, (0, 0, input_size - patch.size[0], input_size - patch.size[1]), fill=(0, 0, 0))

            # Preprocesar el parche
            processed_patch = preprocess_image(patch)

            # Ejecutar el modelo en el parche
            interpreter.set_tensor(input_details[0]['index'], processed_patch)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])

            # Procesar las predicciones
            predictions = np.transpose(np.squeeze(output_data))  # Shape: [8400, 17]

            for pred in predictions:
                x1, y1, x2, y2 = pred[0:4]

                # Extraer las probabilidades de clase
                class_probs = pred[4:]
                class_id = np.argmax(class_probs)
                class_confidence = class_probs[class_id]

                # Filtrar por umbral de confianza
                if class_confidence > CONFIDENCE_THRESHOLD:
                    class_name = CLASS_NAMES[class_id]

                    # Ajustar coordenadas al espacio de la imagen original
                    x1 += x
                    x2 += x
                    y1 += y
                    y2 += y

                    detections.append([x1, y1, x2, y2, class_name, class_confidence])
    print("Detección Imagen: ", nombre_archivo)
    # 🔹 **Registrar las detecciones en la base de datos**
    # 🔹 Crear diccionario para guardar la mejor detección por clase
    mejores_por_clase = {}

    # Recorrer todas las detecciones
    for det in detections:
        x1, y1, x2, y2, class_name, class_confidence = det

        # Si no está la clase o tiene mayor confianza que la registrada, actualizar
        if class_name not in mejores_por_clase or class_confidence > mejores_por_clase[class_name][1]:
            mejores_por_clase[class_name] = ([x1, y1, x2, y2], class_confidence)

    # 🔹 Registrar máximo 5 clases distintas
    for i, (class_name, (bbox, class_confidence)) in enumerate(mejores_por_clase.items()):
        if i >= 5:
            break
        x1, y1, x2, y2 = bbox

        print(f"    🔍 Objeto detectado: {class_name}, Confianza: {class_confidence:.2f}")
        print(f"    📦 Caja delimitadora: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
        print(f"    📍 Ubicación geográfica del dron: {geolocalizacion}\n")

        insertar_deteccion(class_name, class_confidence, [x1, y1, x2, y2], geolocalizacion, nombre_archivo)
        print(" ✅ Registrado en BD")




# Configuración del cliente MQTT
client = mqtt.Client()
client.connect("192.168.0.11", 1883)  # IP del broker MQTT
client.subscribe("dron/imágenes")

client.on_message = on_message
client.loop_forever()
