import sqlite3

# Conectar a SQLite
conn = sqlite3.connect("detecciones.db")
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS detecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    class_name TEXT,
    confidence FLOAT,
    x1 FLOAT, y1 FLOAT, x2 FLOAT, y2 FLOAT,
    geolocation TEXT,
    image_path TEXT,
    synced INTEGER DEFAULT 0 -- 0 = No sincronizado, 1 = Sincronizado
)
""")

conn.commit()
conn.close()
print("✅ Base de datos SQLite creada.")