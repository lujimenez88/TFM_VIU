from app.database import get_connection
from app.models import JobIn, JobUpdate


def crear_job(job: JobIn):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Verificar si ya hay un job activo con ese dron
        cur.execute("SELECT id FROM jobs WHERE dron_id = %s AND estado = 'activo'", (job.dron_id,))
        conflict = cur.fetchone()
        if conflict:
            return None  # ya existe un job activo con ese dron

        cur.execute(
            """
            INSERT INTO jobs (nombre, descripcion, dron_id)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, descripcion, estado, dron_id
            """,
            (job.nombre, job.descripcion, job.dron_id)
        )
        row = cur.fetchone()
        conn.commit()
        return {
            "id": row[0],
            "nombre": row[1],
            "descripcion": row[2],
            "estado": row[3],
            "dron_id": row[4]
        }
    except Exception as e:
        print("❌ Error al crear job:", e)
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()


def listar_jobs(estado=None, dron_id=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        condiciones = []
        params = []
        if estado:
            condiciones.append("estado = %s")
            params.append(estado)
        if dron_id:
            condiciones.append("dron_id = %s")
            params.append(dron_id)

        where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        cur.execute(
            f"""
            SELECT id, nombre, descripcion, estado, dron_id
            FROM jobs
            {where}
            ORDER BY id DESC
            """,
            params
        )
        rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "nombre": r[1],
                "descripcion": r[2],
                "estado": r[3],
                "dron_id": r[4],
            }
            for r in rows
        ]
    except Exception as e:
        print("❌ Error al listar jobs:", e)
        return []
    finally:
        cur.close()
        conn.close()


def actualizar_job(job_id: int, job_data: JobUpdate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        campos = []
        valores = []
        if job_data.dron_id is not None:
            campos.append("dron_id = %s")
            valores.append(job_data.dron_id)
        if job_data.estado is not None:
            campos.append("estado = %s")
            valores.append(job_data.estado)

        if not campos:
            return None

        valores.append(job_id)

        cur.execute(
            f"""
            UPDATE jobs
            SET {', '.join(campos)}
            WHERE id = %s
            RETURNING id, nombre, descripcion, estado, dron_id
            """,
            valores
        )
        row = cur.fetchone()
        conn.commit()
        if not row:
            return None

        return {
            "id": row[0],
            "nombre": row[1],
            "descripcion": row[2],
            "estado": row[3],
            "dron_id": row[4]
        }
    except Exception as e:
        print("❌ Error al actualizar job:", e)
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()
