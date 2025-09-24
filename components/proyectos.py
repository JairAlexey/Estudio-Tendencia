import streamlit as st
from conexion import conn, cursor
import pandas as pd

def mostrar_proyectos():
    st.header("Proyectos registrados")
    with conn.cursor() as cur:
        cur.execute("SELECT id, carrera_estudio, tipo_carpeta FROM proyectos_tendencias")
        proyectos = cur.fetchall()
    if not proyectos:
        st.info("No hay proyectos registrados.")
        return
    for proyecto in proyectos:
        id, nombre, tipo = proyecto
        with st.container():
            st.markdown(f"<div style='border:1px solid #ddd; border-radius:8px; padding:1rem; margin-bottom:1rem; background:#fff;'>"
                        f"<b>{nombre}</b> <br><span style='color:#888;'>{tipo}</span>"
                        f"</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            if cols[0].button("Visualizar", key=f"ver_{id}"):
                st.session_state["page"] = "ver"
                st.session_state["id"] = id
                st.rerun()
            if cols[1].button("Editar", key=f"editar_{id}"):
                st.session_state["page"] = "editar"
                st.session_state["id"] = id
                st.rerun()
            if cols[2].button("Eliminar", key=f"eliminar_{id}"):
                st.session_state["page"] = "eliminar"
                st.session_state["id"] = id
                st.rerun()
