# --- app/api/detecciones.py ---
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models import DeteccionIn, DeteccionOut, DeteccionResumen, DeteccionDetalle, BoundingBox
from app.crud import detecciones
from app.services.aws import generar_url_s3_firmada
import json

router = APIRouter()

# 🔹 GET general (para pruebas, consulta libre)
@router.get("/", response_model=List[DeteccionOut])
def get_detecciones():
    rows = detecciones.obtener_detecciones()
    detecciones_list = []
    for row in rows:
        try:
            lat, lon = json.loads(row[3])  # row[9] = geolocation
        except:
            lat, lon = None, None
        detecciones_list.append(DeteccionOut(
            id=row[0],
            job_name=row[1],
            timestamp=str(row[2]),
            lat=lat,
            lon=lon,
            image_path=row[4]
        ))
    return detecciones_list

@router.post("/", status_code=201)
def post_deteccion(d: DeteccionIn):
    detecciones.insertar_deteccion(d)
    return {"mensaje": "Detección registrada"}

# 🔹 GET detecciones por job con es_sano + coordenadas
@router.get("/job/{job_id}", response_model=List[DeteccionResumen])
def get_detecciones_por_job(job_id: int):
    rows = detecciones.obtener_detecciones_por_job(job_id)
    resultado = []
    for row in rows:
        try:
            lat, lon = json.loads(row["geolocation"])
        except:
            lat, lon = None, None
        resultado.append(DeteccionResumen(
            id=row["id"],
            timestamp=str(row["timestamp"]),
            lat=lat,
            lon=lon,
            image_path=row["image_path"],
            es_sano=row["es_sano"]
        ))
    return resultado

# 🔹 GET detecciones filtrables por job, dron, origen
@router.get("/filtro", response_model=List[DeteccionResumen])
def get_detecciones_filtradas(
    job_id: int = Query(None),
    dron_id: int = Query(None),
    origen: str = Query(None)
):
    rows = detecciones.obtener_detecciones_filtradas(job_id=job_id, dron_id=dron_id, origen=origen)
    resultado = []
    for row in rows:
        try:
            lat, lon = json.loads(row["geolocation"])
        except:
            lat, lon = None, None
        resultado.append(DeteccionResumen(
            id=row["id"],
            timestamp=str(row["timestamp"]),
            lat=lat,
            lon=lon,
            image_path=row["image_path"],
            es_sano=row["es_sano"]
        ))
    return resultado

# 🔹 GET detalle de detección
@router.get("/job/detalle/{id_deteccion}", response_model=DeteccionDetalle)
def get_detalle_deteccion(id_deteccion: int):
    detalle = detecciones.obtener_detalle_por_deteccion(id_deteccion)
    if detalle is None:
        raise HTTPException(status_code=404, detail="Detección no encontrada")

    # Convertir a modelos y generar URL S3
    object_key='detecciones/'+detalle["image_path"]
    url_s3 = generar_url_s3_firmada(object_key)  # Lo veremos abajo
    return DeteccionDetalle(
        image_url=url_s3,
        detalles=[BoundingBox(**d) for d in detalle["detalles"]]
    )
    
    # return DeteccionDetalle(
    #     image_url=detalle["image_path"],
    #     detalles=[BoundingBox(**d) for d in detalle["detalles"]]
    # )