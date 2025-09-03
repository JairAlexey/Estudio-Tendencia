import streamlit as st
import pandas as pd
import time
from streamlit_option_menu import option_menu
from conexion import conn, cursor

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
        st.query_params.clear()  # <-- reemplazo aquí
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
            min-width: 160px;
            height: 40px;
            border-radius: 10px !important;
            font-weight: 600;
            font-size: 15px;
            margin: 0 2px;
            background-color: #f8f9fa !important;
            color: #222 !important;
            border: 1px solid #ddd !important;
            box-shadow: none !important;
        }
        /* Solo el botón Eliminar será rojo */
        div[data-testid="stColumn"]:nth-child(4) button[data-testid="stBaseButton-secondary"] {
            background-color: #ff0000 !important;
            color: #fff !important;
            border: 1px solid #ff0000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    search_query = st.text_input("Buscar proyecto por nombre o tipo de carpeta", key="search_query", label_visibility="collapsed")
    
    with conn.cursor() as cur:
        cur.execute("SELECT id, carrera_estudio, tipo_carpeta FROM proyectos_tendencias")
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

    for proyecto in proyectos:
        id, nombre, tipo = proyecto
        # Línea negra de separación
        st.markdown("""
            <hr style='border: none; border-top: 3px solid #222; margin: 1.2rem 0 1.5rem 0;'>
        """, unsafe_allow_html=True)

        # Card estilo Material con estado traducido y color
        estado = estados.get(id, None)
        if estado in estado_traducido:
            texto, color, icono = estado_traducido[estado]
            estado_html = f"<span style='color:{color}; font-weight:bold;'>{icono} {texto}</span>"
        else:
            estado_html = "<span style='color:#222;'>—</span>"

        st.markdown(f"""
            <div style='
                border:1px solid #ddd; 
                border-radius:10px; 
                padding:1rem; 
                margin-bottom:0.5rem; 
                background:#f8f9fa;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
            '>
                <h4 style='margin:0'>{nombre}</h4>
                <p style='margin:0; color:#555;'>{tipo}</p>
                <div style='margin-top:0.25rem; font-size: 0.9rem;'>Estado: {estado_html}</div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        # Nuevo orden: Ver, Editar, Reporte, Eliminar
        disabled = st.session_state.get("botones_deshabilitados", False)
        with col1:
            st.button("Ver", key=f"ver_{id}", disabled=disabled)
            if not disabled and st.session_state.get(f"ver_{id}"):
                st.session_state["page"] = "ver"
                st.session_state["id"] = id
                st.rerun()
        with col2:
            st.button("Editar", key=f"editar_{id}", disabled=disabled)
            if not disabled and st.session_state.get(f"editar_{id}"):
                st.session_state["page"] = "editar"
                st.session_state["id"] = id
                st.rerun()
        with col3:
            reporte_disabled = disabled or estado != "completed"
            st.button("Reporte", key=f"reporte_{id}", disabled=reporte_disabled)
            if not reporte_disabled and st.session_state.get(f"reporte_{id}"):
                st.session_state["page"] = "reporte"
                st.session_state["id"] = id
                st.rerun()
        with col4:
            st.button("Eliminar", key=f"eliminar_{id}", disabled=disabled)
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
                    with conn.cursor() as cur:
                        # Eliminar de todas las tablas relacionadas
                        cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", (id,))
                        cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", (id,))
                        cur.execute("DELETE FROM linkedin WHERE proyecto_id=?", (id,))
                        cur.execute("DELETE FROM semrush WHERE proyecto_id=?", (id,))
                        cur.execute("DELETE FROM scraper_queue WHERE proyecto_id=?", (id,))
                        # Eliminar el proyecto principal
                        cur.execute("DELETE FROM proyectos_tendencias WHERE id=?", (id,))
                        conn.commit()
                    st.success("Proyecto eliminado correctamente")
                    st.session_state["mostrar_confirmacion_eliminar"] = False
                    st.rerun()
            elif cancelar:
                st.session_state["mostrar_confirmacion_eliminar"] = False
                st.session_state["confirmar_eliminar_id"] = None
                st.session_state["confirmar_eliminar_nombre"] = None
                st.session_state["confirmar_eliminar_tipo"] = None
                st.rerun()


# --- Visualizar proyecto ---
def pagina_ver(id):
    st.title("Visualizar Proyecto")
    if st.button("Regresar al inicio", key="volver_inicio_ver"):
        st.session_state["page"] = "inicio"
        st.rerun()
    with conn.cursor() as cur:
        # Datos principales del proyecto
        cur.execute("SELECT * FROM proyectos_tendencias WHERE id=?", (id,))
        proyecto = cur.fetchone()
        columns = [desc[0] for desc in cur.description]
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        st.subheader("Datos principales")
        for k, v in dict(zip(columns, proyecto)).items():
            st.markdown(f"- **{k.replace('_', ' ').capitalize()}**: {v}")

    # Usar un nuevo cursor para las siguientes consultas
    with conn.cursor() as cur2:
        # Tendencias asociadas
        cur2.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=?", (id,))
        tendencias = cur2.fetchall()
        st.subheader("Trends (palabras y promedios)")
        for item in tendencias:
            if len(item) == 2:
                st.markdown(f"- **{item[0]}**: {item[1]}")
            else:
                st.markdown(f"- {item[0]}")

        # Modalidad de oferta asociada
        cur2.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=?", (id,))
        modalidad = cur2.fetchall()
        st.subheader("Modalidad de Oferta")
        for item in modalidad:
            if len(item) == 2:
                st.markdown(f"- <b>Presencial:</b> {item[0]} &nbsp;&nbsp; <b>Virtual:</b> {item[1]}", unsafe_allow_html=True)
            else:
                st.markdown(f"- {item[0]}")

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
    with conn.cursor() as cur:
        cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=?", id)
        proyecto = cur.fetchone()
    if not proyecto:
        st.error("Proyecto no encontrado.")
        return
    st.warning(f"¿Está seguro que desea eliminar el proyecto '{proyecto[0]}'?")
    if st.button("Eliminar definitivamente"):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM proyectos_tendencias WHERE id=?", id)
            conn.commit()
        st.success("Proyecto eliminado correctamente.")
        st.query_params.update({"page": "inicio"})
        st.rerun()

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

# --- Visualizar proyecto ---
def pagina_reporte(id):
    st.title("Reporte del Proyecto")
    if st.button("Regresar al inicio", key="volver_inicio_reporte"):
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
        st.subheader("Evaluación")
        procesar_proyecto(id, nombre_pestana)
        # Mostrar rango de evaluación final
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
        st.dataframe(df_rango, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"ERROR mostrando reporte: {e}")

# --- Layout principal ---
def main():
    # Consultar mensaje global del sistema
    with conn.cursor() as cur:
        cur.execute("SELECT tipo, mensaje FROM sistema_estado WHERE id=1")
        row = cur.fetchone()
        if row and row[1]:
            st.error(row[1])
            if st.button("Limpiar mensaje de error y continuar", key="limpiar_mensaje_global"):
                with conn.cursor() as cur2:
                    cur2.execute("UPDATE sistema_estado SET tipo=NULL, mensaje=NULL, fecha_actualizacion=GETDATE() WHERE id=1")
                    conn.commit()
                st.rerun()
            st.stop()

    page = st.session_state.get("page", "inicio")
    # Solo mostrar navegación en inicio y formulario
    if page in ["inicio", "formulario", "form", "f"]:
        page = mostrar_navegacion("nav_main")
        if page in ["formulario", "form", "f"]:
            st.session_state["limpiar_formulario"] = True
            pagina_formulario()
        else:
            pagina_inicio()
    elif page == "ver":
        id = st.session_state.get("id", None)
        if id:
            pagina_ver(id)
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

if __name__ == "__main__":
    main()