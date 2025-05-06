# backend-fastapi/app/main.py
from fastapi import FastAPI
from app.api import detecciones, drones
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: permitir frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Reemplaza con tu dominio real en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(detecciones.router, prefix="/detecciones", tags=["Detecciones"])
app.include_router(drones.router, prefix="/drones", tags=["Drones"])
