import streamlit as st
import pandas as pd
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
    if st.session_state.get("page", "inicio") in ["inicio", "formulario", "form", "f"]:
        st.session_state["page"] = selected.lower()
    return st.session_state["page"]


# --- Página de inicio ---
def pagina_inicio():
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
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='red' class='bi bi-search' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85zm-5.442 1.398a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z'/%3E%3C/svg%3E");
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
            height: 40px;
            border-radius: 8px !important;
            font-weight: 600;
            font-size: 15px;
            margin: 0 2px;
        }
        /* Colores por columna */
        div[data-testid="stColumn"]:nth-child(1) button[data-testid="stBaseButton-secondary"] {
            background-color: #0d6efd !important;
            color: #fff !important;
        }
        div[data-testid="stColumn"]:nth-child(2) button[data-testid="stBaseButton-secondary"] {
            background-color: #ffc107 !important;
            color: #222 !important;
        }
        div[data-testid="stColumn"]:nth-child(3) button[data-testid="stBaseButton-secondary"] {
            background-color: #dc3545 !important;
            color: #fff !important;
        }
        div[data-testid="stColumn"]:nth-child(4) button[data-testid="stBaseButton-secondary"] {
            background-color: #198754 !important;
            color: #fff !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    search_query = st.text_input("Buscar proyecto por nombre o tipo de carpeta", key="search_query", label_visibility="collapsed")
    
    with conn.cursor() as cur:
        cur.execute("SELECT id, carrera_referencia, tipo_carpeta FROM proyectos_tendencias")
        proyectos = cur.fetchall()

    if not proyectos:
        st.info("No hay proyectos registrados.")
        return

    if search_query:
        proyectos = [p for p in proyectos if search_query.lower() in p[1].lower() or search_query.lower() in p[2].lower()]

    for proyecto in proyectos:
        id, nombre, tipo = proyecto

        # Card estilo Material
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
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        # Botones con color y tamaño uniforme
        with col1:
            if st.button("Ver", key=f"ver_{id}"):
                st.session_state["page"] = "ver"
                st.session_state["id"] = id
                st.rerun()
        with col2:
            if st.button("Editar", key=f"editar_{id}"):
                st.session_state["page"] = "editar"
                st.session_state["id"] = id
                st.rerun()
        with col3:
            if st.button("Eliminar", key=f"eliminar_{id}"):
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", (id,))
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", (id,))
                    cur.execute("DELETE FROM proyectos_tendencias WHERE id=?", (id,))
                    conn.commit()
                st.success("Proyecto eliminado correctamente")
                st.rerun()
        with col4:
            if st.button("Reporte", key=f"reporte_{id}"):
                st.session_state["page"] = "reporte"
                st.session_state["id"] = id
                st.rerun()

# --- Visualizar proyecto ---
def pagina_ver(id):
    st.title("Visualizar Proyecto")
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
        cur.execute("SELECT carrera_referencia FROM proyectos_tendencias WHERE id=?", id)
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

# --- Layout principal ---
def main():
    page = mostrar_navegacion("nav_main")
    if page in ["formulario", "form", "f"]:
        pagina_formulario()
    elif page in ["", "inicio"]:
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
            st.title("Reporte del Proyecto")
            st.info(f"Aquí puedes mostrar el reporte para el proyecto con ID {id}.")

if __name__ == "__main__":
    main()