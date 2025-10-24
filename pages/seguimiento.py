import streamlit as st
import sys
import os

# Add the parent directory to sys.path to find the conexion module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the parent directory
from conexion import get_connection

def generar_timeline_seguimiento(seguimiento, scraper_status):
    """
    Genera el HTML del timeline basado en los datos de seguimiento
    """
    if not seguimiento:
        return ""
    
    brief, modelo_prioridad, modelo_tendencia, enviada_viabilidad, solicitud_inv_mercados, enviada_inv_mercados, created_at, updated_at = seguimiento
    
    # Determinar estado del modelo de tendencia basado en scraper
    if scraper_status:
        scraper_estado = scraper_status[0]  # status del scraper
        modelo_tendencia_completado = scraper_estado == "completed"
        scraper_finished_at = scraper_status[3] if len(scraper_status) > 3 else None
    else:
        modelo_tendencia_completado = False
        scraper_finished_at = None
    
    # Formatear fechas
    def formatear_fecha(fecha):
        if fecha:
            return fecha.strftime('%d/%m/%Y %H:%M')
        return 'N/A'
    
    # Determinar qué fases mostrar basado en el progreso
    fases = [
        {
            'nombre': 'Brief',
            'completado': True,  # Siempre completado
            'descripcion': 'Información del proyecto registrada',
            'fecha': created_at
        },
        {
            'nombre': 'Modelo de Prioridad',
            'completado': True,  # Siempre completado
            'descripcion': 'Prioridad asignada al proyecto',
            'fecha': created_at
        },
        {
            'nombre': 'Modelo de Tendencia',
            'completado': modelo_tendencia_completado,
            'descripcion': 'Análisis de tendencias completado' if modelo_tendencia_completado else 'En proceso de análisis',
            'fecha': scraper_finished_at if modelo_tendencia_completado else None
        },
        {
            'nombre': 'Enviada la Viabilidad',
            'completado': enviada_viabilidad,
            'descripcion': 'Reporte de viabilidad enviado' if enviada_viabilidad else 'Pendiente de envío',
            'fecha': updated_at if enviada_viabilidad else None
        },
        {
            'nombre': 'Solicitud Inv. de Mercados',
            'completado': solicitud_inv_mercados,
            'descripcion': 'Solicitud de investigación enviada' if solicitud_inv_mercados else 'Pendiente de solicitud',
            'fecha': updated_at if solicitud_inv_mercados else None
        },
        {
            'nombre': 'Enviada la Inv. de Mercados',
            'completado': enviada_inv_mercados,
            'descripcion': 'Investigación de mercados enviada' if enviada_inv_mercados else 'Pendiente de envío',
            'fecha': updated_at if enviada_inv_mercados else None
        }
    ]
    
    # Encontrar la última fase completada
    ultima_fase_completada = -1
    for i, fase in enumerate(fases):
        if fase['completado']:
            ultima_fase_completada = i
    
    # Mostrar solo hasta la siguiente fase después de la última completada
    fases_a_mostrar = fases[:ultima_fase_completada + 2] if ultima_fase_completada < len(fases) - 1 else fases
    
    # Generar el HTML completo de una vez
    timeline_html = "<div class=\"timeline\">"
    
    for fase in fases_a_mostrar:
        estado_clase = "completed" if fase['completado'] else ""
        fecha_texto = formatear_fecha(fase['fecha']) if fase['completado'] else ('En proceso' if fase['nombre'] == 'Modelo de Tendencia' else 'Pendiente')
        
        timeline_html += f"<div class=\"step {estado_clase}\"><h4>{fase['nombre']}</h4><p>{fase['descripcion']}</p><small style=\"color: #666; font-size: 12px;\">{fecha_texto}</small></div>"
    
    timeline_html += "</div>"
    
    return timeline_html

def obtener_datos_seguimiento(proyecto_id):
    """
    Obtiene los datos de seguimiento para un proyecto específico
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Obtener datos de seguimiento
            cur.execute("""
                SELECT brief, modelo_prioridad, modelo_tendencia, 
                       enviada_viabilidad, solicitud_inv_mercados, enviada_inv_mercados, 
                       created_at, updated_at
                FROM seguimiento_proyecto 
                WHERE proyecto_id = %s
            """, (proyecto_id,))
            
            seguimiento = cur.fetchone()
            
            # Obtener estado del scraper
            cur.execute("""
                SELECT status, created_at, started_at, finished_at
                FROM scraper_queue 
                WHERE proyecto_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (proyecto_id,))
            
            scraper_status = cur.fetchone()
            
            conn.close()
            
            return seguimiento, scraper_status
                
    except Exception as e:
        st.error(f"Error consultando la base de datos: {e}")
        return None, None

def actualizar_estado_seguimiento(proyecto_id, enviada_viabilidad, solicitud_inv_mercados, enviada_inv_mercados):
    """
    Actualiza los estados de seguimiento en la base de datos
    """
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE seguimiento_proyecto 
                SET enviada_viabilidad = %s, 
                    solicitud_inv_mercados = %s, 
                    enviada_inv_mercados = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE proyecto_id = %s
            """, (enviada_viabilidad, solicitud_inv_mercados, enviada_inv_mercados, proyecto_id))
            
            conn.commit()
            conn.close()
            return True
            
    except Exception as e:
        st.error(f"Error actualizando el seguimiento: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def mostrar_pagina_seguimiento(proyecto_id):
    """
    Muestra la página de seguimiento para un proyecto específico
    """
    # Botón de volver
    if st.button("⬅️ Volver", key="volver_inicio_seguimiento"):
        st.session_state["page"] = "proyectos"
        st.rerun()
    
    st.title("Seguimiento del Proyecto")
    
    # Obtener datos de seguimiento
    seguimiento, scraper_status = obtener_datos_seguimiento(proyecto_id)
    
    if not seguimiento:
        st.error("No se encontraron datos de seguimiento para este proyecto.")
        return
    
    # Extraer datos del seguimiento
    brief, modelo_prioridad, modelo_tendencia, enviada_viabilidad, solicitud_inv_mercados, enviada_inv_mercados, created_at, updated_at = seguimiento
    
    # Sección de configuración de estados
    st.markdown("### ⚙️ Configurar Estados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selectbox para Enviada Viabilidad
        nueva_enviada_viabilidad = st.selectbox(
            "Enviada la Viabilidad",
            ["No", "Sí"],
            index=1 if enviada_viabilidad else 0,
            key=f"viabilidad_{proyecto_id}"
        )
        
        # Selectbox para Solicitud Inv. de Mercados
        nueva_solicitud_inv_mercados = st.selectbox(
            "Solicitud Inv. de Mercados",
            ["No", "Sí"],
            index=1 if solicitud_inv_mercados else 0,
            key=f"solicitud_{proyecto_id}"
        )
    
    with col2:
        # Selectbox para Enviada Inv. de Mercados (solo si solicitud_inv_mercados es True)
        if solicitud_inv_mercados:
            nueva_enviada_inv_mercados = st.selectbox(
                "Enviada la Inv. de Mercados",
                ["No", "Sí"],
                index=1 if enviada_inv_mercados else 0,
                key=f"enviada_inv_{proyecto_id}"
            )
        else:
            nueva_enviada_inv_mercados = False
            st.info("💡 Para modificar solicitud de investigación, complete primero 'Solicitud Inv. de Mercados'")
    
    # Botón para guardar cambios
    if st.button("💾 Guardar Cambios", type="primary", key=f"guardar_{proyecto_id}"):
        # Convertir valores de string a boolean
        enviada_viabilidad_bool = nueva_enviada_viabilidad == "Sí"
        solicitud_inv_mercados_bool = nueva_solicitud_inv_mercados == "Sí"
        enviada_inv_mercados_bool = nueva_enviada_inv_mercados == "Sí" if solicitud_inv_mercados_bool else False
        
        # Actualizar en la base de datos
        if actualizar_estado_seguimiento(proyecto_id, enviada_viabilidad_bool, solicitud_inv_mercados_bool, enviada_inv_mercados_bool):
            st.success("✅ Estados actualizados correctamente!")
            st.rerun()
        else:
            st.error("❌ Error al actualizar los estados")
    
    st.markdown("---")
    
    # Mostrar timeline cuando hay datos
    # Timeline CSS con colores rojos
    st.markdown("""
        <style>
        .timeline {
            border-left: 3px solid #DC143C;
            margin-left: 25px;
            padding-left: 25px;
            position: relative;
        }

        .step {
            margin-bottom: 35px;
            position: relative;
        }

        .step::before {
            content: "";
            position: absolute;
            left: -36px;
            top: 0;
            width: 22px;
            height: 22px;
            background-color: white;
            border-radius: 50%;
            border: 3px solid #DC143C;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
            color: white;
            text-align: center;
        }

        /* Pasos completados: con check y fondo rojo */
        .step.completed::before {
            content: "✓";
            background-color: #DC143C;
            color: white;
            border: 3px solid #DC143C;
        }

        /* Texto */
        .step h4 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #222;
        }

        .step p {
            margin: 0;
            color: gray;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Timeline HTML dinámico
    timeline_html = generar_timeline_seguimiento(seguimiento, scraper_status)
    st.markdown(timeline_html, unsafe_allow_html=True)
    
    # Botón de actualizar
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Actualizar", type="primary", use_container_width=True):
            st.rerun()
