from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/drones")

# Modelo para drones
class DronConfig(BaseModel):
    id: str
    nombre: Optional[str] = None
    frecuencia: int
    activo: bool
    zona: Optional[str] = None
    ultima_conexion: Optional[datetime] = None

# Conexión PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "detecciones"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "admin")
)
cursor = conn.cursor()

@router.get("/parametros/{dron_id}", response_model=DronConfig)
def obtener_configuracion(dron_id: str):
    cursor.execute("SELECT id, nombre, frecuencia, activo, zona, ultima_conexion FROM drones WHERE id = %s", (dron_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Dron no registrado")
    return DronConfig(
        id=row[0], nombre=row[1], frecuencia=row[2], activo=row[3], zona=row[4], ultima_conexion=row[5]
    )

@router.post("/registrar")
def registrar_dron(dron: DronConfig):
    cursor.execute("SELECT id FROM drones WHERE id = %s", (dron.id,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="El dron ya está registrado")

    cursor.execute(
        """
        INSERT INTO drones (id, nombre, frecuencia, activo, zona, ultima_conexion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (dron.id, dron.nombre, dron.frecuencia, dron.activo, dron.zona, datetime.utcnow())
    )
    conn.commit()
    return {"mensaje": "Dron registrado correctamente"}
