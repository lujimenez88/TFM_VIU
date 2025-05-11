from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.crud import detecciones
from ultralytics import YOLO
import shutil
import os
import uuid
from app.services.aws import subir_a_s3, generar_url_s3_firmada
from app.database import get_connection
from PIL import Image
from app.services.inferir_yolo_en_parches import inferir_imagen_yolo_por_parches
from app.models import BoundingBox, DeteccionDetalle

router = APIRouter()

# Carga del modelo solo una vez al inicio del módulo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "mi_modelo.pt")
#MODEL_PATH = "models/mi_modelo.pt"
model = YOLO(MODEL_PATH)

@router.post("/manual", response_model=DeteccionDetalle)
async def inferencia_manual(
    file: UploadFile = File(...),
    lat: float = Form(None),
    lon: float = Form(None),
    altura_m: float = Form(0.12),
    fov: float = Form(62.2),
    objetivo_cm: float = Form(15.0),
    job_id: int=Form(1)
):
    try:
        nombre_archivo = f"manual_{uuid.uuid4()}.jpg"
        path_local = os.path.join(BASE_DIR,"..","tmp", nombre_archivo)
        # Guardar temporalmente la imagen subida
        with open(path_local, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Abrir imagen con PIL
        img = Image.open(path_local).convert("RGB")
        resolucion_h_px = img.width  # Ajuste: usar ancho real de la imagen

        # Ejecutar inferencia con parcheo
        detecciones_parcheadas, imagen_escalada = inferir_imagen_yolo_por_parches(
            image=img,
            modelo=model,
            altura_m=altura_m,
            fov=fov,
            resolucion_h_px=resolucion_h_px,
            objetivo_cm=objetivo_cm
        )

        # Guardar imagen escalada localmente
        anotada_path = path_local.replace(".jpg", "_out.jpg")
        imagen_escalada.save(anotada_path)

        # Subir imágenes a S3
        #s3_path_original = f"manuales/{nombre_archivo}"
        s3_path_escalada = f"detecciones/{nombre_archivo}"
        #No se guarda la original
        #subir_a_s3(path_local, s3_path_original)
        os.remove(path_local)
        subir_a_s3(anotada_path, s3_path_escalada)

        # Insertar en BBDD
        geolocalizacion = [lat, lon] if lat is not None and lon is not None else None
        image_path = nombre_archivo
        
        id_deteccion = detecciones.insertar_deteccion_manual(
            geolocation=geolocalizacion,
            image_path=image_path,
            origen="manual",
            job_id=job_id
        )
        mejores_por_clase = {}
        detalles=[]
        for det in detecciones_parcheadas:
            x1, y1, x2, y2, class_name, class_confidence = det
            if class_name not in mejores_por_clase or class_confidence > mejores_por_clase[class_name][1]:
                mejores_por_clase[class_name] = ([x1, y1, x2, y2], class_confidence)
        print(5)
        for i, (class_name, (bbox, class_confidence)) in enumerate(mejores_por_clase.items()):
            if i >= 5:
                break
            x1, y1, x2, y2 = bbox
            #Se guardan las detecciones
            detecciones.insertar_detalle_deteccion(
                id_deteccion=id_deteccion,
                class_name=class_name,
                confidence=class_confidence,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2
            )
            print(i)
            detalles.append(BoundingBox(
                class_name=class_name,
                confidence=round(class_confidence, 4),
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2
            ))

        url_imagen = generar_url_s3_firmada(s3_path_escalada)
        #print(url_imagen, detalles)
        return DeteccionDetalle(
            image_url=url_imagen,
            detalles=detalles
        )
        # return {
        #     "mensaje": "✅ Inferencia realizada con éxito",
        #     "id_deteccion": id_deteccion,
        #     "imagen_anotada": url_imagen,
        #     "total_detecciones": len(detecciones_parcheadas)
        # }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
