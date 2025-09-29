# VISTA DEL REPORTE 
import streamlit as st
import pandas as pd
from conexion import get_connection
from scrapers.linkedin_modules.linkedin_database import listar_proyectos
from app import procesar_proyecto

def mostrar_pagina_tabla(id):
    # Obtener nombre del proyecto con manejo de errores y rollback
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=%s", (id,))
        row = cur.fetchone()
        nombre_proyecto = row[0] if row else "Proyecto desconocido"
        nombre_proyecto = " ".join([w.capitalize() for w in nombre_proyecto.split()])
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        st.error(f"Error en la base de datos: {e}")
        return
    cur.close()
    conn.close()

    # Importar la lógica de reporte desde app.py
    try:
        import sys
        sys.path.append(".")
        from scrapers.linkedin_modules.linkedin_database import listar_proyectos
        from app import procesar_proyecto
        proyectos = listar_proyectos()
        proyecto = next((p for p in proyectos if p["id"] == id), None)
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        nombre_pestana = f"{proyecto['id']} - {proyecto['carrera_referencia']} vs {proyecto['carrera_estudio']}"
        st.subheader(f"Evaluación para {nombre_proyecto}")
        with st.spinner("Procesando reporte..."):
            procesar_proyecto(id, nombre_pestana)
        import pandas as pd
        st.subheader("Rango Evaluación Final")
        df_rango = pd.DataFrame(
            {
                "Rango": ["0% - 60%", "61% - 70%", "71% - 100%"],
                "Evaluación": [
                    "Definitivamente No Viable",
                    "Para revisión adicional",
                    "Viable",
                ],
            }
        )
        st.dataframe(df_rango, width="stretch", hide_index=True)
    except Exception as e:
        # Si ocurre un error en la consulta, intentar rollback de la conexión global si existe
        try:
            conn = get_connection()
            cur = conn.cursor()
            conn.rollback()
            cur.close()
            conn.close()
        except Exception:
            pass
        st.error(f"ERROR mostrando reporte: {e}")