import streamlit as st
import sys
sys.path.append("..")
from conexion import get_connection
from components.loading import show_loading_spinner, loading_complete
import time

def mostrar_formulario_datos_solicitud(proyecto_id):
    # Clear button state if it exists
    if f"volver_datos_solicitud_{proyecto_id}" in st.session_state:
        del st.session_state[f"volver_datos_solicitud_{proyecto_id}"]

    # Use a consistent button style that works like in pagina_formulario
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Volver", key=f"volver_inicio_datos_{proyecto_id}", use_container_width=True):
            st.session_state["page"] = "proyectos"
            st.rerun()
    
    # Obtener la conexión a la base de datos
    conn = get_connection()

    # Obtener el nombre del proyecto
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT palabra_semrush FROM proyectos_tendencias WHERE id=%s", (proyecto_id,))
            row = cur.fetchone()
            nombre_proyecto = row[0] if row else "Proyecto desconocido"
            nombre_proyecto = " ".join([w.capitalize() for w in nombre_proyecto.split()])
    except Exception as e:
        st.error(f"Error obteniendo datos del proyecto: {e}")
        return

    # Consultar si ya existe registro previo
    try:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT facultad_propuesta, duracion, modalidad, nombre_proponente, facultad_proponente, cargo_proponente
                FROM datos_solicitud WHERE proyecto_id=%s
            ''', (proyecto_id,))
            datos_previos = cur.fetchone()
    except Exception as e:
        st.error(f"Error consultando datos previos: {e}")
        datos_previos = None

    st.markdown(
        f"""
        <div style='text-align:center; margin-top: 1.5rem; margin-bottom: 2rem;'>
            <h2 style='font-size:2.2rem; color:#C10230; margin-bottom:0.5rem;'>Datos de Solicitud</h2>
            <div style='font-size:1.3rem; color:#222;'>{nombre_proyecto}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
                # Show loading spinner
                spinner = show_loading_spinner("Guardando datos de solicitud...")
                
                try:
                    with conn.cursor() as cur:
                        # Eliminar registro anterior si existe
                        cur.execute('DELETE FROM datos_solicitud WHERE proyecto_id=%s', (proyecto_id,))
                        # Insertar nuevo registro
                        cur.execute('''
                            INSERT INTO datos_solicitud (
                                proyecto_id, nombre_programa, facultad_propuesta, duracion, modalidad,
                                nombre_proponente, facultad_proponente, cargo_proponente
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (proyecto_id, nombre_programa, facultad_propuesta, duracion, modalidad,
                             nombre_proponente, facultad_proponente, cargo_proponente))
                        conn.commit()
                    
                    # Show success message with the spinner
                    loading_complete(spinner, "¡Datos de solicitud guardados correctamente!")
                    
                except Exception as e:
                    spinner.empty()  # Remove spinner on error
                    conn.rollback()
                    st.error(f"Error al guardar datos de solicitud: {e}")
