# --- app/models.py ---
from pydantic import BaseModel
from typing import Optional

class DeteccionIn(BaseModel):
    timestamp: str
    class_name: str
    confidence: str
    x1: str
    y1: str
    x2: str
    y2: str
    geolocation: str
    image_path: str

class DeteccionOut(BaseModel):
    id: int
    timestamp: str
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    lat: float
    lon: float
    image_path: str

class DroneConfigIn(BaseModel):
    drone_id: str
    frecuencia_captura: int
    modo: str
    activo: bool

class DroneConfigOut(DroneConfigIn):
    id: int

