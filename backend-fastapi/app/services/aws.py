import os
import boto3
from dotenv import load_dotenv
import logging

load_dotenv(".env")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET")

# Inicializar cliente S3
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
def subir_a_s3(path_local, path_s3):
    """
    Sube un archivo local a una ruta específica en S3.
    """
    try:
        logging.info(f"Subiendo {path_local} a S3...")
        s3_client.upload_file(path_local, S3_BUCKET, path_s3)
        os.remove(path_local)
        logging.info(f"✅ {path_local} subido y eliminado localmente")
    except Exception as e:
        logging.error(f"❌ Error subiendo {path_local}: {e}")

def generar_url_s3_firmada(object_key: str, expires_in: int = 3600) -> str:
    """
    Genera una URL firmada para acceder a un objeto de S3.
    - object_key: ruta del archivo en el bucket (ej: detecciones/imagen123.jpg)
    - expires_in: duración del link en segundos (default: 1 hora)
    """
    try:
        print(object_key)
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': S3_BUCKET, 'Key': object_key},
            ExpiresIn=expires_in
        )
        print(url)
        return url
    except Exception as e:
        print(f"❌ Error generando URL firmada para {object_key}: {e}")
        return ""
