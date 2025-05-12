from fastapi import APIRouter, Query
from app.crud.drones import obtener_jobs, obtener_drones, obtener_origenes_por_job

router = APIRouter()

@router.get("/drones/")
def get_drones():
    try:
        return obtener_drones()
    except Exception as e:
        return {"error": str(e)}

@router.get("/jobs/")
def get_jobs(dron_id: int = Query(None)):
    try:
        return obtener_jobs(dron_id)
    except Exception as e:
        return {"error": str(e)}

@router.get("/origenes/")
def get_origenes(job_id: int = Query(...)):
    try:
        return obtener_origenes_por_job(job_id)
    except Exception as e:
        return {"error": str(e)}
