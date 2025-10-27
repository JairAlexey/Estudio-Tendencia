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
    
    # Mostrar estado de las presentaciones
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, status, file_name, file_data, error, tipo_reporte 
            FROM presentation_queue 
            WHERE proyecto_id=%s AND status = 'finished'
            ORDER BY finished_at DESC 
        """, (id,))
        rows = cur.fetchall()
    
    # Botón para actualizar el estado de las presentaciones
    if st.button("🔄 Actualizar Estado", key=f"actualizar_estado_{id}", use_container_width=True):
        st.rerun()

    if rows:
        # Organizar por tipo de reporte
        reportes = {}
        for row in rows:
            queue_id, status, file_name, file_data, error, tipo_reporte = row
            tipo_reporte = tipo_reporte or 'viabilidad'  # Por defecto
            
            if tipo_reporte not in reportes:
                reportes[tipo_reporte] = (queue_id, status, file_name, file_data, error)
                
        # Mostrar pestañas para los diferentes tipos de reportes
        if reportes:
            tab_titles = []
            for tipo in reportes:
                if tipo == 'viabilidad':
                    tab_titles.append("📊 Reporte de Viabilidad")
                elif tipo == 'mercado':
                    tab_titles.append("📈 Investigación de Mercado")
                else:
                    tab_titles.append(f"📑 {tipo.capitalize()}")
            
            tabs = st.tabs(tab_titles)
            
            for i, (tipo, datos) in enumerate(reportes.items()):
                queue_id, status, file_name, file_data, error = datos
                
                with tabs[i]:
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
                            f"💾 Descargar {tipo.capitalize()} PPTX",
                            data=file_data,
                            file_name=file_name or f"presentacion_{tipo}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True,
                            help=f"Descargar la presentación de {tipo} para ver en PowerPoint"
                        )
                        
                    with col2:
                        if st.button("🔄 Regenerar", key=f"regenerar_{tipo}_{id}", use_container_width=True, help=f"Volver a generar la presentación de {tipo}"):
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at, tipo_reporte)
                                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP, %s)
                                """, (id, tipo))
                                conn.commit()
                            st.info(f"✨ Presentación de {tipo} encolada para regeneración.")
                            st.rerun()
    else:
        st.info("📄 No hay presentaciones disponibles para este proyecto.")
        
        # Botones para generar diferentes tipos de presentaciones
        st.subheader("Generar presentaciones")
        
        # Opción para generar ambas presentaciones con un solo botón
        if st.button("✨ Generar Ambas Presentaciones", key=f"generar_ambas_{id}", use_container_width=True):
            with conn.cursor() as cur:
                # Encolar reporte de viabilidad
                cur.execute("""
                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at, tipo_reporte)
                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP, 'viabilidad')
                """, (id,))
                
                # Encolar reporte de mercado
                cur.execute("""
                    INSERT INTO presentation_queue (proyecto_id, status, tries, created_at, tipo_reporte)
                    VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP, 'mercado')
                """, (id,))
                
                conn.commit()
            st.success("✨ Ambas presentaciones encoladas para generación.")
            st.rerun()
        
        # O generar presentaciones individuales
        st.subheader("O generar presentaciones individualmente:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✨ Generar Reporte de Viabilidad", key=f"generar_viabilidad_{id}", use_container_width=True):
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO presentation_queue (proyecto_id, status, tries, created_at, tipo_reporte)
                        VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP, 'viabilidad')
                    """, (id,))
                    conn.commit()
                st.info("✨ Reporte de viabilidad encolado para generación.")
                st.rerun()
                
        with col2:
            if st.button("✨ Generar Investigación de Mercado", key=f"generar_mercado_{id}", use_container_width=True):
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO presentation_queue (proyecto_id, status, tries, created_at, tipo_reporte)
                        VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP, 'mercado')
                    """, (id,))
                    conn.commit()
                st.info("✨ Investigación de mercado encolada para generación.")
                st.rerun()
