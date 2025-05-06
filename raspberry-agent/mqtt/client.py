# mqtt/client.py

import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from mqtt.handlers import on_message

# Cargar variables de entorno
load_dotenv()

BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("BROKER_PORT", 1883))
TOPIC_IMAGENES = os.getenv("TOPIC_IMAGENES", "dron/imagenes")

def iniciar_cliente_mqtt():
    """
    Inicializa el cliente MQTT, se conecta al broker y se suscribe al topic.
    """
    client = mqtt.Client()
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT)
        print(f"✅ Conectado al broker MQTT en {BROKER}:{PORT}")
        client.subscribe(TOPIC_IMAGENES)
        print(f"📡 Suscrito al topic '{TOPIC_IMAGENES}'")
    except Exception as e:
        print(f"❌ Error al conectar con el broker MQTT: {e}")
        raise

    return client
