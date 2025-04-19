# --- app/crud/detecciones.py ---
from app.database import get_connection
from app.models import DeteccionIn

def insertar_deteccion(data: DeteccionIn):
    conn = get_connection()
    cur = conn.cursor()
    sql = '''
        INSERT INTO detecciones (timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(sql, (
        data.timestamp, data.class_name, data.confidence, data.x1, data.y1,
        data.x2, data.y2, data.geolocation, data.image_path
    ))
    conn.commit()
    cur.close()
    conn.close()

def obtener_detecciones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path FROM detecciones ORDER BY timestamp DESC LIMIT 50")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows