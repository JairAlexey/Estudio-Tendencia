import streamlit as st
import sys
sys.path.append("..")
from conexion import conn

def mostrar_formulario_datos_solicitud(proyecto_id):
    # Obtener el nombre del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT carrera_estudio FROM proyectos_tendencias WHERE id=?", proyecto_id)
        row = cur.fetchone()
        nombre_proyecto = row[0] if row else "Proyecto desconocido"
        nombre_proyecto = " ".join([w.capitalize() for w in nombre_proyecto.split()])

    # Consultar si ya existe registro previo
    with conn.cursor() as cur:
        cur.execute('''
            SELECT facultad_propuesta, duracion, modalidad, nombre_proponente, facultad_proponente, cargo_proponente
            FROM datos_solicitud WHERE proyecto_id=?
        ''', proyecto_id)
        datos_previos = cur.fetchone()

    st.markdown(
        f"""
        <div style='text-align:center; margin-top: 1.5rem; margin-bottom: 2rem;'>
            <h2 style='font-size:2.2rem; color:#C10230; margin-bottom:0.5rem;'>Datos de Solicitud</h2>
            <div style='font-size:1.3rem; color:#222;'>{nombre_proyecto}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Regresar al inicio", key="volver_inicio_datos_solicitud"):
        st.session_state["page"] = "inicio"
        st.rerun()
    with st.form("form_datos_solicitud"):
        facultad_propuesta = st.text_input("Facultad propuesta", value=datos_previos[0] if datos_previos else "")
        duracion = st.text_input("Duración", value=datos_previos[1] if datos_previos else "")
        modalidad = st.text_input("Modalidad", value=datos_previos[2] if datos_previos else "")
        nombre_proponente = st.text_input("Nombre del proponente", value=datos_previos[3] if datos_previos else "")
        facultad_proponente = st.text_input("Facultad proponente", value=datos_previos[4] if datos_previos else "")
        cargo_proponente = st.text_input("Cargo proponente", value=datos_previos[5] if datos_previos else "")
        enviado = st.form_submit_button("Guardar solicitud")

        if enviado:
            errores = []
            nombre_programa = nombre_proyecto
            if not facultad_propuesta.strip():
                errores.append("El campo 'Facultad propuesta' es obligatorio.")
            if not duracion.strip():
                errores.append("El campo 'Duración' es obligatorio.")
            if not modalidad.strip():
                errores.append("El campo 'Modalidad' es obligatorio.")
            if not nombre_proponente.strip():
                errores.append("El campo 'Nombre del proponente' es obligatorio.")
            if not facultad_proponente.strip():
                errores.append("El campo 'Facultad proponente' es obligatorio.")
            if not cargo_proponente.strip():
                errores.append("El campo 'Cargo proponente' es obligatorio.")
            if errores:
                for err in errores:
                    st.warning(err)
            else:
                try:
                    with conn.cursor() as cur:
                        # Eliminar registro anterior si existe
                        cur.execute('DELETE FROM datos_solicitud WHERE proyecto_id=?', proyecto_id)
                        # Insertar nuevo registro
                        cur.execute('''
                            INSERT INTO datos_solicitud (
                                proyecto_id, nombre_programa, facultad_propuesta, duracion, modalidad,
                                nombre_proponente, facultad_proponente, cargo_proponente
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', proyecto_id, nombre_programa, facultad_propuesta, duracion, modalidad,
                             nombre_proponente, facultad_proponente, cargo_proponente)
                        conn.commit()
                    st.success("Datos de solicitud guardados correctamente.")
                except Exception as e:
                    st.error(f"Error al guardar datos de solicitud: {e}")
