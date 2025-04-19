# --- app/api/detecciones.py ---
from fastapi import APIRouter
from typing import List
from app.models import DeteccionIn, DeteccionOut
from app.crud import detecciones

router = APIRouter()

@router.get("/", response_model=List[DeteccionOut])
def get_detecciones():
    rows = detecciones.obtener_detecciones()
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

@router.post("/", status_code=201)
def post_deteccion(d: DeteccionIn):
    detecciones.insertar_deteccion(d)
    return {"mensaje": "Detección registrada"}

