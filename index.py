import streamlit as st
import pandas as pd
import time
from streamlit_option_menu import option_menu
from conexion import get_connection

# Helper para obtener conexión y cursor
def get_conn_cursor():
    conn = get_connection()
    return conn, conn.cursor()

# --- Navegación ---
def mostrar_navegacion(key):
    selected = option_menu(
        menu_title=None,  # Oculta título
        options=["Inicio", "Formulario"],
        icons=["house", "ui-checks"],  # Iconos de Bootstrap
        menu_icon="cast",
        default_index=0 if st.session_state.get("page", "inicio") == "inicio" else 1,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#1e293b"},
            "icon": {"color": "#cbd5e1", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "color": "#cbd5e1",
                "--hover-color": "#334155",
            },
            "nav-link-selected": {"background-color": "#ff0000", "color": "white"},
        },
        key=key 
    )
    # Solo actualiza la página si no está en una acción especial
    # Si se acaba de guardar exitosamente, no sobrescribir la página
    if st.session_state.get("exito_guardado"):
        return "inicio"
    if st.session_state.get("page", "inicio") in ["inicio", "formulario", "form", "f"]:
        st.session_state["page"] = selected.lower()
    return st.session_state["page"]


# --- Página de inicio ---
def pagina_inicio():
    # Mostrar mensaje de éxito si viene de guardar en el formulario
    if st.session_state.get("exito_guardado"):
        st.success("Datos guardados en la base de datos correctamente.")
        # Deshabilitar botones mientras el mensaje está activo
        st.session_state["botones_deshabilitados"] = True
        # Limpiar la bandera después de mostrar el mensaje y esperar 2 segundos
        st.session_state["exito_guardado"] = False
        st.query_params.clear() 
        st.markdown(
            """
            <script>
            setTimeout(function() {
                window.location.reload();
            }, 2000);
            </script>
            """,
            unsafe_allow_html=True
        )
        return  # No mostrar botones ni proyectos mientras el mensaje está activo

    st.session_state["botones_deshabilitados"] = False
    st.title("Proyectos en la Base de Datos")
    
    st.markdown("""
        <style>
        div[data-testid="stTextInputRootElement"] {
            border:2px solid #ff0000 !important;
            border-radius:10px !important;
            padding:0.75rem 1rem !important;
            margin-bottom:1rem !important;
            background:#f8f9fa !important;
            box-shadow:2px 2px 6px rgba(0,0,0,0.08) !important;
            display:flex !important;
            align-items:center !important;
            position:relative !important;
        }
        div[data-testid="stTextInputRootElement"]::before {
            content: '';
            display: block;
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='%23ff0000' class='bi bi-search' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.442 1.398a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-size: 20px 20px;
            pointer-events: none;
        }
        div[data-testid="stTextInputRootElement"] input {
            border:none !important;
            background:transparent !important;
            font-size:1rem !important;
            color:#222 !important;
            box-shadow:none !important;
            padding-left:2.2rem !important;
        }
        /* Botones personalizados por columna */
        div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] {
            min-width: 125px;
            height: 38px; /* un poco más alto para texto */
            border-radius: 8px !important;
            font-weight: 600;
            font-size: 15px;
            margin: 0 2px;
            background-color: #f8f9fa !important;
            color: #222 !important;
            border: 1px solid #ddd !important;
            box-shadow: none !important;
            padding: 0 8px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] span.small-btn-label {
            font-size: 11px !important;
            font-weight: 400 !important;
            margin-top: -2px !important;
            color: #444 !important;
            letter-spacing: 0.2px;
        }
        /* Solo el botón Eliminar será rojo */
        div[data-testid="stColumn"]:nth-child(5) button[data-testid="stBaseButton-secondary"] {
            background-color: #ff0000 !important;
            color: #fff !important;
            border: 1px solid #ff0000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    search_query = st.text_input("Buscar proyecto por nombre o tipo de carpeta", key="search_query", label_visibility="collapsed")
    
    conn, cur = get_conn_cursor()
    try:
        cur.execute("SELECT id, carrera_estudio, tipo_carpeta, mensaje_error FROM proyectos_tendencias ORDER BY id DESC")
        proyectos = cur.fetchall()
        # Traer último estado de scraper por proyecto
        cur.execute(
            """
            SELECT proyecto_id, status
            FROM (
                SELECT proyecto_id, status,
                       ROW_NUMBER() OVER (PARTITION BY proyecto_id ORDER BY created_at DESC) rn
                FROM scraper_queue
            ) t WHERE rn = 1
            """
        )
        estados = {row[0]: row[1] for row in cur.fetchall()}
    except Exception as e:
        conn.rollback()
        st.error(f"Error en la base de datos: {e}")
        cur.close()
        conn.close()
        return
    cur.close()
    conn.close()

    # Diccionario de traducción y color/ícono
    estado_traducido = {
        "pending": ("En cola", "#6c757d", "⏳"),      # Gris
        "running": ("Procesando", "#ffc107", "🟡"),  # Amarillo
        "completed": ("Completado", "#28a745", "🟢"),# Verde
        "error": ("Error", "#dc3545", "🔴"),         # Rojo
    }

    if not proyectos:
        st.info("No hay proyectos registrados.")
        return

    if search_query:
        proyectos = [p for p in proyectos if search_query.lower() in p[1].lower() or search_query.lower() in p[2].lower()]
    else:
        proyectos = proyectos[:3]

    for proyecto in proyectos:
        id, nombre, tipo, mensaje_error = proyecto
        # Línea negra de separación
        st.markdown("""
            <hr style='border: none; border-top: 3px solid #222; margin: 1.2rem 0 1.5rem 0;'>
        """, unsafe_allow_html=True)

        # Card estilo Material con estado traducido y color
        estado = estados.get(id, None)
        if estado in estado_traducido:
            texto, color, icono = estado_traducido[estado]
            estado_html = f"<span style='color:#555; font-size:0.95rem;'>Estado:</span> <span style='color:{color}; font-size:0.95rem;'>{icono} {texto}</span>"
        else:
            estado_html = "<span style='color:#555; font-size:0.95rem;'>Estado:</span> <span style='color:#800080; font-size:0.95rem;'>🟣 En espera</span>"

        # Verificar si existen datos de solicitud para este proyecto
        try:
            conn2, cur2 = get_conn_cursor()
            cur2.execute("SELECT COUNT(*) FROM datos_solicitud WHERE proyecto_id=%s", (id,))
            solicitud_count = cur2.fetchone()[0]
            cur2.close()
            conn2.close()
        except Exception as e:
            st.error(f"Error en la base de datos (datos_solicitud): {e}")
            return
        if solicitud_count > 0:
            solicitud_html = "<span style='color:#555; font-size:0.95rem;'>Datos solicitud:</span> <span style='color:#28a745; font-size:0.95rem;'>🟢 Agregados</span>"
        else:
            solicitud_html = "<span style='color:#555; font-size:0.95rem;'>Datos solicitud:</span> <span style='color:#dc3545; font-size:0.95rem;'>🔴 No agregados</span>"

        error_icon_html = ""
        if mensaje_error:
            error_icon_html = "<span style='color:#dc3545; font-size:1.2em;' title='Error en scraper'>❗</span>"
        st.markdown(f"""
            <div style='
                border:1px solid #ddd; 
                border-radius:10px; 
                padding:1rem; 
                margin-bottom:0.5rem; 
                background:#f8f9fa;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
            '>
                <h4 style='margin:0'>{nombre} {error_icon_html}</h4>
                <p style='margin:0; color:#555;'>{tipo}</p>
                <div style='margin-top:0.25rem; font-size: 0.9rem;'>
                    <div>{estado_html}</div>
                    <div>{solicitud_html}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Mostrar botón para ver el mensaje de error si existe
        if mensaje_error:
            if st.button(f"Ver error del scraper", key=f"ver_error_{id}"):
                st.warning(mensaje_error)

        col1, col2, col3, col4, col5 = st.columns(5)
        disabled = st.session_state.get("botones_deshabilitados", False)
        with col1:
            st.button("✏️ Editar", key=f"editar_{id}", disabled=disabled, help="Editar")
            if not disabled and st.session_state.get(f"editar_{id}"):
                st.session_state["page"] = "editar"
                st.session_state["id"] = id
                st.rerun()
        with col2:
            st.button("ℹ️ Agregar", key=f"info_{id}", disabled=disabled, help="Agregar")
            if not disabled and st.session_state.get(f"info_{id}"):
                st.session_state["page"] = "datos_solicitud"
                st.session_state["id"] = id
                st.rerun()
        with col3:
            reporte_disabled = disabled or estado != "completed"
            st.button("📑 Tabla", key=f"reporte_{id}", disabled=reporte_disabled, help="Tabla")
            if not reporte_disabled and st.session_state.get(f"reporte_{id}"):
                st.session_state["page"] = "reporte"
                st.session_state["id"] = id
                st.rerun()
        with col4:
            st.button("📊 Reporte", key=f"presentacion_{id}", disabled=disabled, help="Reporte")
            if not disabled and st.session_state.get(f"presentacion_{id}"):
                st.session_state["page"] = "presentacion"
                st.session_state["id"] = id
                st.rerun()            
        with col5:
            st.button("🗑️ Eliminar", key=f"eliminar_{id}", disabled=disabled, help="Eliminar")
            if not disabled and st.session_state.get(f"eliminar_{id}"):
                st.session_state["confirmar_eliminar_id"] = id
                st.session_state["confirmar_eliminar_nombre"] = nombre
                st.session_state["confirmar_eliminar_tipo"] = tipo
                st.session_state["mostrar_confirmacion_eliminar"] = True

        # Mostrar advertencia de confirmación si corresponde
        if st.session_state.get("mostrar_confirmacion_eliminar") and st.session_state.get("confirmar_eliminar_id") == id:
            st.warning(f"¿Está seguro que desea eliminar el proyecto '{nombre}' ({tipo})? Esta acción no se puede deshacer.")
            confirmar = st.button("Sí, eliminar definitivamente", key=f"confirmar_eliminar_{id}")
            cancelar = st.button("Cancelar", key=f"cancelar_eliminar_{id}")
            if confirmar:
                try:
                    conn3, cur3 = get_conn_cursor()
                    # Eliminar de todas las tablas relacionadas
                    cur3.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM tendencias WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM linkedin WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM semrush WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM scraper_queue WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM grafico_radar_datos WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM presentation_queue WHERE proyecto_id=%s", (id,))
                    cur3.execute("DELETE FROM datos_solicitud WHERE proyecto_id=%s", (id,))
                    # Eliminar el proyecto principal
                    cur3.execute("DELETE FROM proyectos_tendencias WHERE id=%s", (id,))
                    conn3.commit()
                    cur3.close()
                    conn3.close()
                    st.success("Proyecto eliminado correctamente")
                    st.session_state["mostrar_confirmacion_eliminar"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error eliminando proyecto: {e}")
                    return
            elif cancelar:
                st.session_state["mostrar_confirmacion_eliminar"] = False
                st.session_state["confirmar_eliminar_id"] = None
                st.session_state["confirmar_eliminar_nombre"] = None
                st.session_state["confirmar_eliminar_tipo"] = None
                st.rerun()

# --- Editar proyecto ---
def pagina_editar(id):
    if st.button("Regresar al inicio", key="volver_inicio_editar"):
        st.session_state["page"] = "inicio"
        st.rerun()
    try:
        import sys
        sys.path.append(".")
        sys.path.append("./forms")
        from forms import form
        if hasattr(form, "mostrar_formulario_edicion"):
            form.mostrar_formulario_edicion(id)
        else:
            st.warning("No se encontró la función mostrar_formulario_edicion en forms/form.py")
    except Exception as e:
        st.error(f"ERROR: {e}")


# --- Eliminar proyecto ---
def pagina_eliminar(id):
    st.title("Eliminar Proyecto")
    conn, cur = get_conn_cursor()
    cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=%s", (id,))
    proyecto = cur.fetchone()
    cur.close()
    conn.close()
    if not proyecto:
        st.error("Proyecto no encontrado.")
        return
    st.warning(f"¿Está seguro que desea eliminar el proyecto '{proyecto[0]}'?")
    if st.button("Eliminar definitivamente"):
        try:
            conn2, cur2 = get_conn_cursor()
            cur2.execute("DELETE FROM proyectos_tendencias WHERE id=%s", (id,))
            conn2.commit()
            cur2.close()
            conn2.close()
            st.success("Proyecto eliminado correctamente.")
            st.query_params.update({"page": "inicio"})
            st.rerun()
        except Exception as e:
            st.error(f"Error eliminando proyecto: {e}")
            return

# --- Formulario ---
def pagina_formulario():
    # Limpiar los campos del formulario al entrar
    if st.session_state.get("limpiar_formulario", True):
        import pandas as pd
        st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
        st.session_state["search_query"] = ""
        st.session_state["limpiar_formulario"] = False
    st.title("Formulario de Proyectos y Tendencias")
    try:
        import sys
        sys.path.append(".")
        sys.path.append("./forms")
        from forms import form
        if hasattr(form, "mostrar_formulario"):
            form.mostrar_formulario()
        else:
            st.warning("No se encontró la función mostrar_formulario en forms/form.py")
    except Exception as e:
        st.error(f"ERROR: {e}")

# --- Reporte proyecto ---
def pagina_reporte(id):
    # Obtener nombre del proyecto con manejo de errores y rollback
    conn, cur = get_conn_cursor()
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

    if st.button("Regresar al inicio", key="volver_inicio_ver"):
        st.session_state["page"] = "inicio"
        st.rerun()

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
            conn, cur = get_conn_cursor()
            conn.rollback()
            cur.close()
            conn.close()
        except Exception:
            pass
        st.error(f"ERROR mostrando reporte: {e}")
        
# --- Presentación ---
def pagina_presentacion(id):
    # Diccionario de traducción y color/ícono para presentación
    estado_traducido_presentacion = {
        "queued": ("En cola", "#6c757d", "⏳"),
        "running": ("Procesando", "#ffc107", "🟡"),
        "finished": ("Completado", "#28a745", "🟢"),
        "error": ("Error", "#dc3545", "🔴"),
    }
    # Obtener nombre del proyecto
    conn, cur = get_conn_cursor()
    cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=%s", (id,))
    row = cur.fetchone()
    nombre_proyecto = row[0] if row else "Proyecto desconocido"
    cur.close()
    conn.close()
    st.title(f"Presentación generada para: {nombre_proyecto}")
    if st.button("Regresar al inicio", key="volver_inicio_presentacion"):
        st.session_state["page"] = "inicio"
        st.rerun()
    # Mostrar estado de la presentación
    conn2, cur2 = get_conn_cursor()
    cur2.execute("SELECT status, file_name, file_data, error FROM presentation_queue WHERE proyecto_id=%s ORDER BY created_at DESC", (id,))
    row = cur2.fetchone()
    cur2.close()
    conn2.close()
    status = None
    if row:
        status, file_name, file_data, error = row
        texto, color, icono = estado_traducido_presentacion.get(status, (status, "#800080", "🟣"))
        st.markdown(f"""
            <div style='border:2px solid {color}; border-radius:12px; padding:1.2rem; margin:1.2rem 0; background:#f8f9fa;'>
                <h4 style='margin:0 0 0.5rem 0;'>Estado de la presentación</h4>
                <div style='font-size:1.1rem; color:{color}; font-weight:bold;'>{icono} {texto}</div>
            </div>
        """, unsafe_allow_html=True)
        if status == "finished" and file_data:
            # Convertir a bytes si es memoryview
            if isinstance(file_data, memoryview):
                file_data = file_data.tobytes()
            st.download_button(
                label="📥 Descargar presentación",
                data=file_data,
                file_name=file_name or "presentacion.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        if status == "error" and error:
            st.error(f"Error: {error}")
    else:
        st.markdown("<div style='border:2px solid #800080; border-radius:12px; padding:1.2rem; margin:1.2rem 0; background:#f8f9fa;'><h4>Estado de la presentación</h4><div style='font-size:1.1rem; color:#800080; font-weight:bold;'>🟣 Sin registro</div></div>", unsafe_allow_html=True)
    # Botón para generar presentación solo si no está en proceso o ya finalizada
    if not status or status in ["error", "finished"]:
        if st.button("Reintentar generación", key=f"reintentar_presentacion_{id}_presentacion"):
            try:
                conn3, cur3 = get_conn_cursor()
                cur3.execute("SELECT id FROM presentation_queue WHERE proyecto_id=%s AND status IN ('queued','running')", (id,))
                existe = cur3.fetchone()
                if not existe:
                    cur3.execute("""
                        INSERT INTO presentation_queue (proyecto_id, status, tries, created_at)
                        VALUES (%s, 'queued', 0, CURRENT_TIMESTAMP)
                    """, (id,))
                    conn3.commit()
                cur3.close()
                conn3.close()
            except Exception as e:
                st.error(f"Error reintentando presentación: {e}")
                return
            st.info("Proyecto reintentado para generación de presentación.")
            st.rerun()

# --- Layout principal ---
def main():

    page = st.session_state.get("page", "inicio")
    # Solo mostrar navegación en inicio y formulario
    if page in ["inicio", "formulario", "form", "f"]:
        page = mostrar_navegacion("nav_main")
        if page in ["formulario", "form", "f"]:
            st.session_state["limpiar_formulario"] = True
            pagina_formulario()
        else:
            pagina_inicio()
    elif page == "editar":
        id = st.session_state.get("id", None)
        if id:
            pagina_editar(id)
    elif page == "eliminar":
        id = st.session_state.get("id", None)
        if id:
            pagina_eliminar(id)
    elif page == "reporte":
        id = st.session_state.get("id", None)
        if id:
            pagina_reporte(id)
    elif page == "datos_solicitud":
        id = st.session_state.get("id", None)
        if id:
            from forms.datos_solicitud import mostrar_formulario_datos_solicitud
            mostrar_formulario_datos_solicitud(id)
    elif page == "presentacion":
        id = st.session_state.get("id", None)
        if id:
            pagina_presentacion(id)

if __name__ == "__main__":
    main()