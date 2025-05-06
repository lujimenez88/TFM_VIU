import sqlite3
import requests
import os
import json
from core.configuracion import cargar_configuracion, guardar_config_local, obtener_mac

API_URL_BASE = os.getenv("API_URL_BASE", "http://localhost:8000")
API_URL_DETECCIONES = f"{API_URL_BASE}/detecciones/"
API_URL_DRONES = f"{API_URL_BASE}/drones/"

DB_PATH = os.getenv("DB_PATH", "detecciones.db")


def sincronizar_detecciones(dron_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM detecciones WHERE synced = 0")
    filas = cur.fetchall()

    for fila in filas:
        id_, time_stamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path, synced = fila

        payload = {
            "dron_id": dron_id,
            "timestamp": time_stamp,  # Si tienes timestamp original, inclúyelo
            "class_name": class_name,
            "confidence": confidence,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "geolocation": geolocation,
            "image_path": image_path
        }

        try:
            resp = requests.post(API_URL_DETECCIONES, json=payload, timeout=5)
            if resp.status_code == 201:
                cur.execute("UPDATE detecciones SET synced = 1 WHERE id = ?", (id_,))
                conn.commit()
                print(f"✅ Detección {id_} sincronizada correctamente")
            else:
                print(f"❌ Error al sincronizar ID {id_}: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"⚠️ Excepción sincronizando ID {id_}: {e}")

    cur.close()
    conn.close()


def sincronizar_dron():
    #config = cargar_configuracion()
    config={}
    mac = obtener_mac()
    dron_id=0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM drones WHERE mac = ? AND synced = 0", (mac,))
    row = cur.fetchone()

    if not row:
        print("✅ Dron ya sincronizado o no hay cambios locales")
        return

    mac, frecuencia, altura, fov, resolucion, modo, objeto_cm, dron_id_backend, synced = row
    payload = {
        "mac": mac,
        "frecuencia_captura": frecuencia,
        "altura_vuelo_metros": altura,
        "fov_horizontal": fov,
        "resolucion_horizontal": resolucion,
        "modo": modo,
        "objeto_cm": objeto_cm
    }

    try:
        resp = requests.get(f"{API_URL_DRONES}{mac}", timeout=5)
        if resp.status_code == 404:
            # Crear nuevo dron
            post = requests.post(API_URL_DRONES, json=payload, timeout=5)
            if post.status_code in [200, 201]:
                cur.execute("UPDATE drones SET synced = 1 WHERE mac = ?", (mac,))
                conn.commit()
                config_data = post.json()
                # Actualizar config.json con valores del backend
                config.update({
                    "dron_id": config_data.get("id"),
                    "frecuencia_captura": config_data.get("frecuencia_captura", frecuencia),
                    "altura_vuelo_metros": config_data.get("altura_vuelo_metros", altura),
                    "fov_horizontal": config_data.get("fov_horizontal", fov),
                    "resolucion_horizontal": config_data.get("resolucion_horizontal", resolucion),
                    "objeto_cm": config_data.get("objeto_cm", objeto_cm)
                })
                guardar_config_local(config)
                print("🆕 Dron creado y sincronizado")
                dron_id=config_data.get("id")
        elif resp.status_code == 200:
            # Actualizar dron existente
            put = requests.put(f"{API_URL_DRONES}{mac}", json=payload, timeout=5)
            if put.status_code in [200, 204]:
                cur.execute("UPDATE drones SET synced = 1 WHERE mac = ?", (mac,))
                conn.commit()
                config_data = resp.json()
                config.update({
                    "dron_id": config_data.get("id"),
                    "frecuencia_captura": config_data.get("frecuencia_captura", frecuencia),
                    "altura_vuelo_metros": config_data.get("altura_vuelo_metros", altura),
                    "fov_horizontal": config_data.get("fov_horizontal", fov),
                    "resolucion_horizontal": config_data.get("resolucion_horizontal", resolucion),
                    "objeto_cm": config_data.get("objeto_cm", objeto_cm)
                })
                guardar_config_local(config)
                print("🔄 Dron actualizado y sincronizado")
                dron_id=config_data.get("id")
    except Exception as e:
        print(f"⚠️ Error al sincronizar dron: {e}")

    cur.close()
    conn.close()
    return dron_id


def sincronizar_todo():
    dron_id=sincronizar_dron()
    sincronizar_detecciones(dron_id)

if __name__ == "__main__":
    if conexion_activa():
        print("🌐 Conexión a internet activa. Iniciando sincronización...")
        sincronizar_todo()
    else:
        print("⚠️ No hay conexión a internet. Reintentar luego.")