import streamlit as st
from conexion import conn, cursor
import pandas as pd

# --- Navegación ---
def set_page():
    query_params = st.query_params
    page = query_params.get("page", [""])[0]
    st.session_state["page"] = page
    return page

def navbar():
    # Leer el parámetro 'page' directamente de la URL para reflejar el estado real
    import streamlit as st
    query_params = st.query_params
    page = query_params.get("page", [""])[0]
    st.session_state["page"] = page
    navbar_html = f'''
        <style>
        .navbar {{
            display: flex;
            gap: 2rem;
            background: #f5f5f5;
            padding: 0.7rem 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        .navbar a {{
            text-decoration: none;
            color: #333;
            font-weight: bold;
            padding: 0.5rem 1.2rem;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        .navbar a.active, .navbar a:hover {{
            background: #0068c9;
            color: #fff;
        }}
        </style>
        <div class="navbar">
            <a href="/" class="{'active' if page in ['', 'inicio'] else ''}">Inicio</a>
            <a href="/?page=formulario" class="{'active' if page in ['formulario', 'form', 'f'] else ''}">Formulario</a>
        </div>
    '''
    st.markdown(navbar_html, unsafe_allow_html=True)

# --- Página de inicio ---
def pagina_inicio():
    st.title("Proyectos en la Base de Datos")
    # Barra de búsqueda
    search_query = st.text_input("Buscar proyecto por nombre o tipo de carpeta")
    # Obtener proyectos
    with conn.cursor() as cur:
        cur.execute("SELECT id, carrera_referencia, tipo_carpeta FROM proyectos_tendencias")
        proyectos = cur.fetchall()
    if not proyectos:
        st.info("No hay proyectos registrados.")
        return
    # Filtrar proyectos por búsqueda
    if search_query:
        proyectos = [p for p in proyectos if search_query.lower() in p[1].lower() or search_query.lower() in p[2].lower()]
    for proyecto in proyectos:
        id, nombre, tipo = proyecto
        with st.container():
            st.markdown(f"<div style='border:1px solid #ddd; border-radius:8px; padding:1rem; margin-bottom:1rem; background:#fff;'>"
                        f"<b>{nombre}</b> <br><span style='color:#888;'>{tipo}</span>"
                        f"<br><br>"
                        f"<a href='/?page=ver&id={id}' style='margin-right:1rem;'>Visualizar</a>"
                        f"<a href='/?page=editar&id={id}' style='margin-right:1rem;'>Editar</a>"
                        f"<a href='/?page=eliminar&id={id}' style='color:red;'>Eliminar</a>"
                        f"</div>", unsafe_allow_html=True)

# --- Visualizar proyecto ---
def pagina_ver(id):
    st.title("Visualizar Proyecto")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM proyectos_tendencias WHERE id=?", id)
        proyecto = cur.fetchone()
    if not proyecto:
        st.error("Proyecto no encontrado.")
        return
    df = pd.DataFrame([proyecto], columns=[desc[0] for desc in cur.description])
    st.table(df)

# --- Editar proyecto ---
def pagina_editar(id):
    st.title("Editar Proyecto")
    st.info("Funcionalidad de edición pendiente de implementar.")


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
    navbar()
    page = set_page()
    # Navegación principal
    if page in ["formulario", "form", "f"]:
        pagina_formulario()
    elif page in ["", "inicio"]:
        pagina_inicio()
    elif page == "ver":
        id = st.query_params.get("id", [None])[0]
        if id:
            pagina_ver(id)
    elif page == "editar":
        id = st.query_params.get("id", [None])[0]
        if id:
            pagina_editar(id)
    elif page == "eliminar":
        id = st.query_params.get("id", [None])[0]
        if id:
            pagina_eliminar(id)

if __name__ == "__main__":
    main()
