# --- app/api/drones.py ---
from fastapi import APIRouter, HTTPException
from app.models import DronIn, DronOut
from app.crud import drones
from typing import List

router = APIRouter()

@router.get("/{mac}", response_model=DronOut)
def get_dron(mac: str):
    dron = drones.obtener_dron_por_mac(mac)
    if not dron:
        raise HTTPException(status_code=404, detail="Dron no encontrado")
    return DronOut(**dron)

@router.post("/", response_model=DronOut, status_code=201)
def create_dron(dron: DronIn):
    if drones.obtener_dron_por_mac(dron.mac):
        return update_dron(dron.mac, dron)
    drones.crear_dron(dron)
    return DronOut(**drones.obtener_dron_por_mac(dron.mac))

@router.put("/{mac}", response_model=DronOut)
def update_dron(mac: str, dron: DronIn):
    if not drones.obtener_dron_por_mac(mac):
        raise HTTPException(status_code=404, detail="Dron no encontrado")
    drones.actualizar_dron(mac, dron)
    return DronOut(**drones.obtener_dron_por_mac(mac))
    
@router.get("/", response_model=List[DronOut])
def listar_drones():
    rows = drones.obtener_todos_los_drones()
    return [DronOut(
        id=row[0],
        mac=row[1],
        frecuencia_captura=row[2],
        altura_vuelo_metros=row[3],
        fov_horizontal=row[4],
        resolucion_horizontal=row[5],
        modo=row[6],
        objeto_cm=row[7]
    ) for row in rows]
