# --- Formulario de edición de proyecto ---
def mostrar_formulario_edicion(id):
    st.title("Editar Proyecto y Tendencias")
    # Obtener datos actuales del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin FROM proyectos_tendencias WHERE id=?", id)
        proyecto = cur.fetchone()
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto

    # Tendencias
    with conn.cursor() as cur:
        cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=?", id)
        tendencias = cur.fetchall()

    # Modalidad de oferta
    with conn.cursor() as cur:
        cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=?", id)
        modalidad = cur.fetchall()

    # --- Formulario ---
    tipo_carpeta = st.selectbox("Tipo de carpeta", ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"], index=0 if "POSGRADOS" in tipo_carpeta else 1)
    # Carrera referencia
    tipo_carpeta_lower = tipo_carpeta.lower()
    carreras_filtradas = []
    if "pregrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
    elif "posgrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
    if carreras_filtradas:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", carreras_filtradas, index=carreras_filtradas.index(carrera_referencia) if carrera_referencia in carreras_filtradas else 0)
    else:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", [carrera_referencia])
    # --- Carrera linkedin ---
    agregar_carrera_linkedin = st.button("Agregar carrera linkedin", key=f"btn_agregar_carrera_linkedin_{id}")
    if f"mostrar_campo_linkedin_{id}" not in st.session_state:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = False
    if agregar_carrera_linkedin:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = True
    if st.session_state[f"mostrar_campo_linkedin_{id}"]:
        carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin", value=carrera_linkedin or "")
    else:
        carrera_linkedin_input = nombre_proyecto_1
    # Carrera estudio
    nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio", value=carrera_estudio)
    # SEMRUSH
    palabra_semrush = st.text_input("Palabra clave", value=palabra_semrush)
    # Trends
    st.subheader("Trends (palabras y promedios)")
    try:
        tendencias_limpias = [list(row) for row in tendencias]
        if tendencias_limpias and all(len(row) == 2 for row in tendencias_limpias):
            df_trends = pd.DataFrame(tendencias_limpias, columns=["Palabra", "Promedio"])
        elif tendencias_limpias and all(len(row) == 1 for row in tendencias_limpias):
            st.warning("Advertencia: Las tendencias tienen solo una columna. Se mostrará solo 'Palabra'.")
            df_trends = pd.DataFrame([(row[0], "") for row in tendencias_limpias], columns=["Palabra", "Promedio"])
        else:
            df_trends = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(df_trends, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"trends_editor_{id}")
    except Exception as e:
        st.error(f"ERROR al crear DataFrame de tendencias: {e}")
    # Código CIIU
    codigos_ciiu = obtener_codigos_ciiu()
    codigo_ciiu = st.selectbox("Seleccione el código CIIU", codigos_ciiu, index=codigos_ciiu.index(codigo_ciiu) if codigo_ciiu in codigos_ciiu else 0)
    # Modalidad de oferta
    st.subheader("Modalidad de Oferta")
    modalidad_limpia = [list(row) for row in modalidad]
    if modalidad_limpia and all(len(row) == 2 for row in modalidad_limpia):
        df_modalidad = pd.DataFrame(modalidad_limpia, columns=["Presencial", "Virtual"])
    elif modalidad_limpia and all(len(row) == 1 for row in modalidad_limpia):
        st.warning("Advertencia: Modalidad tiene solo una columna. Se mostrará solo 'Presencial'.")
        df_modalidad = pd.DataFrame([(row[0], "") for row in modalidad_limpia], columns=["Presencial", "Virtual"])
    else:
        df_modalidad = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
    df_modalidad = st.data_editor(df_modalidad, num_rows="fixed", use_container_width=True, hide_index=True, key=f"modalidad_oferta_editor_{id}")
    # Botón de guardar cambios
    guardado = st.button("Guardar cambios")
    if guardado:
        errores = []
        if not nombre_proyecto_1:
            errores.append("El campo 'Carrera Referencia' es obligatorio.")
        if not nombre_proyecto_2.strip():
            errores.append("El campo 'Carrera Estudio' es obligatorio.")
        if not palabra_semrush.strip():
            errores.append("El campo 'Palabra clave' es obligatorio.")
        if not codigo_ciiu:
            errores.append("El campo 'Código CIIU' es obligatorio.")
        trends_validas = [
            row for row in df_trends.to_dict("records")
            if str(row.get("Palabra", "")).strip() and str(row.get("Promedio", "")).strip()
        ]
        if not trends_validas:
            errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
        modalidad_valida = False
        if df_modalidad.shape[0] > 0:
            presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
            virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
            modalidad_valida = presencial and virtual
        if not modalidad_valida:
            errores.append("Debe ingresar modalidad presencial y virtual.")
        if errores:
            for err in errores:
                st.warning(err)
        else:
            try:
                # Actualizar proyecto principal
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE proyectos_tendencias SET
                            tipo_carpeta=?, carrera_referencia=?, carrera_estudio=?, palabra_semrush=?, codigo_ciiu=?, carrera_linkedin=?
                        WHERE id=?
                    ''', tipo_carpeta, nombre_proyecto_1, nombre_proyecto_2, palabra_semrush, codigo_ciiu, carrera_linkedin_input, id)

                # Eliminar tendencias
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", id)

                # Insertar tendencias
                for row in df_trends.to_dict("records"):
                    palabra = row.get("Palabra", "")
                    promedio = row.get("Promedio", None)
                    if palabra:
                        try:
                            promedio_float = float(promedio)
                        except:
                            promedio_float = None
                        with conn.cursor() as cur:
                            cur.execute('''
                                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                VALUES (?, ?, ?)
                            ''', id, palabra, promedio_float)

                # Eliminar modalidad de oferta
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", id)

                # Insertar modalidad de oferta
                if df_modalidad.shape[0] > 0:
                    presencial = df_modalidad.iloc[0].get("Presencial", "")
                    virtual = df_modalidad.iloc[0].get("Virtual", "")
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                            VALUES (?, ?, ?)
                        ''', id, presencial, virtual)

                conn.commit()
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    enqueue_scraper_job(id)
                    st.info("Scraper encolado para este proyecto.")
                except Exception as e:
                    st.warning(f"No se pudo encolar el scraper: {e}")
                st.success("Cambios guardados correctamente.")
            except Exception as e:
                st.error(f"Error al guardar cambios: {e}")

# VISTA DEL FORMUALRIO 
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
sys.path.append("../..")
from codigos import obtener_codigos_ciiu
import re
import pandas as pd

# --- Función para obtener carreras desde la base de datos ---
def obtener_carreras_por_nivel(nivel):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Carrera FROM carreras_facultad WHERE Nivel = ?", nivel)
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        st.error(f"Error al consultar carreras: {e}")
        return []

def mostrar_formulario():
    # Tipo de carpeta fuera del formulario para actualización en tiempo real

    tipo_carpeta = st.selectbox("Tipo de carpeta", ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])

    with st.form("form_proyectos"):
        # --- Proyecto 1: Carrera Referencia ---
        st.subheader("Carrera Referencia")

        tipo_carpeta_lower = tipo_carpeta.lower()
        carreras_filtradas = []
        if tipo_carpeta != "Seleccione un tipo...":
            if "pregrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
            elif "posgrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
        if carreras_filtradas:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."])

        # --- Carrera linkedin ---
        agregar_carrera_linkedin = st.form_submit_button("Agregar carrera linkedin")
        if "mostrar_campo_linkedin" not in st.session_state:
            st.session_state["mostrar_campo_linkedin"] = False
        if agregar_carrera_linkedin:
            st.session_state["mostrar_campo_linkedin"] = True
        if st.session_state["mostrar_campo_linkedin"]:
            carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin")
        else:
            carrera_linkedin_input = nombre_proyecto_1 if nombre_proyecto_1 != "Seleccione una carrera..." else ""

        # --- Proyecto 2: Carrera Estudio ---
        st.subheader("Carrera Estudio")
        nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio")

        # --- SEMRUSH ---
        st.subheader("Palabra a consultar en SEMRUSH")
        palabra_semrush = st.text_input("Palabra clave")

        # --- Trends ---
        st.subheader("Trends (palabras y promedios)")
        if "df_trends" not in st.session_state:
            st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(
            st.session_state["df_trends"],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="trends_editor"
        )
        st.session_state["df_trends"] = df_trends

        # --- Código CIIU ---
        st.subheader("Código CIIU")
        codigos_ciiu = obtener_codigos_ciiu()
        codigo_ciiu = st.selectbox("Seleccione el código CIIU", ["Seleccione un código..."] + codigos_ciiu)

        # --- Modalidad de Oferta ---
        st.subheader("Modalidad de Oferta")
        if "modalidad_oferta" not in st.session_state:
            st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
        df_modalidad = st.data_editor(
            st.session_state["modalidad_oferta"],
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            key="modalidad_oferta_editor"
        )
        st.session_state["modalidad_oferta"] = df_modalidad

        # Botón de envío
        enviado = st.form_submit_button("Enviar formulario")

        if enviado:
            # Validaciones de campos requeridos
            errores = []
            if tipo_carpeta == "Seleccione un tipo...":
                errores.append("El campo 'Tipo de carpeta' es obligatorio.")
            if nombre_proyecto_1 == "Seleccione una carrera..." or not nombre_proyecto_1:
                errores.append("El campo 'Carrera Referencia' es obligatorio.")
            if not nombre_proyecto_2.strip():
                errores.append("El campo 'Carrera Estudio' es obligatorio.")
            if not palabra_semrush.strip():
                errores.append("El campo 'Palabra clave' es obligatorio.")
            if codigo_ciiu == "Seleccione un código...":
                errores.append("El campo 'Código CIIU' es obligatorio.")
            # Validar tendencias
            trends_validas = [row for row in df_trends.to_dict("records") if row.get("Palabra", "").strip() and row.get("Promedio", "").strip()]
            if not trends_validas:
                errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
            # Validar modalidad de oferta
            modalidad_valida = False
            if df_modalidad.shape[0] > 0:
                presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
                virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
                modalidad_valida = presencial and virtual
            if not modalidad_valida:
                errores.append("Debe ingresar modalidad presencial y virtual.")

            if errores:
                for err in errores:
                    st.warning(err)
            else:
                # Guardar en la base de datos
                try:
                    # Usar un cursor exclusivo para la transacción
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO proyectos_tendencias (
                                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin
                            ) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                            tipo_carpeta,
                            nombre_proyecto_1,
                            nombre_proyecto_2,
                            palabra_semrush,
                            codigo_ciiu,
                            carrera_linkedin_input
                        )
                        proyecto_id_row = cur.fetchone()
                        if proyecto_id_row is None or proyecto_id_row[0] is None:
                            raise Exception("No se pudo obtener el ID del proyecto insertado.")
                        proyecto_id = int(proyecto_id_row[0])

                        # Insertar tendencias
                        for row in df_trends.to_dict("records"):
                            palabra = row.get("Palabra", "")
                            promedio = row.get("Promedio", None)
                            if palabra:
                                try:
                                    promedio_float = float(promedio)
                                except:
                                    promedio_float = None
                                # Guardar como valores nativos, no como string
                                cur.execute('''
                                    INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                    VALUES (?, ?, ?)
                                ''', proyecto_id, palabra, promedio_float)

                        # Insertar modalidad de oferta (solo una fila)
                        if df_modalidad.shape[0] > 0:
                            presencial = df_modalidad.iloc[0].get("Presencial", "")
                            virtual = df_modalidad.iloc[0].get("Virtual", "")
                            # Guardar como valores nativos, no como string
                            cur.execute('''
                                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                                VALUES (?, ?, ?)
                            ''', proyecto_id, presencial, virtual)

                        conn.commit()
                    # Encolar job para el nuevo proyecto
                    try:
                        from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                        enqueue_scraper_job(proyecto_id)
                        st.info("Scraper encolado para el nuevo proyecto.")
                    except Exception as e:
                        st.warning(f"No se pudo encolar el scraper: {e}")
                    # Guardar bandera de éxito y limpiar datos
                    st.session_state["exito_guardado"] = True
                    st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
                    st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
                    st.session_state["search_query"] = ""
                    st.session_state["page"] = "inicio"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en la base de datos: {e}")

def mostrar_formulario_edicion(id):
    st.title("Editar Proyecto y Tendencias")
    # Obtener datos actuales del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin FROM proyectos_tendencias WHERE id=?", id)
        proyecto = cur.fetchone()
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto

    # Tendencias
    with conn.cursor() as cur:
        cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=?", id)
        tendencias = cur.fetchall()

    # Modalidad de oferta
    with conn.cursor() as cur:
        cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=?", id)
        modalidad = cur.fetchall()

    # --- Formulario ---
    tipo_carpeta = st.selectbox("Tipo de carpeta", ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"], index=0 if "POSGRADOS" in tipo_carpeta else 1)
    # Carrera referencia
    tipo_carpeta_lower = tipo_carpeta.lower()
    carreras_filtradas = []
    if "pregrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
    elif "posgrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
    if carreras_filtradas:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", carreras_filtradas, index=carreras_filtradas.index(carrera_referencia) if carrera_referencia in carreras_filtradas else 0)
    else:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", [carrera_referencia])
    # --- Carrera linkedin ---
    agregar_carrera_linkedin = st.button("Agregar carrera linkedin", key=f"btn_agregar_carrera_linkedin_{id}")
    if f"mostrar_campo_linkedin_{id}" not in st.session_state:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = False
    if agregar_carrera_linkedin:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = True
    if st.session_state[f"mostrar_campo_linkedin_{id}"]:
        carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin", value=carrera_linkedin or "")
    else:
        carrera_linkedin_input = nombre_proyecto_1
    # Carrera estudio
    nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio", value=carrera_estudio)
    # SEMRUSH
    palabra_semrush = st.text_input("Palabra clave", value=palabra_semrush)
    # Trends
    st.subheader("Trends (palabras y promedios)")
    try:
        tendencias_limpias = [list(row) for row in tendencias]
        if tendencias_limpias and all(len(row) == 2 for row in tendencias_limpias):
            df_trends = pd.DataFrame(tendencias_limpias, columns=["Palabra", "Promedio"])
        elif tendencias_limpias and all(len(row) == 1 for row in tendencias_limpias):
            st.warning("Advertencia: Las tendencias tienen solo una columna. Se mostrará solo 'Palabra'.")
            df_trends = pd.DataFrame([(row[0], "") for row in tendencias_limpias], columns=["Palabra", "Promedio"])
        else:
            df_trends = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(df_trends, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"trends_editor_{id}")
    except Exception as e:
        st.error(f"ERROR al crear DataFrame de tendencias: {e}")
    # Código CIIU
    codigos_ciiu = obtener_codigos_ciiu()
    codigo_ciiu = st.selectbox("Seleccione el código CIIU", codigos_ciiu, index=codigos_ciiu.index(codigo_ciiu) if codigo_ciiu in codigos_ciiu else 0)
    # Modalidad de oferta
    st.subheader("Modalidad de Oferta")
    modalidad_limpia = [list(row) for row in modalidad]
    if modalidad_limpia and all(len(row) == 2 for row in modalidad_limpia):
        df_modalidad = pd.DataFrame(modalidad_limpia, columns=["Presencial", "Virtual"])
    elif modalidad_limpia and all(len(row) == 1 for row in modalidad_limpia):
        st.warning("Advertencia: Modalidad tiene solo una columna. Se mostrará solo 'Presencial'.")
        df_modalidad = pd.DataFrame([(row[0], "") for row in modalidad_limpia], columns=["Presencial", "Virtual"])
    else:
        df_modalidad = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
    df_modalidad = st.data_editor(df_modalidad, num_rows="fixed", use_container_width=True, hide_index=True, key=f"modalidad_oferta_editor_{id}")
    # Botón de guardar cambios
    guardado = st.button("Guardar cambios")
    if guardado:
        errores = []
        if not nombre_proyecto_1:
            errores.append("El campo 'Carrera Referencia' es obligatorio.")
        if not nombre_proyecto_2.strip():
            errores.append("El campo 'Carrera Estudio' es obligatorio.")
        if not palabra_semrush.strip():
            errores.append("El campo 'Palabra clave' es obligatorio.")
        if not codigo_ciiu:
            errores.append("El campo 'Código CIIU' es obligatorio.")
        trends_validas = [
            row for row in df_trends.to_dict("records")
            if str(row.get("Palabra", "")).strip() and str(row.get("Promedio", "")).strip()
        ]
        if not trends_validas:
            errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
        modalidad_valida = False
        if df_modalidad.shape[0] > 0:
            presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
            virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
            modalidad_valida = presencial and virtual
        if not modalidad_valida:
            errores.append("Debe ingresar modalidad presencial y virtual.")
        if errores:
            for err in errores:
                st.warning(err)
        else:
            try:
                # Actualizar proyecto principal
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE proyectos_tendencias SET
                            tipo_carpeta=?, carrera_referencia=?, carrera_estudio=?, palabra_semrush=?, codigo_ciiu=?, carrera_linkedin=?
                        WHERE id=?
                    ''', tipo_carpeta, nombre_proyecto_1, nombre_proyecto_2, palabra_semrush, codigo_ciiu, carrera_linkedin_input, id)

                # Eliminar tendencias
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", id)

                # Insertar tendencias
                for row in df_trends.to_dict("records"):
                    palabra = row.get("Palabra", "")
                    promedio = row.get("Promedio", None)
                    if palabra:
                        try:
                            promedio_float = float(promedio)
                        except:
                            promedio_float = None
                        with conn.cursor() as cur:
                            cur.execute('''
                                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                VALUES (?, ?, ?)
                            ''', id, palabra, promedio_float)

                # Eliminar modalidad de oferta
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", id)

                # Insertar modalidad de oferta
                if df_modalidad.shape[0] > 0:
                    presencial = df_modalidad.iloc[0].get("Presencial", "")
                    virtual = df_modalidad.iloc[0].get("Virtual", "")
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                            VALUES (?, ?, ?)
                        ''', id, presencial, virtual)

                conn.commit()
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    enqueue_scraper_job(id)
                    st.info("Scraper encolado para este proyecto.")
                except Exception as e:
                    st.warning(f"No se pudo encolar el scraper: {e}")
                st.success("Cambios guardados correctamente.")
            except Exception as e:
                st.error(f"Error al guardar cambios: {e}")

# VISTA DEL FORMUALRIO 
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
sys.path.append("../..")
from codigos import obtener_codigos_ciiu
import re
import pandas as pd

# --- Función para obtener carreras desde la base de datos ---
def obtener_carreras_por_nivel(nivel):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Carrera FROM carreras_facultad WHERE Nivel = ?", nivel)
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        st.error(f"Error al consultar carreras: {e}")
        return []

def mostrar_formulario():
    # Tipo de carpeta fuera del formulario para actualización en tiempo real

    tipo_carpeta = st.selectbox("Tipo de carpeta", ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])

    with st.form("form_proyectos"):
        # --- Proyecto 1: Carrera Referencia ---
        st.subheader("Carrera Referencia")

        tipo_carpeta_lower = tipo_carpeta.lower()
        carreras_filtradas = []
        if tipo_carpeta != "Seleccione un tipo...":
            if "pregrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
            elif "posgrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
        if carreras_filtradas:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."])

        # --- Carrera linkedin ---
        agregar_carrera_linkedin = st.form_submit_button("Agregar carrera linkedin")
        if "mostrar_campo_linkedin" not in st.session_state:
            st.session_state["mostrar_campo_linkedin"] = False
        if agregar_carrera_linkedin:
            st.session_state["mostrar_campo_linkedin"] = True
        if st.session_state["mostrar_campo_linkedin"]:
            carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin")
        else:
            carrera_linkedin_input = nombre_proyecto_1 if nombre_proyecto_1 != "Seleccione una carrera..." else ""

        # --- Proyecto 2: Carrera Estudio ---
        st.subheader("Carrera Estudio")
        nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio")

        # --- SEMRUSH ---
        st.subheader("Palabra a consultar en SEMRUSH")
        palabra_semrush = st.text_input("Palabra clave")

        # --- Trends ---
        st.subheader("Trends (palabras y promedios)")
        if "df_trends" not in st.session_state:
            st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(
            st.session_state["df_trends"],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="trends_editor"
        )
        st.session_state["df_trends"] = df_trends

        # --- Código CIIU ---
        st.subheader("Código CIIU")
        codigos_ciiu = obtener_codigos_ciiu()
        codigo_ciiu = st.selectbox("Seleccione el código CIIU", ["Seleccione un código..."] + codigos_ciiu)

        # --- Modalidad de Oferta ---
        st.subheader("Modalidad de Oferta")
        if "modalidad_oferta" not in st.session_state:
            st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
        df_modalidad = st.data_editor(
            st.session_state["modalidad_oferta"],
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            key="modalidad_oferta_editor"
        )
        st.session_state["modalidad_oferta"] = df_modalidad

        # Botón de envío
        enviado = st.form_submit_button("Enviar formulario")

        if enviado:
            # Validaciones de campos requeridos
            errores = []
            if tipo_carpeta == "Seleccione un tipo...":
                errores.append("El campo 'Tipo de carpeta' es obligatorio.")
            if nombre_proyecto_1 == "Seleccione una carrera..." or not nombre_proyecto_1:
                errores.append("El campo 'Carrera Referencia' es obligatorio.")
            if not nombre_proyecto_2.strip():
                errores.append("El campo 'Carrera Estudio' es obligatorio.")
            if not palabra_semrush.strip():
                errores.append("El campo 'Palabra clave' es obligatorio.")
            if codigo_ciiu == "Seleccione un código...":
                errores.append("El campo 'Código CIIU' es obligatorio.")
            # Validar tendencias
            trends_validas = [row for row in df_trends.to_dict("records") if row.get("Palabra", "").strip() and row.get("Promedio", "").strip()]
            if not trends_validas:
                errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
            # Validar modalidad de oferta
            modalidad_valida = False
            if df_modalidad.shape[0] > 0:
                presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
                virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
                modalidad_valida = presencial and virtual
            if not modalidad_valida:
                errores.append("Debe ingresar modalidad presencial y virtual.")

            if errores:
                for err in errores:
                    st.warning(err)
            else:
                # Guardar en la base de datos
                try:
                    # Usar un cursor exclusivo para la transacción
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO proyectos_tendencias (
                                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin
                            ) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                            tipo_carpeta,
                            nombre_proyecto_1,
                            nombre_proyecto_2,
                            palabra_semrush,
                            codigo_ciiu,
                            carrera_linkedin_input
                        )
                        proyecto_id_row = cur.fetchone()
                        if proyecto_id_row is None or proyecto_id_row[0] is None:
                            raise Exception("No se pudo obtener el ID del proyecto insertado.")
                        proyecto_id = int(proyecto_id_row[0])

                        # Insertar tendencias
                        for row in df_trends.to_dict("records"):
                            palabra = row.get("Palabra", "")
                            promedio = row.get("Promedio", None)
                            if palabra:
                                try:
                                    promedio_float = float(promedio)
                                except:
                                    promedio_float = None
                                # Guardar como valores nativos, no como string
                                cur.execute('''
                                    INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                    VALUES (?, ?, ?)
                                ''', proyecto_id, palabra, promedio_float)

                        # Insertar modalidad de oferta (solo una fila)
                        if df_modalidad.shape[0] > 0:
                            presencial = df_modalidad.iloc[0].get("Presencial", "")
                            virtual = df_modalidad.iloc[0].get("Virtual", "")
                            # Guardar como valores nativos, no como string
                            cur.execute('''
                                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                                VALUES (?, ?, ?)
                            ''', proyecto_id, presencial, virtual)

                        conn.commit()
                    # Encolar job para el nuevo proyecto
                    try:
                        from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                        enqueue_scraper_job(proyecto_id)
                        st.info("Scraper encolado para el nuevo proyecto.")
                    except Exception as e:
                        st.warning(f"No se pudo encolar el scraper: {e}")
                    # Guardar bandera de éxito y limpiar datos
                    st.session_state["exito_guardado"] = True
                    st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
                    st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
                    st.session_state["search_query"] = ""
                    st.session_state["page"] = "inicio"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en la base de datos: {e}")

def mostrar_formulario_edicion(id):
    st.title("Editar Proyecto y Tendencias")
    # Obtener datos actuales del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin FROM proyectos_tendencias WHERE id=?", id)
        proyecto = cur.fetchone()
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto

    # Tendencias
    with conn.cursor() as cur:
        cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=?", id)
        tendencias = cur.fetchall()

    # Modalidad de oferta
    with conn.cursor() as cur:
        cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=?", id)
        modalidad = cur.fetchall()

    # --- Formulario ---
    tipo_carpeta = st.selectbox("Tipo de carpeta", ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"], index=0 if "POSGRADOS" in tipo_carpeta else 1)
    # Carrera referencia
    tipo_carpeta_lower = tipo_carpeta.lower()
    carreras_filtradas = []
    if "pregrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
    elif "posgrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
    if carreras_filtradas:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", carreras_filtradas, index=carreras_filtradas.index(carrera_referencia) if carrera_referencia in carreras_filtradas else 0)
    else:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", [carrera_referencia])
    # --- Carrera linkedin ---
    agregar_carrera_linkedin = st.button("Agregar carrera linkedin", key=f"btn_agregar_carrera_linkedin_{id}")
    if f"mostrar_campo_linkedin_{id}" not in st.session_state:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = False
    if agregar_carrera_linkedin:
        st.session_state[f"mostrar_campo_linkedin_{id}"] = True
    if st.session_state[f"mostrar_campo_linkedin_{id}"]:
        carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin", value=carrera_linkedin or "")
    else:
        carrera_linkedin_input = nombre_proyecto_1
    # Carrera estudio
    nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio", value=carrera_estudio)
    # SEMRUSH
    palabra_semrush = st.text_input("Palabra clave", value=palabra_semrush)
    # Trends
    st.subheader("Trends (palabras y promedios)")
    try:
        tendencias_limpias = [list(row) for row in tendencias]
        if tendencias_limpias and all(len(row) == 2 for row in tendencias_limpias):
            df_trends = pd.DataFrame(tendencias_limpias, columns=["Palabra", "Promedio"])
        elif tendencias_limpias and all(len(row) == 1 for row in tendencias_limpias):
            st.warning("Advertencia: Las tendencias tienen solo una columna. Se mostrará solo 'Palabra'.")
            df_trends = pd.DataFrame([(row[0], "") for row in tendencias_limpias], columns=["Palabra", "Promedio"])
        else:
            df_trends = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(df_trends, num_rows="dynamic", use_container_width=True, hide_index=True, key=f"trends_editor_{id}")
    except Exception as e:
        st.error(f"ERROR al crear DataFrame de tendencias: {e}")
    # Código CIIU
    codigos_ciiu = obtener_codigos_ciiu()
    codigo_ciiu = st.selectbox("Seleccione el código CIIU", codigos_ciiu, index=codigos_ciiu.index(codigo_ciiu) if codigo_ciiu in codigos_ciiu else 0)
    # Modalidad de oferta
    st.subheader("Modalidad de Oferta")
    modalidad_limpia = [list(row) for row in modalidad]
    if modalidad_limpia and all(len(row) == 2 for row in modalidad_limpia):
        df_modalidad = pd.DataFrame(modalidad_limpia, columns=["Presencial", "Virtual"])
    elif modalidad_limpia and all(len(row) == 1 for row in modalidad_limpia):
        st.warning("Advertencia: Modalidad tiene solo una columna. Se mostrará solo 'Presencial'.")
        df_modalidad = pd.DataFrame([(row[0], "") for row in modalidad_limpia], columns=["Presencial", "Virtual"])
    else:
        df_modalidad = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
    df_modalidad = st.data_editor(df_modalidad, num_rows="fixed", use_container_width=True, hide_index=True, key=f"modalidad_oferta_editor_{id}")
    # Botón de guardar cambios
    guardado = st.button("Guardar cambios")
    if guardado:
        errores = []
        if not nombre_proyecto_1:
            errores.append("El campo 'Carrera Referencia' es obligatorio.")
        if not nombre_proyecto_2.strip():
            errores.append("El campo 'Carrera Estudio' es obligatorio.")
        if not palabra_semrush.strip():
            errores.append("El campo 'Palabra clave' es obligatorio.")
        if not codigo_ciiu:
            errores.append("El campo 'Código CIIU' es obligatorio.")
        trends_validas = [
            row for row in df_trends.to_dict("records")
            if str(row.get("Palabra", "")).strip() and str(row.get("Promedio", "")).strip()
        ]
        if not trends_validas:
            errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
        modalidad_valida = False
        if df_modalidad.shape[0] > 0:
            presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
            virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
            modalidad_valida = presencial and virtual
        if not modalidad_valida:
            errores.append("Debe ingresar modalidad presencial y virtual.")
        if errores:
            for err in errores:
                st.warning(err)
        else:
            try:
                # Actualizar proyecto principal
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE proyectos_tendencias SET
                            tipo_carpeta=?, carrera_referencia=?, carrera_estudio=?, palabra_semrush=?, codigo_ciiu=?, carrera_linkedin=?
                        WHERE id=?
                    ''', tipo_carpeta, nombre_proyecto_1, nombre_proyecto_2, palabra_semrush, codigo_ciiu, carrera_linkedin_input, id)

                # Eliminar tendencias
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=?", id)

                # Insertar tendencias
                for row in df_trends.to_dict("records"):
                    palabra = row.get("Palabra", "")
                    promedio = row.get("Promedio", None)
                    if palabra:
                        try:
                            promedio_float = float(promedio)
                        except:
                            promedio_float = None
                        with conn.cursor() as cur:
                            cur.execute('''
                                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                VALUES (?, ?, ?)
                            ''', id, palabra, promedio_float)

                # Eliminar modalidad de oferta
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=?", id)

                # Insertar modalidad de oferta
                if df_modalidad.shape[0] > 0:
                    presencial = df_modalidad.iloc[0].get("Presencial", "")
                    virtual = df_modalidad.iloc[0].get("Virtual", "")
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                            VALUES (?, ?, ?)
                        ''', id, presencial, virtual)

                conn.commit()
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    enqueue_scraper_job(id)
                    st.info("Scraper encolado para este proyecto.")
                except Exception as e:
                    st.warning(f"No se pudo encolar el scraper: {e}")
                st.success("Cambios guardados correctamente.")
            except Exception as e:
                st.error(f"Error al guardar cambios: {e}")

# VISTA DEL FORMUALRIO 
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
sys.path.append("../..")
from codigos import obtener_codigos_ciiu
import re
import pandas as pd

# --- Función para obtener carreras desde la base de datos ---
def obtener_carreras_por_nivel(nivel):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Carrera FROM carreras_facultad WHERE Nivel = ?", nivel)
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        st.error(f"Error al consultar carreras: {e}")
        return []

def mostrar_formulario():
    # Tipo de carpeta fuera del formulario para actualización en tiempo real

    tipo_carpeta = st.selectbox("Tipo de carpeta", ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])

    with st.form("form_proyectos"):
        # --- Proyecto 1: Carrera Referencia ---
        st.subheader("Carrera Referencia")

        tipo_carpeta_lower = tipo_carpeta.lower()
        carreras_filtradas = []
        if tipo_carpeta != "Seleccione un tipo...":
            if "pregrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
            elif "posgrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
        if carreras_filtradas:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."])

        # --- Carrera linkedin ---
        agregar_carrera_linkedin = st.form_submit_button("Agregar carrera linkedin")
        if "mostrar_campo_linkedin" not in st.session_state:
            st.session_state["mostrar_campo_linkedin"] = False
        if agregar_carrera_linkedin:
            st.session_state["mostrar_campo_linkedin"] = True
        if st.session_state["mostrar_campo_linkedin"]:
            carrera_linkedin_input = st.text_input("Nombre de la Carrera Linkedin")
        else:
            carrera_linkedin_input = nombre_proyecto_1 if nombre_proyecto_1 != "Seleccione una carrera..." else ""

        # --- Proyecto 2: Carrera Estudio ---
        st.subheader("Carrera Estudio")
        nombre_proyecto_2 = st.text_input("Nombre de la Carrera Estudio")

        # --- SEMRUSH ---
        st.subheader("Palabra a consultar en SEMRUSH")
        palabra_semrush = st.text_input("Palabra clave")

        # --- Trends ---
        st.subheader("Trends (palabras y promedios)")
        if "df_trends" not in st.session_state:
            st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
        df_trends = st.data_editor(
            st.session_state["df_trends"],
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="trends_editor"
        )
        st.session_state["df_trends"] = df_trends

        # --- Código CIIU ---
        st.subheader("Código CIIU")
        codigos_ciiu = obtener_codigos_ciiu()
        codigo_ciiu = st.selectbox("Seleccione el código CIIU", ["Seleccione un código..."] + codigos_ciiu)

        # --- Modalidad de Oferta ---
        st.subheader("Modalidad de Oferta")
        if "modalidad_oferta" not in st.session_state:
            st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
        df_modalidad = st.data_editor(
            st.session_state["modalidad_oferta"],
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            key="modalidad_oferta_editor"
        )
        st.session_state["modalidad_oferta"] = df_modalidad

        # Botón de envío
        enviado = st.form_submit_button("Enviar formulario")

        if enviado:
            # Validaciones de campos requeridos
            errores = []
            if tipo_carpeta == "Seleccione un tipo...":
                errores.append("El campo 'Tipo de carpeta' es obligatorio.")
            if nombre_proyecto_1 == "Seleccione una carrera..." or not nombre_proyecto_1:
                errores.append("El campo 'Carrera Referencia' es obligatorio.")
            if not nombre_proyecto_2.strip():
                errores.append("El campo 'Carrera Estudio' es obligatorio.")
            if not palabra_semrush.strip():
                errores.append("El campo 'Palabra clave' es obligatorio.")
            if codigo_ciiu == "Seleccione un código...":
                errores.append("El campo 'Código CIIU' es obligatorio.")
            # Validar tendencias
            trends_validas = [row for row in df_trends.to_dict("records") if row.get("Palabra", "").strip() and row.get("Promedio", "").strip()]
            if not trends_validas:
                errores.append("Debe ingresar al menos una palabra y promedio en 'Trends'.")
            # Validar modalidad de oferta
            modalidad_valida = False
            if df_modalidad.shape[0] > 0:
                presencial = df_modalidad.iloc[0].get("Presencial", "").strip()
                virtual = df_modalidad.iloc[0].get("Virtual", "").strip()
                modalidad_valida = presencial and virtual
            if not modalidad_valida:
                errores.append("Debe ingresar modalidad presencial y virtual.")

            if errores:
                for err in errores:
                    st.warning(err)
            else:
                # Guardar en la base de datos
                try:
                    # Usar un cursor exclusivo para la transacción
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO proyectos_tendencias (
                                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin
                            ) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                            tipo_carpeta,
                            nombre_proyecto_1,
                            nombre_proyecto_2,
                            palabra_semrush,
                            codigo_ciiu,
                            carrera_linkedin_input
                        )
                        proyecto_id_row = cur.fetchone()
                        if proyecto_id_row is None or proyecto_id_row[0] is None:
                            raise Exception("No se pudo obtener el ID del proyecto insertado.")
                        proyecto_id = int(proyecto_id_row[0])

                        # Insertar tendencias
                        for row in df_trends.to_dict("records"):
                            palabra = row.get("Palabra", "")
                            promedio = row.get("Promedio", None)
                            if palabra:
                                try:
                                    promedio_float = float(promedio)
                                except:
                                    promedio_float = None
                                # Guardar como valores nativos, no como string
                                cur.execute('''
                                    INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                    VALUES (?, ?, ?)
                                ''', proyecto_id, palabra, promedio_float)

                        # Insertar modalidad de oferta (solo una fila)
                        if df_modalidad.shape[0] > 0:
                            presencial = df_modalidad.iloc[0].get("Presencial", "")
                            virtual = df_modalidad.iloc[0].get("Virtual", "")
                            # Guardar como valores nativos, no como string
                            cur.execute('''
                                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                                VALUES (?, ?, ?)
                            ''', proyecto_id, presencial, virtual)

                        conn.commit()
                    # Encolar job para el nuevo proyecto
                    try:
                        from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                        enqueue_scraper_job(proyecto_id)
                        st.info("Scraper encolado para el nuevo proyecto.")
                    except Exception as e:
                        st.warning(f"No se pudo encolar el scraper: {e}")
                    # Guardar bandera de éxito y limpiar datos
                    st.session_state["exito_guardado"] = True
                    st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
                    st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
                    st.session_state["search_query"] = ""
                    st.session_state["page"] = "inicio"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en la base de datos: {e}")

