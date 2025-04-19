from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()
# 🔹 Habilitar CORS para permitir peticiones desde el frontend en React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las conexiones (puedes restringirlo luego)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname="CoffeeDB",
    user="postgres",
    password="Viu123456*",
    host="localhost",
    port="5432"
)



# Modelo de respuesta para detecciones
class Deteccion(BaseModel):
    id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    lat: float
    lon: float
    timestamp: str

@app.get("/detecciones", response_model=List[Deteccion])
def obtener_detecciones():
    with conn.cursor() as cur:
        cur.execute("SELECT id, timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path FROM detecciones")
        rows = cur.fetchall()
    
    # Convertir coordenadas de string a float
    detecciones = []
    for row in rows:
        try:
            # Convertir geolocalización de string a lista [lat, lon]
            lat, lon = json.loads(row[8])  # Convierte la cadena a una lista de Python
        except:
            lat, lon = None, None  # Si hay error, asignar valores nulos

        detecciones.append(Deteccion(
            id=row[0],
            timestamp=str(row[1]),
            class_name=row[2],
            confidence=row[3],
            x1=row[4],
            y1=row[5],
            x2=row[6],
            y2=row[7],
            lat=lat,
            lon=lon,
            image_path=row[9]
        ))

    return detecciones
