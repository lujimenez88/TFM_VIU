from fastapi import FastAPI
from routes import drones

app = FastAPI()

# Incluir routers externos
app.include_router(drones.router)

@app.get("/")
def read_root():
    return {"message": "Backend FastAPI funcionando!"}