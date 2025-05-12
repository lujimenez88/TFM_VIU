from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models import JobIn, JobOut, JobUpdate
from app.crud.jobs import crear_job, listar_jobs, actualizar_job

router = APIRouter()

@router.get("/", response_model=List[JobOut])
def get_jobs(estado: str = Query(None), dron_id: int = Query(None)):
    return listar_jobs(estado, dron_id)

@router.post("/", response_model=JobOut, status_code=201)
def post_job(job: JobIn):
    nuevo = crear_job(job)
    if not nuevo:
        raise HTTPException(status_code=400, detail="No se pudo crear el job")
    return nuevo

@router.patch("/{job_id}", response_model=JobOut)
def patch_job(job_id: int, job_data: JobUpdate):
    actualizado = actualizar_job(job_id, job_data)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Job no encontrado o sin cambios")
    return actualizado