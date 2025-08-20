import streamlit as st
from conexion import conn, cursor
import pandas as pd

# --- Navegación ---
def set_page():
    query_params = st.query_params
    page = query_params.get("page", [""])[0]
    st.session_state["page"] = page

def navbar():
    st.sidebar.title("Navegación")
    page = st.sidebar.radio(
        "Ir a:",
        ["Inicio", "Formulario"],
        index=0 if st.session_state.get("page", "inicio") in ["", "inicio"] else 1
    )
    # Actualizar el parámetro de navegación
    if page == "Inicio":
        st.session_state["page"] = "inicio"
    elif page == "Formulario":
        st.session_state["page"] = "formulario"
    return st.session_state["page"]

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
            st.markdown(f"""
                <div style='border:1px solid #ddd; border-radius:8px; padding:1rem; margin-bottom:0.5rem; background:#fff;'>
                    <b>{nombre}</b> <br><span style='color:#888;'>{tipo}</span>
                </div>
            """, unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (label, page) in enumerate([("Visualizar", "ver"), ("Editar", "editar"), ("Eliminar", "eliminar")]):
                with cols[i]:
                        if label == "Eliminar":
                            if st.button(label, key=f"eliminar_index_{id}"):
                                with conn.cursor() as cur:
                                    # Eliminar primero los registros relacionados en todas las tablas hijas
                                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", (id,))
                                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", (id,))
                                    # Luego eliminar el proyecto principal
                                    cur.execute("DELETE FROM proyectos_tendencias WHERE id=?", (id,))
                                    conn.commit()
                                st.success("Proyecto y sus datos relacionados eliminados correctamente.")
                                st.rerun()
                        else:
                            if st.button(label, key=f"{page}_index_{id}"):
                                st.session_state["page"] = page
                                st.session_state["id"] = id
                                st.rerun()

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
    page = navbar()
    # Navegación principal
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

if __name__ == "__main__":
    main()
