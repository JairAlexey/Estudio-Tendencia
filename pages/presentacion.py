import streamlit as st
from conexion import get_connection
from utils.pptx_preview import mostrar_preview_pptx

def mostrar_pagina_presentacion(id):
    """Muestra la página de presentación con estado y opciones de descarga"""
    # Diccionario de traducción y color/ícono para presentación
    estado_traducido_presentacion = {
        "queued": ("En cola", "#6c757d", "⏳"),
        "running": ("Procesando", "#ffc107", "🟡"),
        "finished": ("Completado", "#28a745", "🟢"),
        "error": ("Error", "#dc3545", "🔴"),
    }
    
    # Obtener nombre del proyecto
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=%s", (id,))
        row = cur.fetchone()
        nombre_proyecto = row[0] if row else "Proyecto desconocido"
    
    st.title(f"Presentación generada para: {nombre_proyecto}")
    
    # Mostrar estado de la presentación
    with conn.cursor() as cur:
        cur.execute("""
            SELECT status, file_name, file_data, error 
            FROM presentation_queue 
            WHERE proyecto_id=%s AND status = 'finished'
            ORDER BY finished_at DESC 
            LIMIT 1
        """, (id,))
        row = cur.fetchone()
        
    if row and row[0]:  # Si hay archivo
        status, file_name, file_data, error = row
        
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
        
        texto, color, icono = estado_traducido_presentacion.get(status, (status, "#800080", "🟣"))
        
        st.markdown(f"""
            <div style='border:2px solid {color}; border-radius:12px; padding:1.2rem; margin:1.2rem 0; background:#f8f9fa;'>
                <h4 style='margin:0 0 0.5rem 0;'>Estado de la presentación</h4>
                <div style='font-size:1.1rem; color:{color}; font-weight:bold;'>{icono} {texto}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Mostrar la presentación
        st.write("### Presentación del proyecto")
        mostrar_preview_pptx(file_data)
        
    else:
        st.write("No hay presentación disponible para este proyecto.")
        
    # Botón para generar/regenerar presentación
    if not row or status in ["error"]:
        if st.button("Generar presentación"):
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                """, (id,))
                conn.commit()
            st.info("Presentación encolada para generación.")
            st.rerun()
    # Botón para generar/regenerar presentación
    if not row or status in ["error"]:
        if st.button("Generar presentación"):
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                """, (id,))
                conn.commit()
            st.info("Presentación encolada para generación.")
            st.rerun()
        if st.button("Generar presentación"):
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                """, (id,))
                conn.commit()
            st.info("Presentación encolada para generación.")
            st.rerun()
            st.rerun()
