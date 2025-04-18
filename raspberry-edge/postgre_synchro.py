import sqlite3
import psycopg2
import requests

# Conexión a PostgreSQL en la nube
conn_cloud = psycopg2.connect(
    dbname="CoffeeDB",
    user="postgres",
    password="Viu123456*",
    host="192.168.0.15",
    port="5432"
)

def sincronizar_detecciones():
    """ Sincroniza las detecciones almacenadas en SQLite con PostgreSQL en la nube. """
    
    # Conectar a SQLite
    conn_local = sqlite3.connect("detecciones.db")
    cursor_local = conn_local.cursor()

    # Obtener detecciones no sincronizadas
    cursor_local.execute("SELECT * FROM detecciones WHERE synced = 0")
    detecciones = cursor_local.fetchall()

    if not detecciones:
        print("✅ No hay detecciones pendientes de sincronización.")
        return

    # Conectar a PostgreSQL
    cursor_cloud = conn_cloud.cursor()

    for det in detecciones:
        id_det, timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, img_path, synced = det

        # Insertar en PostgreSQL
        sql = """
        INSERT INTO detecciones (timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor_cloud.execute(sql, (timestamp, class_name, confidence, x1, y1, x2, y2, geolocation, img_path))
        conn_cloud.commit()

        # Marcar como sincronizado en SQLite
        cursor_local.execute("UPDATE detecciones SET synced = 1 WHERE id = ?", (id_det,))
        conn_local.commit()

    print("✅ Sincronización con PostgreSQL completada.")

    # Cerrar conexiones
    cursor_cloud.close()
    conn_local.close()

# Ejecutar sincronización si hay conexión a internet
try:
    requests.get("https://www.google.com", timeout=5)  # Prueba de conexión
    sincronizar_detecciones()
except requests.ConnectionError:
    print("⚠️ No hay conexión a Internet, se sincronizará más tarde.")
