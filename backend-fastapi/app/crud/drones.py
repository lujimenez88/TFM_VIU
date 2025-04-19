# --- app/crud/drones.py ---
from app.database import get_connection
from app.models import DroneConfigIn

def obtener_configuracion(drone_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT drone_id, frecuencia_captura, modo, activo FROM drones WHERE drone_id = %s", (drone_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def crear_o_actualizar_config(config: DroneConfigIn):
    conn = get_connection()
    cur = conn.cursor()
    sql = '''
        INSERT INTO drones (drone_id, frecuencia_captura, modo, activo)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (drone_id) DO UPDATE
        SET frecuencia_captura = EXCLUDED.frecuencia_captura,
            modo = EXCLUDED.modo,
            activo = EXCLUDED.activo
    '''
    cur.execute(sql, (config.drone_id, config.frecuencia_captura, config.modo, config.activo))
    conn.commit()
    cur.close()
    conn.close()

