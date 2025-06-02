# dron/publisher.py

import paho.mqtt.client as mqtt
import base64
import json
import os
import time
import random
from dotenv import load_dotenv

# -------------------------
# CARGA DE VARIABLES .env
# -------------------------
load_dotenv()
#25
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.0.25")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC_IMAGENES", "dron/imagenes")
MQTT_TOPIC_CONTROL = os.getenv("MQTT_TOPIC_CONTROL", "dron/frecuencia")
CARPETA_BASE = os.getcwd()#os.getenv("CARPETA_IMAGENES", os.getcwd())
SUBCARPETAS = os.getenv("SUBCARPETAS", "PruebaLive").split(",")
IMAGENES_ENVIO = int(os.getenv("IMAGENES_ENVIO", 5))

LAT_MIN = float(os.getenv("LAT_MIN", -10.12200))
LAT_MAX = float(os.getenv("LAT_MAX", -10.10400))
LON_MIN = float(os.getenv("LON_MIN", -75.98800))
LON_MAX = float(os.getenv("LON_MAX", -75.98600))

REGIONES = [
    {
        "pais": "Colombia",
        "ciudad": "Manizales",
        "LAT_MIN": 5.03700,
        "LAT_MAX": 5.06000,
        "LON_MIN": -75.52800,
        "LON_MAX": -75.50000
    },
    {
        "pais": "Colombia",
        "ciudad": "Pitalito",
        "LAT_MIN": 1.85200,
        "LAT_MAX": 1.87500,
        "LON_MIN": -76.06000,
        "LON_MAX": -76.03000
    },
    {
        "pais": "Perú",
        "ciudad": "Villa Rica",
        "LAT_MIN": -10.12200,
        "LAT_MAX": -10.10400,
        "LON_MIN": -75.98800,
        "LON_MAX": -75.98600
    },
    {
        "pais": "Perú",
        "ciudad": "Jaén",
        "LAT_MIN": -5.72000,
        "LAT_MAX": -5.70000,
        "LON_MIN": -78.81000,
        "LON_MAX": -78.78000
    },
    {
        "pais": "Brasil",
        "ciudad": "Patrocínio",
        "LAT_MIN": -18.97000,
        "LAT_MAX": -18.95000,
        "LON_MIN": -46.99000,
        "LON_MAX": -46.96000
    },
    {
        "pais": "Brasil",
        "ciudad": "Guaxupé",
        "LAT_MIN": -21.32000,
        "LAT_MAX": -21.30000,
        "LON_MIN": -46.75000,
        "LON_MAX": -46.73000
    }
]


# --------------------------------
# Funciones auxiliares
# --------------------------------
def generar_coordenadas(region):
    lat = round(random.uniform(region["LAT_MIN"], region["LAT_MAX"]),6)
    lon = round(random.uniform(region["LON_MIN"], region["LON_MAX"]),6)
    # lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
    # lon = round(random.uniform(LON_MIN, LON_MAX), 6)
    return [lat, lon]

def cargar_imagenes():
    imagenes = []
    for subcarpeta in SUBCARPETAS:
        carpeta_completa = os.path.join(CARPETA_BASE, subcarpeta)
        if os.path.exists(carpeta_completa):
            for archivo in os.listdir(carpeta_completa):
                if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
                    imagenes.append(os.path.join(carpeta_completa, archivo))
    return imagenes

# -------------------------
# Callback para la frecuencia
# -------------------------
frecuencia = int(os.getenv("FRECUENCIA_INICIAL", 5))

def on_message(client, userdata, msg):
    global frecuencia
    try:
        frecuencia = int(msg.payload.decode())
        print(f"🔁 Frecuencia actualizada por el servidor: {frecuencia}s")
    except:
        print("⚠️ Error al interpretar la nueva frecuencia recibida")

# -------------------------
# Publicador principal
# -------------------------

def publicar_imagenes():
    random.seed(51)  # Fija la semilla si se proporciona
    imagenes = cargar_imagenes()
    if not imagenes:
        print("⚠️ No se encontraron imágenes para enviar")
        return

    seleccionadas = random.sample(imagenes, min(IMAGENES_ENVIO, len(imagenes)))

    for ruta_completa in seleccionadas:
        with open(ruta_completa, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()

        coordenadas = generar_coordenadas(REGIONES[0])
        nombre_archivo = os.path.basename(ruta_completa)
        subcarpeta_origen = os.path.basename(os.path.dirname(ruta_completa))

        data = json.dumps({
            "imagen": encoded_string,
            "coordenadas": coordenadas,
            "nombre_archivo": nombre_archivo,
            "origen": subcarpeta_origen
        })

        client.publish(MQTT_TOPIC, data)
        print(f"📤 Enviada imagen: {nombre_archivo} con coordenadas {coordenadas}, frecuencia: {frecuencia} s")
        time.sleep(frecuencia)

# -------------------------
# Inicialización MQTT
# -------------------------

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC_CONTROL)
client.on_message = on_message

client.loop_start()

try:
    publicar_imagenes()
finally:
    client.loop_stop()
    client.disconnect()
    print("✅ Finalizó la transmisión de imágenes")
