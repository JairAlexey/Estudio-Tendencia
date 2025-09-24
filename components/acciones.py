import streamlit as st
from conexion import conn, cursor
import pandas as pd

def visualizar_proyecto(id):
    st.header("Visualizar Proyecto")
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM proyectos_tendencias WHERE id=%s", (id,))
        proyecto = cur.fetchone()
    if not proyecto:
        st.error("Proyecto no encontrado.")
        return
    df = pd.DataFrame([proyecto], columns=[desc[0] for desc in cur.description])
    st.table(df)

def editar_proyecto(id):
    st.header("Editar Proyecto")
    st.info("Funcionalidad de edición pendiente de implementar.")
    # Aquí podrías reutilizar el formulario y cargar los datos

def eliminar_proyecto(id):
    st.header("Eliminar Proyecto")
    with conn.cursor() as cur:
        cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=%s", (id,))
        proyecto = cur.fetchone()
    if not proyecto:
        st.error("Proyecto no encontrado.")
        return
    st.warning(f"¿Está seguro que desea eliminar el proyecto '{proyecto[0]}'?")
    if st.button("Eliminar definitivamente"):
        with conn.cursor() as cur:
            cur.execute("DELETE FROM proyectos_tendencias WHERE id=%s", (id,))
            conn.commit()
        st.success("Proyecto eliminado correctamente.")
        st.query_params.update({"page": "inicio"})
        st.rerun()
