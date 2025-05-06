# ----------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------
# Se estructura el proyecto separando:
# - .env: variables de entorno (BROKER, URLs, TOPICs, CLASS_NAMES, etc.)
# - config.json: configuración dinámica del dron (frecuencia, altura, FOV, etc.)
# ----------------------------

import os
import json
import math
import uuid
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv(".env")

# Variables de entorno
BROKER = os.getenv("BROKER", "localhost")
TOPIC_IMAGENES = os.getenv("TOPIC_IMAGENES", "dron/imagenes")
TOPIC_CONTROL = os.getenv("TOPIC_CONTROL", "dron/frecuencia")
API_URL_BASE = os.getenv("API_URL_BASE", "http://localhost:8000")
API_URL_DRONES = f"{API_URL_BASE}/drones/"
DB_PATH = os.getenv("DB_PATH", "detecciones.db")
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")
CLASS_NAMES = os.getenv("CLASS_NAMES", "healthy,rust,phoma,miner").split(",")

# MAC Address como ID único
mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                for ele in range(0, 8 * 6, 8)][::-1])

def obtener_mac():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                for ele in range(0, 8 * 6, 8)][::-1])
    return mac
def registrar_dron_local(config):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS drones (
            mac TEXT PRIMARY KEY,
            frecuencia_captura INTEGER,
            altura_vuelo_metros REAL,
            fov_horizontal REAL,
            resolucion_horizontal INTEGER,
            modo TEXT,
            objeto_cm REAL,
            dron_id_backend INTEGER DEFAULT 0,
            synced INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        INSERT OR REPLACE INTO drones (
            mac, frecuencia_captura, altura_vuelo_metros,
            fov_horizontal, resolucion_horizontal, modo, objeto_cm, dron_id_backend, synced
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        mac,
        config["frecuencia_captura"],
        config["altura_vuelo_metros"],
        config["fov_horizontal"],
        config["resolucion_horizontal"],
        config.get("modo", "adaptativo"),
        config.get("objeto_cm", 15.0),
        config.get("dron_id", 0)
    ))
    conn.commit()
    conn.close()

def guardar_config_local(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    registrar_dron_local(config)

def cargar_local():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    else:
        config = {
            "mac":mac,
            "dron_id": None,
            "frecuencia_captura": 10,
            "altura_vuelo_metros": 20,
            "fov_horizontal": 84.0,
            "resolucion_horizontal": 1920,
            "modo": "adaptativo",
            "objeto_cm": 15.0
        }
        guardar_config_local(config)
    return config

def cargar_configuracion():
    config = cargar_local()
    payload = {
        "mac": mac,
        "frecuencia_captura": config["frecuencia_captura"],
        "modo": config.get("modo", "adaptativo"),
        "altura_vuelo_metros": config["altura_vuelo_metros"],
        "fov_horizontal": config["fov_horizontal"],
        "resolucion_horizontal": config["resolucion_horizontal"],
        "objeto_cm": config.get("objeto_cm", 15.0)
    }
    try:
        resp = requests.get(f"{API_URL_DRONES}{mac}", timeout=5)
        if resp.status_code == 404:
            post_resp = requests.post(API_URL_DRONES, json=payload, timeout=5)
            if post_resp.status_code in [200, 201]:
                config_backend = post_resp.json()
                config.update(config_backend)
                guardar_config_local(config)
                print("🆕 Dron registrado y configuración guardada")
        elif resp.status_code == 200:
            config_backend = resp.json()
            config.update(config_backend)
            guardar_config_local(config)
            print("✅ Configuración cargada desde backend")
    except:
        print("⚠️ Error conectando con backend. Usando configuración local")

    return config

def actualizar_config_local(frecuencia):
    config = cargar_local()
    config.update({
                    "frecuencia_captura": frecuencia
                })
    guardar_config_local(config)
    return config

