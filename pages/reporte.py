# VISTA DEL REPORTE 
import streamlit as st
import pandas as pd
from conexion import conn
from scrapers.linkedin_modules.linkedin_database import listar_proyectos
from app import procesar_proyecto

def mostrar_pagina_reporte(proyecto_id):
    st.title("Reporte de Proyecto")
    
    # Obtener datos del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM proyectos_tendencias WHERE id=%s", (proyecto_id,))
        proyecto = cur.fetchone()
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto[1:7]
        nombre_proyecto = " ".join([w.capitalize() for w in carrera_estudio.split()])

    # 1. Información General
    st.subheader("Datos del Proyecto")
    st.write(f"**Tipo de carpeta:** {tipo_carpeta}")
    st.write(f"**Carrera Referencia:** {carrera_referencia}")
    st.write(f"**Carrera Estudio:** {carrera_estudio}")
    st.write(f"**Palabra SEMRUSH:** {palabra_semrush}")
    st.write(f"**Código CIIU:** {codigo_ciiu}")
    st.write(f"**Carrera LinkedIn:** {carrera_linkedin}")

    # 2. Tendencias
    st.subheader("Tendencias")
    with conn.cursor() as cur:
        cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=%s", (proyecto_id,))
        tendencias = cur.fetchall()
    
    if tendencias:
        df_tendencias = pd.DataFrame(tendencias, columns=["Palabra", "Promedio"])
        st.dataframe(df_tendencias)
    else:
        st.write("No hay tendencias disponibles para este proyecto.")

    # 3. Modalidad de Oferta
    st.subheader("Modalidad de Oferta")
    with conn.cursor() as cur:
        cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=%s", (proyecto_id,))
        modalidad = cur.fetchall()
    
    if modalidad:
        df_modalidad = pd.DataFrame(modalidad, columns=["Presencial", "Virtual"])
        st.dataframe(df_modalidad)
    else:
        st.write("No hay información de modalidad de oferta para este proyecto.")

    # 4. Evaluación y Reporte
    st.subheader(f"Evaluación para {nombre_proyecto}")
    with st.spinner("Procesando reporte..."):
        try:
            nombre_pestana = f"{proyecto_id} - {carrera_referencia} vs {carrera_estudio}"
            procesar_proyecto(proyecto_id, nombre_pestana)
            
            # Mostrar rango de evaluación
            st.subheader("Rango Evaluación Final")
            df_rango = pd.DataFrame({
                "Rango": ["0% - 60%", "61% - 70%", "71% - 100%"],
                "Evaluación": ["Definitivamente No Viable", "Para revisión adicional", "Viable"],
            })
            st.dataframe(df_rango, width="stretch", hide_index=True)
        except Exception as e:
            st.error(f"Error procesando evaluación: {e}")