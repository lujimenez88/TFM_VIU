# core/almacenamiento.py

import os
import sqlite3
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

load_dotenv(".env")

DB_PATH = os.getenv("DB_PATH", "detecciones.db")
IMAGES_PATH = os.getenv("IMAGES_PATH", "imagenes")

# Crear carpeta de imágenes si no existe
os.makedirs(IMAGES_PATH, exist_ok=True)

def guardar_imagen_local(image, nombre_archivo):
    """Guarda la imagen preprocesada en disco con timestamp único."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #nombre_final = f"{timestamp}_{nombre_archivo}"
    nombre_final = f"{nombre_archivo}"
    ruta_completa = os.path.join(IMAGES_PATH, nombre_final)
    image.save(ruta_completa)
    return nombre_final  # Solo se guarda el nombre, no la ruta absoluta

def insertar_deteccion(class_name, confidence, bbox, geolocation, image_path):
    """Inserta una detección en SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS detecciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        class_name TEXT,
        confidence FLOAT,
        x1 FLOAT,
        y1 FLOAT,
        x2 FLOAT,
        y2 FLOAT,
        geolocation TEXT,
        image_path TEXT,
        synced INTEGER DEFAULT 0
    )
    """

    cursor.execute(sql)

    insert_sql = """
    INSERT INTO detecciones (class_name, confidence, x1, y1, x2, y2, geolocation, image_path, synced)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """
    cursor.execute(insert_sql, (
        class_name, float(confidence), float(bbox[0]), float(bbox[1]),
        float(bbox[2]), float(bbox[3]), str(geolocation), image_path
    ))

    conn.commit()
    conn.close()

    print(f"    ✅ Detección almacenada en SQLite: {class_name} ({confidence:.2f})")
