# mqtt/handlers.py

import json
import base64
import io
import os
from PIL import Image
from core.inferencia import procesar_parches_o_redimensionar
#from core.inferencia_pytorch import procesar_parches_o_redimensionar_pytorch
from core.almacenamiento import insertar_deteccion, guardar_imagen_local
from core.adaptacion import evaluar_frecuencia, detecciones_recientes
from core.configuracion import cargar_configuracion
from dotenv import load_dotenv
import time

#Se carga el archivo .env
load_dotenv(".env")

config = cargar_configuracion()
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD",0.5))
WITH_PYTORCHSCRIPT = os.getenv("WITH_PYTORCHSCRIPT",0)
IMAGES_DIR = os.getenv("IMAGES_PATH")
altura_vuelo = config["altura_vuelo_metros"]
fov_horizontal = config["fov_horizontal"]
resolucion_horizontal = config["resolucion_horizontal"]
objeto_cm = config.get("objeto_cm", 15.0)  # Longitud estimada del objeto a detectar

#IMAGES_DIR = "imagenes_guardadas"
os.makedirs(IMAGES_DIR, exist_ok=True)

def on_message(client, userdata, msg):
    print("📸 Imagen recibida para procesar")

    # Decodificar mensaje
    data = json.loads(msg.payload.decode())
    image_data = base64.b64decode(data['imagen'])
    geolocalizacion = data['coordenadas']
    nombre_archivo = data['nombre_archivo']
    altura_imagen = data.get('altura', altura_vuelo)
    image = Image.open(io.BytesIO(image_data))
    # Inferencia y tiempo TfLite
    start_tflite = time.time()
    detecciones, imagen_escalada = procesar_parches_o_redimensionar(
        image,
        CONFIDENCE_THRESHOLD,
        altura_imagen,
        fov_horizontal,
        resolucion_horizontal,
        objeto_cm,
        return_image=True
    )
    end_tflite = time.time()
    tiempo_tflite=end_tflite-start_tflite
    print("Tiempo para TFLite: ",tiempo_tflite,"\n")

    path_guardado = guardar_imagen_local(imagen_escalada, nombre_archivo)
    ##################################################
    ## Para hacer experimento de varias detecciones###
    ##################################################
    if (WITH_PYTORCHSCRIPT==1):
        mejores_por_clase = []  # Ahora es una lista

        for det in detecciones:
            x1, y1, x2, y2, class_name, class_confidence = det
            mejores_por_clase.append((class_name, [x1, y1, x2, y2], class_confidence))

        # 🔹 Ordenar opcionalmente por mayor confianza primero
        mejores_por_clase.sort(key=lambda x: x[2], reverse=True)

        # 🔹 Procesar solo las primeras 5 detecciones (o todas si quieres)
        for i, (class_name, bbox, class_confidence) in enumerate(mejores_por_clase):
            if i >= 5:
                break
            x1, y1, x2, y2 = bbox

            print(f"    🔍 Objeto detectado: {class_name}, Confianza: {class_confidence:.2f}")
            print(f"    📦 Caja delimitadora: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
            print(f"    📍 Ubicación geográfica del dron: {geolocalizacion}\n")

            insertar_deteccion(class_name, class_confidence, [x1, y1, x2, y2], geolocalizacion, path_guardado)
            detecciones_recientes.append({"class_name": class_name, "confianza": class_confidence})
    ################################################
    ##Fin experimento###############################
    ################################################
    if (WITH_PYTORCHSCRIPT==0):
        
        mejores_por_clase = {}
        for det in detecciones:
            x1, y1, x2, y2, class_name, class_confidence = det
            if class_name not in mejores_por_clase or class_confidence > mejores_por_clase[class_name][1]:
                mejores_por_clase[class_name] = ([x1, y1, x2, y2], class_confidence)

        for i, (class_name, (bbox, class_confidence)) in enumerate(mejores_por_clase.items()):
            if i >= 5:
                break
            x1, y1, x2, y2 = bbox

            print(f"    🔍 Objeto detectado: {class_name}, Confianza: {class_confidence:.2f}")
            print(f"    📦 Caja delimitadora: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
            print(f"    📍 Ubicación geográfica del dron: {geolocalizacion}\n")

            insertar_deteccion(class_name, class_confidence, [x1, y1, x2, y2], geolocalizacion, path_guardado)
            detecciones_recientes.append({"class_name": class_name,"confianza": class_confidence})
    
    # if (WITH_PYTORCHSCRIPT==1):
        ##Inferencia y tiempo PytorchScript
        # start_pytorch = time.time()
        ##Inferencia con Pytorch
        # detecciones, imagen_escalada = procesar_parches_o_redimensionar_pytorch(
            # image,
            # CONFIDENCE_THRESHOLD,
            # altura_imagen,
            # fov_horizontal,
            # resolucion_horizontal,
            # objeto_cm,
            # return_image=True
        # )
        # end_pytorch = time.time()
        # tiempo_pytorch=end_pytorch-start_pytorch
        # print("Tiempo para PytorchScript: ",tiempo_pytorch,"\n")
        # mejores_por_clase = {}
        # for det in detecciones:
            # x1, y1, x2, y2, class_name, class_confidence = det
            # if class_name not in mejores_por_clase or class_confidence > mejores_por_clase[class_name][1]:
                # mejores_por_clase[class_name] = ([x1, y1, x2, y2], class_confidence)

        # for i, (class_name, (bbox, class_confidence)) in enumerate(mejores_por_clase.items()):
            # if i >= 5:
                # break
            # x1, y1, x2, y2 = bbox

            # print(f"    🔍 Objeto detectado: {class_name}, Confianza: {class_confidence:.2f}")
            # print(f"    📦 Caja delimitadora: ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
            # print(f"    📍 Ubicación geográfica del dron: {geolocalizacion}\n")
    
    
    
    evaluar_frecuencia(config["frecuencia_captura"], config.get("mac"))
