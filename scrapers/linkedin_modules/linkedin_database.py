import xlwings as xw
import pandas as pd
import os
from conexion import conn, cursor, ensure_connection, is_connected
import datetime

def extraer_datos_tabla(nombre_tabla, proyecto_id):
    """
    Extrae datos de una tabla específica de la base de datos para el proyecto dado.
    """
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede continuar (extraer_datos_tabla).")
        return []
    if nombre_tabla == "reporteLinkedin":
        cursor.execute("""
            SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin
            FROM proyectos_tendencias WHERE id = %s
        """, (proyecto_id,))
        row = cursor.fetchone()
        if row:
            return [{
                "Carpeta": row[0],
                "ProyectoReferencia": row[1],
                "ProyectoEstudio": row[2],
                "PalabraSemrush": row[3],
                "CodigoCIIU": row[4],
                "CarreraLinkedin": row[5]
            }]
        else:
            return []
    elif nombre_tabla == "modalidad_oferta":
        cursor.execute("""
            SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id = %s
        """, (proyecto_id,))
        rows = cursor.fetchall()
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
    elif nombre_tabla == "semrush":
        cursor.execute("""
            SELECT VisionGeneral, Palabras, Volumen FROM semrush WHERE proyecto_id = %s
        """, (proyecto_id,))
        rows = cursor.fetchall()
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
    elif nombre_tabla == "tendencias":
        cursor.execute("""
            SELECT palabra, promedio FROM tendencias WHERE proyecto_id = %s
        """, (proyecto_id,))
        rows = cursor.fetchall()
        return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
    elif nombre_tabla == "linkedin":
        cursor.execute("""
            SELECT Tipo, Region, Profesionales, AnunciosEmpleo, PorcentajeAnunciosProfesionales, DemandaContratacion
            FROM linkedin WHERE proyecto_id = %s
        """, (proyecto_id,))
        rows = cursor.fetchall()
        return [
            dict(zip([desc[0] for desc in cursor.description], row))
            for row in rows
        ]
    else:
        raise ValueError(f"Tabla '{nombre_tabla}' no está permitida.")

def guardar_datos_sql(data, plataforma, proyecto_id):
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede guardar datos.")
        return
    """
    Inserta resultados en la tabla correspondiente de la base de datos.
    """
    if not data:
        print("⚠️ No hay datos para guardar.")
        return

    if plataforma.lower() == "linkedin":
        for item in data:
            cursor.execute("""
                DELETE FROM linkedin WHERE proyecto_id=%s AND Tipo=%s AND Region=%s
            """, (proyecto_id, item.get("Tipo"), item.get("Region")))
            cursor.execute("""
                INSERT INTO linkedin (proyecto_id, Tipo, Region, Profesionales, AnunciosEmpleo, PorcentajeAnunciosProfesionales, DemandaContratacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (proyecto_id, item.get("Tipo"), item.get("Region"), item.get("Profesionales"),
                  item.get("AnunciosEmpleo"), item.get("PorcentajeAnunciosProfesionales"), item.get("DemandaContratacion")))
        conn.commit()
        print("Datos guardados en la tabla 'linkedin'.")

    elif plataforma.lower() == "semrush":
        for item in data:
            cursor.execute("""
                DELETE FROM semrush WHERE proyecto_id=%s AND VisionGeneral=%s AND Palabras=%s AND Volumen=%s
            """, (proyecto_id, item.get("VisionGeneral"), item.get("Palabras"), item.get("Volumen")))
            cursor.execute("""
                INSERT INTO semrush (proyecto_id, VisionGeneral, Palabras, Volumen)
                VALUES (%s, %s, %s, %s)
            """, (proyecto_id, item.get("VisionGeneral"), item.get("Palabras"), item.get("Volumen")))
        conn.commit()
        print("Datos guardados en la tabla 'semrush'.")

    elif plataforma.lower() == "modalidad_oferta":
        for item in data:
            cursor.execute("""
                DELETE FROM modalidad_oferta WHERE proyecto_id=%s AND presencial=%s AND virtual=%s
            """, (proyecto_id, item.get("presencial"), item.get("virtual")))
            cursor.execute("""
                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                VALUES (%s, %s, %s)
            """, (proyecto_id, item.get("presencial"), item.get("virtual")))
        conn.commit()
        print("Datos guardados en la tabla 'modalidad_oferta'.")

    elif plataforma.lower() == "tendencias":
        for item in data:
            cursor.execute("""
                DELETE FROM tendencias WHERE proyecto_id=%s AND palabra=%s AND promedio=%s
            """, (proyecto_id, item.get("palabra"), item.get("promedio")))
            cursor.execute("""
                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                VALUES (%s, %s, %s)
            """, (proyecto_id, item.get("palabra"), item.get("promedio")))
        conn.commit()
        print("Datos guardados en la tabla 'tendencias'.")

    else:
        raise ValueError(f"Plataforma '{plataforma}' no está configurada.")

def obtener_id_carrera(nombre_carrera):
    ensure_connection()
    if not is_connected():
        raise ValueError("No hay conexión a PostgreSQL. No se puede obtener ID de carrera.")
    cursor.execute("SELECT ID FROM carreras_facultad WHERE Carrera = %s", (nombre_carrera,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No se encontró ninguna carrera para '{nombre_carrera}'.")
    return row[0]

def obtener_codigos_por_id_carrera(id_carrera):
    ensure_connection()
    if not is_connected():
        raise ValueError("No hay conexión a PostgreSQL. No se puede obtener códigos de carrera.")
    cursor.execute("SELECT Codigo FROM codigos_carrera WHERE ID_Carrera = %s", (id_carrera,))
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"No se encontraron códigos para ID '{id_carrera}'.")
    return [r[0] for r in rows]

def obtener_semrush_base_por_id(id_carrera):
    ensure_connection()
    if not is_connected():
        raise ValueError("No hay conexión a PostgreSQL. No se puede obtener semrush_base.")
    cursor.execute("""
        SELECT Vision_General, Palabras, Volumen FROM semrush_base WHERE ID_Carrera = %s
    """, (id_carrera,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No se encontró semrush_base para ID_Carrera '{id_carrera}'.")
    return {
        "VisionGeneral": row[0],
        "Palabras": row[1],
        "Volumen": row[2],
    }

def obtener_trends_base_por_id(id_carrera):
    ensure_connection()
    if not is_connected():
        raise ValueError("No hay conexión a PostgreSQL. No se puede obtener tendencias base.")
    cursor.execute("""
        SELECT Palabra, Cantidad FROM tendencias_carrera WHERE ID_Carrera = %s
    """, (id_carrera,))
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"No se encontraron tendencias base para ID_Carrera '{id_carrera}'.")
    return [
        {"Palabra": r[0], "Cantidad": r[1]}
        for r in rows
    ]

def listar_proyectos():
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede listar proyectos.")
        return []
    cursor.execute("""
        SELECT id, tipo_carpeta, carrera_referencia, carrera_estudio FROM proyectos_tendencias ORDER BY id
    """)
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "tipo_carpeta": r[1],
            "carrera_referencia": r[2],
            "carrera_estudio": r[3],
        }
        for r in rows
    ]

# --- Cola de Scrapers ---
def enqueue_scraper_job(proyecto_id):
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede encolar job.")
        return
    cursor.execute(
        """
        INSERT INTO scraper_queue (proyecto_id, status)
        VALUES (%s, 'queued')
        """,
        (proyecto_id,),
    )
    conn.commit()

def fetch_next_job():
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede continuar.")
        return None
    # Buscar jobs en 'queued' o 'retry'
    cursor.execute(
        """
        SELECT id, proyecto_id
        FROM scraper_queue
        WHERE status IN ('queued', 'retry')
        ORDER BY created_at ASC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "proyecto_id": row[1]}
    # Si no hay jobs en cola, buscar jobs 'running' atascados (>10 min)
    cursor.execute(
        """
        SELECT id, proyecto_id, started_at
        FROM scraper_queue
        WHERE status = 'running'
        ORDER BY started_at ASC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    if row:
        started_at = row[2]
        if started_at:
            delta = datetime.datetime.now(datetime.timezone.utc) - started_at
            if delta.total_seconds() > 600:
                cursor.execute(
                    """
                    UPDATE scraper_queue SET status = 'retry', tries = COALESCE(tries,0)+1 WHERE id = %s
                    """,
                    (row[0],),
                )
                conn.commit()
                return {"id": row[0], "proyecto_id": row[1]}
    return None

def mark_job_running(job_id):
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede marcar job como running.")
        return
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = 'running', started_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (job_id,),
    )
    conn.commit()

def mark_job_completed(job_id):
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede marcar job como completed.")
        return
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = 'completed', finished_at = CURRENT_TIMESTAMP, error = NULL
        WHERE id = %s
        """,
        (job_id,),
    )
    conn.commit()

def mark_job_failed(job_id, error_message, max_retries=3):
    ensure_connection()
    if not is_connected():
        print("No hay conexión a PostgreSQL. No se puede marcar job como failed.")
        return
    cursor.execute(
        """
        SELECT tries FROM scraper_queue WHERE id = %s
        """,
        (job_id,),
    )
    row = cursor.fetchone()
    tries = row[0] if row else 0
    tries += 1
    new_status = 'failed' if tries >= max_retries else 'retry'
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = %s, tries = %s, error = %s, finished_at = CASE WHEN %s = 'failed' THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE id = %s
        """,
        (new_status, tries, str(error_message)[:4000], new_status, job_id),
    )
    conn.commit()