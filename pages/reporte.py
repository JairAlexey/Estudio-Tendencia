import streamlit as st
from conexion import get_connection

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
        
        # Mostrar botones en columnas
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "💾 Descargar PPTX",
                data=file_data,
                file_name=file_name or "presentacion.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                help="Descargar la presentación para ver en PowerPoint"
            )
            
        with col2:
            if st.button("🔄 Regenerar", key=f"regenerar_{id}", use_container_width=True, help="Volver a generar la presentación"):
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                        VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                    """, (id,))
                    conn.commit()
                st.info("✨ Presentación encolada para regeneración.")
                st.rerun()
        
    else:
        st.info("📄 No hay presentación disponible para este proyecto.")
        
        # Botón centrado para primera generación
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✨ Generar Presentación", key=f"generar_{id}", use_container_width=True):
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                        VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                    """, (id,))
                    conn.commit()
                st.info("✨ Presentación encolada para generación.")
                st.rerun()
