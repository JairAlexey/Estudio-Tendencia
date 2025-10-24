import streamlit as st
import pandas as pd
import time
from streamlit_option_menu import option_menu
from conexion import get_connection
import os

st.set_page_config(page_title="Formulario de Proyectos", page_icon=":bar_chart:", layout="centered")

# Helper para obtener conexión y cursor
def get_conn_cursor():
    conn = get_connection()
    return conn, conn.cursor()

# Improved CSS loading to prevent sidebar flash
def load_css():
    # First, direct CSS to immediately hide the sidebar
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
            height: 0px !important;
            visibility: hidden !important;
            position: absolute !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Then load the full CSS file
    css_file = os.path.join(os.path.dirname(__file__), ".streamlit", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load CSS at the very beginning
load_css()

# --- Navegación ---
def mostrar_navegacion(key):
    selected = option_menu(
        menu_title=None,
        options=["Proyectos", "Formulario", "Carpetas"],  # Agregado "Carpetas"
        icons=["house", "ui-checks", "folder"],  # Agregado ícono para carpetas
        menu_icon="cast",
        default_index=0 if st.session_state.get("page", "proyectos") == "proyectos" else (
            1 if st.session_state.get("page") == "formulario" else 2
        ),
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
        return "proyectos"
    if st.session_state.get("page", "proyectos") in ["proyectos", "formulario", "carpetas"]:
        st.session_state["page"] = selected.lower()
    return st.session_state["page"]


# --- Página de proyectos ---
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
            min-width: 100px;
            height: 32px;
            border-radius: 6px !important;
            font-weight: 500;
            font-size: 12px;
            margin: 0 4px;
            background-color: #f8f9fa !important;
            color: #222 !important;
            border: 1px solid #ddd !important;
            box-shadow: none !important;
            padding: 0 6px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #e9ecef !important;
            border-color: #adb5bd !important;
            transform: translateY(-1px);
        }
        div[data-testid="stButton"] button[data-testid="stBaseButton-secondary"] span.small-btn-label {
            font-size: 10px !important;
            font-weight: 400 !important;
            margin-top: -1px !important;
            color: #444 !important;
            letter-spacing: 0.1px;
        }
        /* Solo el botón Eliminar será rojo */
        div[data-testid="stColumn"]:nth-child(6) button[data-testid="stBaseButton-secondary"] {
            background-color: #ff0000 !important;
            color: #fff !important;
            border: 1px solid #ff0000 !important;
        }
        div[data-testid="stColumn"]:nth-child(6) button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #dc3545 !important;
            border-color: #dc3545 !important;
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

        col1, col2, col3, col4, col5, col6 = st.columns(6)
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
            st.button("🔍 Seguir", key=f"seguimiento_{id}", disabled=disabled, help="Seguimiento")
            if not disabled and st.session_state.get(f"seguimiento_{id}"):
                st.session_state["page"] = "seguimiento"
                st.session_state["id"] = id
                st.rerun()
        with col4:
            reporte_disabled = disabled or estado != "completed"
            st.button("📑 Tabla", key=f"reporte_{id}", disabled=reporte_disabled, help="Tabla")
            if not reporte_disabled and st.session_state.get(f"reporte_{id}"):
                st.session_state["page"] = "reporte"
                st.session_state["id"] = id
                st.rerun()
        with col5:
            st.button("📊 PPTX", key=f"presentacion_{id}", disabled=disabled, help="Reporte")
            if not disabled and st.session_state.get(f"presentacion_{id}"):
                st.session_state["page"] = "presentacion"
                st.session_state["id"] = id
                st.rerun()            
        with col6:
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
    if st.button("⬅️ Volver", key="volver_inicio_editar"):
        st.session_state["page"] = "proyectos"
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
            st.query_params.update({"page": "proyectos"})
            st.rerun()
        except Exception as e:
            st.error(f"Error eliminando proyecto: {e}")
            return

# --- Formulario ---
def pagina_formulario():
    # Clear form button state if it exists
    if f"volver_inicio_form_main" in st.session_state:
        del st.session_state[f"volver_inicio_form_main"]
        
    # Agregar botón de regreso fuera del formulario con clearer intent
    col1, col2 = st.columns([1, 5])
    with col1:
        # Limpiar los campos del formulario al entrar
        if st.session_state.get("limpiar_formulario", True):
            import pandas as pd
            st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
            st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
            st.session_state["search_query"] = ""
            st.session_state["limpiar_formulario"] = False
            # Limpiar mensaje de éxito al entrar en formulario
            if "mensaje_exito" in st.session_state:
                del st.session_state["mensaje_exito"]
            
    st.title("Formulario de Proyectos")
    
    # Verificar y mostrar mensaje de éxito guardado en session_state
    # (solo si viene de la acción de guardado, no al regresar al formulario)
    if "mensaje_exito" in st.session_state and st.session_state.get("mostrar_mensaje", False):
        st.success(st.session_state["mensaje_exito"])
        # Limpiar la bandera de mostrar después de mostrar el mensaje
        st.session_state["mostrar_mensaje"] = False
    
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
    if st.button("⬅️ Volver", key="volver_inicio_reporte"):
        st.session_state["page"] = "proyectos"
        st.rerun()
    
    from pages.tabla import mostrar_pagina_tabla
    mostrar_pagina_tabla(id)

def pagina_presentacion(id):
    if st.button("⬅️ Volver", key="volver_inicio_presentacion"):
        st.session_state["page"] = "proyectos"
        st.rerun()
    
    from pages.reporte import mostrar_pagina_presentacion
    mostrar_pagina_presentacion(id)

# --- Layout principal ---
def main():
    # Inicializar page si no existe
    if "page" not in st.session_state:
        st.session_state["page"] = "proyectos"
    
    # Check if the back button was pressed and handle it first
    for key in list(st.session_state.keys()):
        if (key.startswith("volver_inicio") or key.startswith("volver_datos_solicitud") or 
            key.startswith("volver_inicio_datos") or key.startswith("volver_inicio_seguimiento")) and st.session_state[key]:
            st.session_state["page"] = "proyectos"
            # Clear the button state to prevent loops
            st.session_state[key] = False
            st.rerun()
            break
            
    page = st.session_state.get("page", "proyectos")
    
    # Mostrar navegación en las páginas principales
    if page in ["proyectos", "formulario", "carpetas"]:
        page = mostrar_navegacion("nav_main")
        if page == "formulario":
            st.session_state["limpiar_formulario"] = True
            pagina_formulario()
        elif page == "carpetas":
            from pages.carpetas import mostrar_pagina_carpetas
            mostrar_pagina_carpetas()
        else:
            pagina_inicio()
    elif page == "editar":
        id = st.session_state.get("id", None)
        if id:
            pagina_editar(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()
    elif page == "eliminar":
        id = st.session_state.get("id", None)
        if id:
            pagina_eliminar(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()
    elif page == "reporte":
        id = st.session_state.get("id", None)
        if id:
            pagina_reporte(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()
    elif page == "seguimiento":
        id = st.session_state.get("id", None)
        if id:
            from pages.seguimiento import mostrar_pagina_seguimiento
            mostrar_pagina_seguimiento(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()
    elif page == "datos_solicitud":
        id = st.session_state.get("id", None)
        if id:
            from forms.datos_solicitud import mostrar_formulario_datos_solicitud
            mostrar_formulario_datos_solicitud(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()
    elif page == "presentacion":
        id = st.session_state.get("id", None)
        if id:
            pagina_presentacion(id)
        else:
            st.error("ID de proyecto no encontrado")
            st.session_state["page"] = "proyectos"
            st.rerun()

if __name__ == "__main__":
    main()