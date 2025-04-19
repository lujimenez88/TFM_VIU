# --- app/api/drones.py ---
from fastapi import APIRouter, HTTPException
from app.models import DroneConfigIn
from app.crud import drones

router = APIRouter()

@router.get("/{drone_id}")
def get_config(drone_id: str):
    result = drones.obtener_configuracion(drone_id)
    if result:
        return {
            "drone_id": result[0],
            "frecuencia_captura": result[1],
            "modo": result[2],
            "activo": result[3]
        }
    else:
        raise HTTPException(status_code=404, detail="Drone no encontrado")

@router.post("/")
def post_config(config: DroneConfigIn):
    drones.crear_o_actualizar_config(config)
    return {"mensaje": "Configuración guardada"}

