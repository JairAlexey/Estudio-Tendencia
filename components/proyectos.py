import streamlit as st
from conexion import conn, cursor
import pandas as pd

def mostrar_proyectos():
    st.header("Proyectos registrados")
    with conn.cursor() as cur:
        cur.execute("SELECT id, nombre_proyecto, tipo_carpeta FROM proyectos_tendencias")
        proyectos = cur.fetchall()
    if not proyectos:
        st.info("No hay proyectos registrados.")
        return
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
