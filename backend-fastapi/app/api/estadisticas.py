from fastapi import APIRouter, Query
from app.database import get_connection
from datetime import datetime

router = APIRouter()

@router.get("/kpi")
def obtener_kpis(
    job_id: int = Query(None),
    dron_id: int = Query(None),
    origen: str = Query(None)
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        where_clauses = []
        params = []

        if job_id is not None:
            where_clauses.append("d.job_id = %s")
            params.append(job_id)
        if dron_id is not None:
            where_clauses.append("d.dron_id = %s")
            params.append(dron_id)
        if origen is not None:
            where_clauses.append("d.origen = %s")
            params.append(origen)

        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Total imágenes (detecciones)
        cur.execute(f"SELECT COUNT(*) FROM detecciones d {where_clause}", params)
        total_imagenes = cur.fetchone()[0]

        # Total detecciones (detalle_detecciones unidas a detecciones con filtro)
        cur.execute(f"""
            SELECT COUNT(*)
            FROM detalle_detecciones det
            JOIN detecciones d ON det.id_deteccion = d.id
            {where_clause}
        """, params)
        total_detecciones = cur.fetchone()[0]

        # Imágenes con al menos una enfermedad (class_name != healthy)
        cur.execute(f"""
            SELECT COUNT(DISTINCT d.id)
            FROM detecciones d
            JOIN detalle_detecciones det ON d.id = det.id_deteccion
            WHERE det.class_name != 'healthy'
            {f"AND { ' AND '.join(where_clauses) }" if where_clauses else ""}
        """, params)
        con_enfermedades = cur.fetchone()[0]

        porcentaje_enfermas = round((con_enfermedades / total_imagenes) * 100, 2) if total_imagenes > 0 else 0

        # Última detección
        cur.execute(f"SELECT MAX(d.timestamp) FROM detecciones d {where_clause}", params)
        ultima_fecha = cur.fetchone()[0]
        ultima_fecha_str = ultima_fecha.strftime("%Y-%m-%d %H:%M:%S") if isinstance(ultima_fecha, datetime) else None

        cur.close()
        conn.close()

        return {
            "total_imagenes": total_imagenes,
            "total_detecciones": total_detecciones,
            "porcentaje_enfermas": porcentaje_enfermas,
            "ultima_deteccion": ultima_fecha_str
        }

    except Exception as e:
        return {"error": str(e)}

@router.get("/clases")
def estadisticas_por_clase(
    job_id: int = Query(None),
    dron_id: int = Query(None),
    origen: str = Query(None)
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        where_clauses = []
        params = []

        if job_id is not None:
            where_clauses.append("d.job_id = %s")
            params.append(job_id)
        if dron_id is not None:
            where_clauses.append("j.dron_id = %s")
            params.append(dron_id)
        if origen is not None:
            where_clauses.append("d.origen = %s")
            params.append(origen)

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        cur.execute(f"""
            SELECT det.class_name, COUNT(*) as total
            FROM detalle_detecciones det
            JOIN detecciones d ON det.id_deteccion = d.id
            JOIN jobs j ON j.id = d.job_id
            {where_sql}
            GROUP BY det.class_name
            ORDER BY total DESC
        """, params)

        resultados = cur.fetchall()
        cur.close()
        conn.close()

        return [{"class_name": row[0], "total": row[1]} for row in resultados]

    except Exception as e:
        return {"error": str(e)}

@router.get("/tiempo")
def estadisticas_por_tiempo(
    job_id: int = Query(None),
    dron_id: int = Query(None),
    origen: str = Query(None),
    intervalo: str = Query("dia")  # opciones: "dia", "semana", "mes"
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        where_clauses = []
        params = []

        if job_id is not None:
            where_clauses.append("d.job_id = %s")
            params.append(job_id)
        if dron_id is not None:
            where_clauses.append("j.dron_id = %s")
            params.append(dron_id)
        if origen is not None:
            where_clauses.append("d.origen = %s")
            params.append(origen)

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Elegir agrupamiento temporal
        if intervalo == "semana":
            agrupamiento = "DATE_TRUNC('week', d.timestamp)"
        elif intervalo == "mes":
            agrupamiento = "DATE_TRUNC('month', d.timestamp)"
        else:
            agrupamiento = "DATE_TRUNC('day', d.timestamp)"

        cur.execute(f"""
            SELECT {agrupamiento} as periodo, COUNT(*) as total
            FROM detecciones d
            JOIN jobs j ON j.id = d.job_id
            {where_sql}
            GROUP BY periodo
            ORDER BY periodo
        """, params)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [{"periodo": row[0].strftime("%Y-%m-%d"), "total": row[1]} for row in rows]

    except Exception as e:
        return {"error": str(e)}

@router.get("/mapa")
def obtener_puntos_mapa(
    job_id: int = Query(None),
    dron_id: int = Query(None),
    origen: str = Query(None),
    class_name: str = Query(None),
    solo_enfermos: bool = Query(True)
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        where_clauses = ["d.geolocation IS NOT NULL"]
        params = []

        if job_id is not None:
            where_clauses.append("d.job_id = %s")
            params.append(job_id)
        if dron_id is not None:
            where_clauses.append("d.dron_id = %s")
            params.append(dron_id)
        if origen is not None:
            where_clauses.append("d.origen = %s")
            params.append(origen)
        if class_name is not None:
            where_clauses.append("det.class_name = %s")
            params.append(class_name)
        elif solo_enfermos:
            where_clauses.append("det.class_name != 'healthy'")

        where_sql = " WHERE " + " AND ".join(where_clauses)

        cur.execute(f"""
            SELECT d.geolocation, det.class_name, det.confidence
            FROM detalle_detecciones det
            JOIN detecciones d ON det.id_deteccion = d.id
            {where_sql}
        """, params)

        filas = cur.fetchall()
        cur.close()
        conn.close()

        resultado = []
        for fila in filas:
            try:
                coords = eval(fila[0])  # geolocation es un texto tipo "[lat, lon]"
                if len(coords) == 2:
                    resultado.append({
                        "lat": coords[0],
                        "lon": coords[1],
                        "class_name": fila[1],
                        "confidence": round(fila[2], 3)
                    })
            except:
                continue

        return resultado

    except Exception as e:
        return {"error": str(e)}