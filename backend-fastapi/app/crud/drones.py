# app/crud/drones.py

from app.database import get_connection
from app.models import DronIn


def obtener_dron_por_mac(mac: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, mac, frecuencia_captura, altura_vuelo_metros,
               fov_horizontal, resolucion_horizontal, modo, objeto_cm
        FROM drones WHERE mac = %s
    """, (mac,))
    row = cur.fetchone()
    if row:
        columns = [desc[0] for desc in cur.description]
        result = dict(zip(columns, row))
    else:
        result = None
    cur.close()
    conn.close()
    return result


def crear_dron(data: DronIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO drones (mac, frecuencia_captura, altura_vuelo_metros,
                            fov_horizontal, resolucion_horizontal, modo, objeto_cm)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        data.mac, data.frecuencia_captura, data.altura_vuelo_metros,
        data.fov_horizontal, data.resolucion_horizontal, data.modo, data.objeto_cm
    ))
    dron_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return dron_id


def actualizar_dron(mac: str, data: DronIn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE drones SET
            frecuencia_captura = %s,
            altura_vuelo_metros = %s,
            fov_horizontal = %s,
            resolucion_horizontal = %s,
            modo = %s,
            objeto_cm = %s
        WHERE mac = %s
    """, (
        data.frecuencia_captura, data.altura_vuelo_metros,
        data.fov_horizontal, data.resolucion_horizontal, data.modo,
        data.objeto_cm, mac
    ))
    conn.commit()
    cur.close()
    conn.close()
    
def obtener_todos_los_drones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, mac, frecuencia_captura, altura_vuelo_metros, fov_horizontal,
               resolucion_horizontal, modo, objeto_cm
        FROM drones
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
