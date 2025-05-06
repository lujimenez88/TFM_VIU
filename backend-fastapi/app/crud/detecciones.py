# --- app/crud/detecciones.py ---
from app.database import get_connection
from app.models import DeteccionIn
from datetime import datetime

def insertar_deteccion(data: DeteccionIn):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 🔹 1. Buscar o crear job
        cur.execute('SELECT id FROM jobs WHERE dron_id = %s AND estado = %s', (data.dron_id, 'activo'))
        job = cur.fetchone()
        print(data.dron_id)
        if job:
            job_id = job[0]
        else:
            cur.execute('''
                INSERT INTO jobs (nombre, descripcion, dron_id, estado)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (
                f"Trabajo automático {data.dron_id}",
                "Generado automáticamente por el Agente Raspberry",
                data.dron_id,
                'activo'
            ))
            job_id = cur.fetchone()[0]
            conn.commit()

        # 🔹 2. Buscar o crear deteccion (geolocation + image_path)
        cur.execute('''
            SELECT id FROM detecciones
            WHERE geolocation = %s AND image_path = %s
        ''', (data.geolocation, data.image_path))
        deteccion = cur.fetchone()

        if deteccion:
            id_deteccion = deteccion[0]
        else:
            cur.execute('''
                INSERT INTO detecciones (timestamp, geolocation, image_path, job_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (
                data.timestamp,
                data.geolocation,
                data.image_path,
                job_id
            ))
            id_deteccion = cur.fetchone()[0]
            conn.commit()

        # 🔹 3. Insertar en detalle_detecciones
        cur.execute('''
            INSERT INTO detalle_detecciones (id_deteccion, class_name, confidence, x1, y1, x2, y2)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            id_deteccion,
            data.class_name,
            data.confidence,
            data.x1,
            data.y1,
            data.x2,
            data.y2
        ))
        conn.commit()

    except Exception as e:
        print("❌ ERROR en insertar_deteccion:", e)
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def obtener_detecciones():
    try:
        conn = get_connection()
        cur = conn.cursor()
        print("📡 Conectado a la base de datos.")
        cur.execute('''
            SELECT d.id, j.nombre AS job_nombre, d.timestamp, d.geolocation, d.image_path
            FROM detecciones d
            JOIN jobs j ON d.job_id = j.id
            ORDER BY d.timestamp DESC
        ''')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("❌ ERROR en obtener_detecciones:", e)
        raise

def obtener_detecciones_por_job(job_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = '''
            SELECT 
                d.id,
                d.timestamp,
                d.geolocation,
                d.image_path,
                CASE 
                    WHEN COUNT(CASE WHEN dd.class_name != 'healthy' THEN 1 END) > 0 THEN false
                    ELSE true
                END AS es_sano
            FROM 
                detecciones d
            LEFT JOIN 
                detalle_detecciones dd ON d.id = dd.id_deteccion
            WHERE 
                d.job_id = %s
            GROUP BY 
                d.id, d.timestamp, d.geolocation, d.image_path
            ORDER BY d.timestamp DESC
        '''
        cur.execute(sql, (job_id,))
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "geolocation": row[2],
                "image_path": row[3],
                "es_sano": row[4]
            }
            for row in rows
        ]
    except Exception as e:
        print("❌ ERROR en obtener_detecciones_por_job:", e)
        raise
    finally:
        cur.close()
        conn.close()

def obtener_detalle_por_deteccion(id_deteccion: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql_img = '''
            SELECT image_path
            FROM detecciones
            WHERE id = %s
        '''
        cur.execute(sql_img, (id_deteccion,))
        result = cur.fetchone()
        if not result:
            return None  # detección no existe

        image_path = result[0]

        sql_detalle = '''
            SELECT class_name, confidence, x1, y1, x2, y2
            FROM detalle_detecciones
            WHERE id_deteccion = %s
        '''
        cur.execute(sql_detalle, (id_deteccion,))
        detalles = cur.fetchall()

        return {
            "image_path": image_path,
            "detalles": [
                {
                    "class_name": r[0],
                    "confidence": r[1],
                    "x1": r[2],
                    "y1": r[3],
                    "x2": r[4],
                    "y2": r[5]
                } for r in detalles
            ]
        }
    except Exception as e:
        print("❌ ERROR en obtener_detalle_por_deteccion:", e)
        raise
    finally:
        cur.close()
        conn.close()
