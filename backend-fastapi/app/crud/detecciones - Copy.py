# --- app/crud/detecciones.py ---
from app.database import get_connection
from app.models import DeteccionIn

def insertar_deteccion(data: DeteccionIn):
    conn = get_connection()
    cur = conn.cursor()
    sql = '''
        INSERT INTO detecciones (dron_id, timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cur.execute(sql, (
        data.dron_id, data.timestamp, data.class_name, data.confidence, data.x1, data.y1,
        data.x2, data.y2, data.geolocation, data.image_path
    ))
    conn.commit()
    cur.close()
    conn.close()

def obtener_detecciones():
    try:
        conn = get_connection()
        cur = conn.cursor()
        print("📡 Conectado a la base de datos.")
        cur.execute("SELECT id, dron_id, timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path FROM detecciones ORDER BY timestamp DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("❌ ERROR en obtener_detecciones:", e)
        raise
