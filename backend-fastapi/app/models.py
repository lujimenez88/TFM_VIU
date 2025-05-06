# --- app/models.py ---
from pydantic import BaseModel
from typing import Optional

class DeteccionIn(BaseModel):
    dron_id: int
    timestamp: str
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    geolocation: str
    image_path: str

class DeteccionOut(BaseModel):
    id: int
    job_name: str
    timestamp: str
    lat: Optional[float]
    lon: Optional[float]
    image_path: str

class DronIn(BaseModel):
    mac: str
    frecuencia_captura: int
    altura_vuelo_metros: float
    fov_horizontal: float
    resolucion_horizontal: int
    modo: str = "adaptativo"
    objeto_cm: Optional[float] = 15.0

class DronOut(DronIn):
    id: int

# Para la lista general de detecciones

class DeteccionResumen(BaseModel):
    id: int
    timestamp: str
    lat: Optional[float]
    lon: Optional[float]
    image_path: str
    es_sano: bool

# Para el detalle de detección individual
class BoundingBox(BaseModel):
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

class DeteccionDetalle(BaseModel):
    image_url: str
    detalles: list[BoundingBox]