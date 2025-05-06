# sync/sincronizar_todo.py

import time
import requests
import os
from dotenv import load_dotenv
from sync.sincronizacion import sincronizar_dron, sincronizar_detecciones
from sync.sincronizar_imagenes import sincronizar_imagenes

# Cargar variables de entorno
load_dotenv(".env")

SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL_SECONDS", 300))  # por defecto 5 minutos

def hay_conexion():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def sincronizar_todo():
    if not hay_conexion():
        print("🔌 Sin conexión a Internet. Reintentando más tarde...")
        return

    print("\n🛠️  Iniciando proceso de sincronización...")
    sincronizar_dron()
    sincronizar_detecciones()
    sincronizar_imagenes()
    print("✅ Sincronización completa.\n")

if __name__ == "__main__":
    while True:
        sincronizar_todo()
        print(f"🕒 Esperando {SYNC_INTERVAL} segundos antes de la próxima sincronización...")
        time.sleep(SYNC_INTERVAL)
