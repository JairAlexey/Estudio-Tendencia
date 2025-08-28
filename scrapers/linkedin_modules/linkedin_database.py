import xlwings as xw
import pandas as pd
import os
from conexion import conn, cursor

def extraer_datos_tabla(nombre_tabla, proyecto_id):
    """
    Extrae datos de una tabla específica de la base de datos para el proyecto dado.
    """
    if nombre_tabla == "reporteLinkedin":
        # Ejemplo: podrías tener una tabla 'proyectos_tendencias' con la configuración del proyecto
        cursor.execute("""
            SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu
            FROM proyectos_tendencias WHERE id = ?
        """, proyecto_id)
        row = cursor.fetchone()
        if row:
            return [{
                "Carpeta": row.tipo_carpeta,
                "ProyectoReferencia": row.carrera_referencia,
                "ProyectoEstudio": row.carrera_estudio,
                "PalabraSemrush": row.palabra_semrush,
                "CodigoCIIU": row.codigo_ciiu
            }]
        else:
            return []
    elif nombre_tabla == "modalidad_oferta":
        cursor.execute("""
            SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id = ?
        """, proyecto_id)
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    elif nombre_tabla == "semrush":
        cursor.execute("""
            SELECT VisionGeneral, Palabras, Volumen FROM semrush WHERE proyecto_id = ?
        """, proyecto_id)
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    elif nombre_tabla == "tendencias":
        cursor.execute("""
            SELECT palabra, promedio FROM tendencias WHERE proyecto_id = ?
        """, proyecto_id)
        rows = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    elif nombre_tabla == "linkedin":
        cursor.execute("""
            SELECT Tipo, Region, Profesionales, AnunciosEmpleo, PorcentajeAnunciosProfesionales, DemandaContratacion
            FROM linkedin WHERE proyecto_id = ?
        """, proyecto_id)
        rows = cursor.fetchall()
        return [
            dict(zip([column[0] for column in cursor.description], row))
            for row in rows
        ]
    else:
        raise ValueError(f"Tabla '{nombre_tabla}' no está permitida.")

def guardar_datos_sql(data, plataforma, proyecto_id):
    """
    Inserta resultados en la tabla correspondiente de la base de datos.
    """
    if not data:
        print("⚠️ No hay datos para guardar.")
        return

    if plataforma.lower() == "linkedin":
        for item in data:
            cursor.execute("""
                INSERT INTO linkedin (proyecto_id, Tipo, Region, Profesionales, AnunciosEmpleo, PorcentajeAnunciosProfesionales, DemandaContratacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, proyecto_id, item.get("Tipo"), item.get("Region"), item.get("Profesionales"),
                 item.get("AnunciosEmpleo"), item.get("PorcentajeAnunciosProfesionales"), item.get("DemandaContratacion"))
        conn.commit()
        print("Datos guardados en la tabla 'linkedin'.")

    elif plataforma.lower() == "semrush":
        for item in data:
            cursor.execute("""
                INSERT INTO semrush (proyecto_id, VisionGeneral, Palabras, Volumen)
                VALUES (?, ?, ?, ?)
            """, proyecto_id, item.get("VisionGeneral"), item.get("Palabras"), item.get("Volumen"))
        conn.commit()
        print("Datos guardados en la tabla 'semrush'.")

    elif plataforma.lower() == "modalidad_oferta":
        for item in data:
            cursor.execute("""
                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                VALUES (?, ?, ?)
            """, proyecto_id, item.get("presencial"), item.get("virtual"))
        conn.commit()
        print("Datos guardados en la tabla 'modalidad_oferta'.")

    elif plataforma.lower() == "tendencias":
        for item in data:
            cursor.execute("""
                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                VALUES (?, ?, ?)
            """, proyecto_id, item.get("palabra"), item.get("promedio"))
        conn.commit()
        print("Datos guardados en la tabla 'tendencias'.")

    else:
        raise ValueError(f"Plataforma '{plataforma}' no está configurada.")

def obtener_id_carrera(nombre_carrera):
    cursor.execute("SELECT ID FROM carreras_facultad WHERE Carrera = ?", nombre_carrera)
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No se encontró ninguna carrera para '{nombre_carrera}'.")
    return row.ID

def obtener_codigos_por_id_carrera(id_carrera):
    cursor.execute("SELECT Codigo FROM codigos_carrera WHERE ID_Carrera = ?", id_carrera)
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"No se encontraron códigos para ID '{id_carrera}'.")
    return [r.Codigo for r in rows]

def obtener_semrush_base_por_id(id_carrera):
    cursor.execute("""
        SELECT Vision_General, Palabras, Volumen FROM semrush_base WHERE ID_Carrera = ?
    """, id_carrera)
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No se encontró semrush_base para ID_Carrera '{id_carrera}'.")
    return {
        "VisionGeneral": row.Vision_General,
        "Palabras": row.Palabras,
        "Volumen": row.Volumen,
    }

def obtener_trends_base_por_id(id_carrera):
    cursor.execute("""
        SELECT Palabra, Cantidad FROM tendencias_carrera WHERE ID_Carrera = ?
    """, id_carrera)
    rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"No se encontraron tendencias base para ID_Carrera '{id_carrera}'.")
    return [
        {"Palabra": r.Palabra, "Cantidad": r.Cantidad}
        for r in rows
    ]

def listar_proyectos():
    cursor.execute("""
        SELECT id, tipo_carpeta, carrera_referencia, carrera_estudio FROM proyectos_tendencias ORDER BY id
    """)
    rows = cursor.fetchall()
    return [
        {
            "id": r.id,
            "tipo_carpeta": r.tipo_carpeta,
            "carrera_referencia": r.carrera_referencia,
            "carrera_estudio": r.carrera_estudio,
        }
        for r in rows
    ]

# --- Cola de Scrapers ---
def enqueue_scraper_job(proyecto_id):
    cursor.execute(
        """
        INSERT INTO scraper_queue (proyecto_id, status)
        VALUES (?, 'queued')
        """,
        proyecto_id,
    )
    conn.commit()

def fetch_next_job():
    cursor.execute(
        """
        SELECT TOP 1 id, proyecto_id
        FROM scraper_queue
        WHERE status IN ('queued', 'retry')
        ORDER BY created_at ASC
        """
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {"id": row.id, "proyecto_id": row.proyecto_id}

def mark_job_running(job_id):
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = 'running', started_at = GETDATE()
        WHERE id = ?
        """,
        job_id,
    )
    conn.commit()

def mark_job_completed(job_id):
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = 'completed', finished_at = GETDATE(), error = NULL
        WHERE id = ?
        """,
        job_id,
    )
    conn.commit()

def mark_job_failed(job_id, error_message, max_retries=3):
    cursor.execute(
        """
        SELECT tries FROM scraper_queue WHERE id = ?
        """,
        job_id,
    )
    row = cursor.fetchone()
    tries = row.tries if row else 0
    tries += 1
    new_status = 'failed' if tries >= max_retries else 'retry'
    cursor.execute(
        """
        UPDATE scraper_queue
        SET status = ?, tries = ?, error = ?, finished_at = CASE WHEN ? = 'failed' THEN GETDATE() ELSE NULL END
        WHERE id = ?
        """,
        new_status, tries, str(error_message)[:4000], new_status, job_id,
    )
    conn.commit()