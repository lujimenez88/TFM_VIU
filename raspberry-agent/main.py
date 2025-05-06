# mqtt/main.py

import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from core.configuracion import cargar_configuracion
from core.caracterizacion import calcular_resolucion_espacial
from mqtt.handlers import on_message
from mqtt.client import iniciar_cliente_mqtt

# ----------------------------
# 1. CARGAR VARIABLES DE ENTORNO (.env)
# ----------------------------
load_dotenv(".env")
BROKER = os.getenv("BROKER", "localhost")
TOPIC_IMAGENES = os.getenv("TOPIC_IMAGENES", "dron/imagenes")

# ----------------------------
# 2. CARGAR CONFIGURACIÓN LOCAL
# ----------------------------
config = cargar_configuracion()
altura_vuelo = config["altura_vuelo_metros"]
fov_horizontal = config["fov_horizontal"]
resolucion_horizontal = config["resolucion_horizontal"]

# ----------------------------
# 3. CALCULAR RESOLUCIÓN ESPACIAL
# ----------------------------
resolucion_px_por_m = calcular_resolucion_espacial(resolucion_horizontal, altura_vuelo, fov_horizontal)
print(f"📐 Resolución espacial aproximada: {resolucion_px_por_m:.2f} px/m")

# ----------------------------
# 4. CONECTAR AL BROKER MQTT Y SUSCRIBIRSE
# ----------------------------
client = iniciar_cliente_mqtt()
client.loop_forever()
