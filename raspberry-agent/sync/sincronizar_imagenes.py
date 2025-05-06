# core/sincronizar_imagenes.py

import os
import boto3
from dotenv import load_dotenv
import logging

load_dotenv(".env")

# Configuración de AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")
IMAGES_PATH = os.getenv("IMAGES_PATH", "imagenes")

# Inicializar cliente de S3
s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

logging.basicConfig(level=logging.INFO)

def sincronizar_imagenes():
    if not os.path.exists(IMAGES_PATH):
        logging.info("No existe carpeta de imágenes.")
        return

    archivos = [f for f in os.listdir(IMAGES_PATH) if f.endswith(('.jpg', '.jpeg', '.png'))]

    if not archivos:
        logging.info("No hay imágenes para sincronizar.")
        return

    for nombre_archivo in archivos:
        ruta_local = os.path.join(IMAGES_PATH, nombre_archivo)
        try:
            logging.info(f"Subiendo {nombre_archivo} a S3...")
            s3.upload_file(ruta_local, S3_BUCKET, f"detecciones/{nombre_archivo}")
            os.remove(ruta_local)
            logging.info(f"✅ {nombre_archivo} subido y eliminado localmente")
        except Exception as e:
            logging.error(f"❌ Error subiendo {nombre_archivo}: {e}")

if __name__ == "__main__":
    sincronizar_imagenes()
