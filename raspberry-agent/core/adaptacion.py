import os
import json
import requests
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from core.configuracion import actualizar_config_local

load_dotenv()

# Leer variables del entorno
BROKER = os.getenv("BROKER", "localhost")
TOPIC_CONTROL = os.getenv("TOPIC_CONTROL", "dron/frecuencia")
API_URL_BASE = os.getenv("API_URL_BASE", "http://localhost:8000/drones/")
API_URL_DRONES = f"{API_URL_BASE}/drones/"

# Inicializar cliente MQTT para enviar nueva frecuencia
client = mqtt.Client()
client.connect(BROKER)

# Historial de detecciones
detecciones_recientes = []

# Límites de frecuencia
FRECUENCIA_MIN = int(os.getenv("FRECUENCIA_MIN", 3))
FRECUENCIA_MAX = int(os.getenv("FRECUENCIA_MAX", 30))


def evaluar_frecuencia(frecuencia_actual, mac=None):
    """
    Ajusta la frecuencia según si se detectaron enfermedades recientemente.
    """
    ultimos = detecciones_recientes[-5:] if len(detecciones_recientes) >= 5 else detecciones_recientes
    print(ultimos)
    
    # ✅ Solo consideramos enfermedad si class_name es distinto de 'healthy'
    hay_enfermedad = any(d["class_name"].lower() != "healthy" for d in ultimos)
    #print(hay_enfermedad)
    if hay_enfermedad:
        nueva_frecuencia = max(FRECUENCIA_MIN, frecuencia_actual // 2)
    else:
        nueva_frecuencia = min(FRECUENCIA_MAX, frecuencia_actual + 5)
    #print(nueva_frecuencia, frecuencia_actual)
    if nueva_frecuencia != frecuencia_actual:
        # 🛰️ Publicar nueva frecuencia al dron
        client.publish(TOPIC_CONTROL, str(nueva_frecuencia), retain=True)
        print(f"🧠 Nueva frecuencia enviada al dron: {nueva_frecuencia}s")

        # 💾 Actualizar localmente
        config=actualizar_config_local(frecuencia=nueva_frecuencia)

        # 🌐 Intentar actualizar también en el backend si se conoce el ID
        if mac:
            try:
                resp = requests.put(f"{API_URL_DRONES}{mac}", json=config, timeout=5)
                if resp.status_code in [200, 204]:
                    print("☁️ Frecuencia actualizada en backend")
            except:
                print("⚠️ No se pudo actualizar la frecuencia en el backend")

    return nueva_frecuencia
