# VISTA DEL FORMUALRIO 
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
from components.loading import show_loading_spinner, loading_complete
# Eliminada la importación de codigos
import re
import pandas as pd
import unicodedata
import time  # Importar time para usarlo en los retrasos

# Definir mapeos de prioridad como constantes globales
PRIORITY_DEFAULT = 2  # Media por defecto
PRIORIDAD_MAP = {"Alta": 1, "Media": 2, "Baja": 3}
PRIORIDAD_INV_MAP = {1: "Alta", 2: "Media", 3: "Baja"}

# Función movida desde codigos.py
def obtener_codigos_ciiu(hoja_origen="Total Ingresos"):
    try:
        cursor.execute(
            "SELECT DISTINCT actividad_economica FROM mercado_datos WHERE hoja_origen = %s AND actividad_economica IS NOT NULL",
            (hoja_origen,)
        )
        rows = cursor.fetchall()
        codigos = [row[0] for row in rows]
        return codigos
    except Exception as e:
        st.error(f"ERROR al leer códigos CIIU desde la base de datos: {e}")
        return []

def obtener_carreras_por_nivel(nivel):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT Carrera FROM carreras_facultad WHERE Nivel = %s", (nivel,))
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        st.error(f"Error al consultar carreras: {e}")
        return []

def obtener_proyectos_carpeta(tipo_carpeta):
    """Obtiene los proyectos de una carpeta específica desde la base de datos"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT nombre_proyecto 
                FROM carpetas 
                WHERE tipo_carpeta = %s 
                ORDER BY nombre_proyecto
            """, (tipo_carpeta,))
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        st.error(f"Error al consultar proyectos: {e}")
        return []

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.upper()

def validar_trends_data(df_trends):
    """
    Valida y limpia los datos de tendencias
    Retorna: (datos_validos, mensaje_error)
    """
    trends_validas = []
    errores = []
    
    if df_trends.empty:
        return [], "No hay datos de tendencias"
        
    for idx, row in df_trends.iterrows():
        palabra = str(row.get("Palabra", "")).strip()
        promedio = row.get("Promedio", "")
        
        # Ignorar filas completamente vacías
        if not palabra and (promedio == "" or promedio is None):
            continue
            
        # Validar palabra
        if not palabra:
            errores.append(f"Fila {idx + 1}: La palabra no puede estar vacía")
            continue
            
        # Validar y convertir promedio
        try:
            # Considerar explícitamente "0" como valor válido
            if isinstance(promedio, str):
                promedio = promedio.replace(',', '.').strip()
                
            if promedio == "" or promedio is None:
                errores.append(f"Fila {idx + 1}: El promedio no puede estar vacío")
                continue
                
            # Convertir a float - el valor 0 es válido
            promedio_float = float(promedio)
            trends_validas.append({"palabra": palabra, "promedio": promedio_float})
        except ValueError:
            errores.append(f"Fila {idx + 1}: El promedio debe ser un número válido")
            
    if errores:
        return None, "\n".join(errores)
    if not trends_validas:
        return None, "Debe ingresar al menos una tendencia válida"
    return trends_validas, None

def mostrar_formulario():
    # Remove the internal return button - this will be handled by app.py
    
    # Tipo de carpeta fuera del formulario para actualización en tiempo real
    tipo_carpeta = st.selectbox("Tipo de carpeta", 
                               ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])
    
    # Obtener proyectos según el tipo de carpeta seleccionado
    proyectos_linkedin = []
    if tipo_carpeta != "Seleccione un tipo...":
        proyectos_linkedin = obtener_proyectos_carpeta(tipo_carpeta)

    # Agregar selector de prioridad
    prioridad_label = st.selectbox("Prioridad de procesamiento", 
                                  ["Alta", "Media", "Baja"], 
                                  index=1)
    
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
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", 
                                           ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", 
                                           ["Seleccione una carrera..."])

        # --- Carrera linkedin (usando datos de la base de datos) ---
        carrera_linkedin_input = st.selectbox("Nombre de la Carrera Referencia en Linkedin",
                                            ["Seleccione una carrera..."] + proyectos_linkedin)

        # --- Proyecto 2: Carrera Estudio (usando los mismos datos de LinkedIn) ---
        nombre_proyecto_2 = st.selectbox("Nombre de la Carrera Estudio en Linkedin",
                                     ["Seleccione una carrera..."] + proyectos_linkedin)

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
            width="stretch",
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
            width="stretch",
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
            trends_data, trends_error = validar_trends_data(df_trends)
            if trends_error:
                st.error(f"Error en tendencias:\n{trends_error}")
                return
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
                # Show loading spinner
                spinner = show_loading_spinner("Guardando proyecto y encolando scraper...")
                
                try:
                    # Normalizar campos antes de guardar
                    nombre_proyecto_1_norm = normalizar_texto(nombre_proyecto_1)
                    nombre_proyecto_2_norm = normalizar_texto(nombre_proyecto_2)
                    palabra_semrush_norm = normalizar_texto(palabra_semrush)
                    carrera_linkedin_input_norm = normalizar_texto(carrera_linkedin_input)
                    # Usar un cursor exclusivo para la transacción
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO proyectos_tendencias (
                                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id
                        ''', (
                            tipo_carpeta,
                            nombre_proyecto_1_norm,
                            nombre_proyecto_2_norm,
                            palabra_semrush_norm,
                            codigo_ciiu,
                            carrera_linkedin_input_norm
                        ))
                        proyecto_id_row = cur.fetchone()
                        if proyecto_id_row is None or proyecto_id_row[0] is None:
                            raise Exception("No se pudo obtener el ID del proyecto insertado.")
                        proyecto_id = int(proyecto_id_row[0])

                        # Insertar tendencias
                        for trend in trends_data:
                            cur.execute('''
                                INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                VALUES (%s, %s, %s)
                            ''', (proyecto_id, trend["palabra"], trend["promedio"]))

                        # Insertar modalidad de oferta (solo una fila)
                        if df_modalidad.shape[0] > 0:
                            presencial = df_modalidad.iloc[0].get("Presencial", "")
                            virtual = df_modalidad.iloc[0].get("Virtual", "")
                            cur.execute('''
                                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                                VALUES (%s, %s, %s)
                            ''', (proyecto_id, presencial, virtual))

                        conn.commit()
                    # Encolar job para el nuevo proyecto
                    try:
                        from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                        enqueue_scraper_job(proyecto_id, priority=PRIORIDAD_MAP[prioridad_label])
                        
                        # Show success message
                        loading_complete(spinner, "¡Proyecto guardado y scraper encolado correctamente!")
                        
                        # Guardar estado y mensaje con bandera de mostrar una sola vez
                        st.session_state["mensaje_exito"] = "Proyecto guardado y scraper encolado correctamente."
                        st.session_state["mostrar_mensaje"] = True  # Nueva bandera para controlar visualización
                        st.session_state["exito_guardado"] = True
                        st.session_state["df_trends"] = pd.DataFrame({"Palabra": [""], "Promedio": [""]})
                        st.session_state["modalidad_oferta"] = pd.DataFrame({"Presencial": [""], "Virtual": [""]})
                        st.session_state["search_query"] = ""
                        
                        # Redirigir a la página de inicio
                        st.session_state["page"] = "proyectos"
                        
                        # Allow the success message to be visible before redirecting
                        time.sleep(1.5)
                        st.rerun()
                        
                    except Exception as e:
                        spinner.empty()  # Remove spinner on error
                        st.warning(f"Proyecto guardado pero no se pudo encolar el scraper: {e}")
                        st.session_state["page"] = "proyectos"
                        st.rerun()
                        
                except Exception as e:
                    spinner.empty()  # Remove spinner on error
                    st.error(f"Error al guardar en la base de datos: {e}")


def mostrar_formulario_edicion(id):
    st.title("Editar Proyecto y Tendencias")
    
    # Get a fresh connection for each query
    from conexion import get_connection
    
    # Obtener datos actuales del proyecto
    try:
        conn_proyecto = get_connection()
        with conn_proyecto.cursor() as cur:
            cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin FROM proyectos_tendencias WHERE id=%s", (id,))
            proyecto = cur.fetchone()
            if not proyecto:
                st.error("Proyecto no encontrado.")
                conn_proyecto.close()
                return
            tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto
        conn_proyecto.close()
    except Exception as e:
        st.error(f"Error obteniendo datos del proyecto: {e}")
        return

    # Obtener prioridad actual del proyecto
    try:
        conn_prioridad = get_connection()
        with conn_prioridad.cursor() as cur:
            cur.execute("SELECT priority FROM scraper_queue WHERE proyecto_id=%s ORDER BY created_at DESC LIMIT 1", (id,))
            row = cur.fetchone()
            prioridad_actual = row[0] if row else PRIORITY_DEFAULT
        conn_prioridad.close()
    except Exception as e:
        st.error(f"Error obteniendo prioridad: {e}")
        prioridad_actual = PRIORITY_DEFAULT

    # Tipo de carpeta y prioridad (primer selectbox)
    tipo_carpeta = st.selectbox("Tipo de carpeta", 
                               ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"], 
                               index=0 if "POSGRADOS" in tipo_carpeta else 1,
                               key=f"tipo_carpeta_1_{id}")  # Añadir key única
    
    prioridad_label = st.selectbox(
        "Prioridad de procesamiento", 
        ["Alta", "Media", "Baja"], 
        index=["Alta", "Media", "Baja"].index(PRIORIDAD_INV_MAP.get(prioridad_actual, "Media")),
        key=f"prioridad_{id}"  # Añadir key única
    )

    # Tendencias - use a new connection
    try:
        conn_tendencias = get_connection()
        with conn_tendencias.cursor() as cur:
            cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=%s", (id,))
            tendencias = cur.fetchall()
        conn_tendencias.close()
    except Exception as e:
        st.error(f"Error obteniendo tendencias: {e}")
        tendencias = []

    # Modalidad de oferta - use a new connection
    try:
        conn_modalidad = get_connection()
        with conn_modalidad.cursor() as cur:
            cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=%s", (id,))
            modalidad = cur.fetchall()
        conn_modalidad.close()
    except Exception as e:
        st.error(f"Error obteniendo modalidad: {e}")
        modalidad = []

    # --- Formulario ---
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
    
    # --- Carrera linkedin (usando datos de la base de datos) ---
    proyectos_linkedin = obtener_proyectos_carpeta(tipo_carpeta)
    carrera_actual_index = 0
    if carrera_linkedin in proyectos_linkedin:
        carrera_actual_index = proyectos_linkedin.index(carrera_linkedin)
    carrera_linkedin_input = st.selectbox(
        "Nombre de la Carrera Referencia en Linkedin", 
        proyectos_linkedin,
        index=carrera_actual_index
    )
    
    # --- Proyecto 2: Carrera Estudio (usando los mismos datos de LinkedIn) ---
    # FIX: Properly initialize the second project name dropdown with current value
    carrera_estudio_index = 0
    if carrera_estudio in proyectos_linkedin:
        carrera_estudio_index = proyectos_linkedin.index(carrera_estudio)
    nombre_proyecto_2 = st.selectbox(
        "Nombre de la Carrera Estudio en Linkedin",
        proyectos_linkedin,
        index=carrera_estudio_index,
        key=f"carrera_estudio_{id}"
    )

    # --- SEMRUSH ---
    st.subheader("Palabra a consultar en SEMRUSH")
    palabra_semrush = st.text_input("Palabra clave", value=palabra_semrush)

    # --- Trends ---
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
        df_trends = st.data_editor(df_trends, num_rows="dynamic", width="stretch", hide_index=True, key=f"trends_editor_{id}")
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
    df_modalidad = st.data_editor(df_modalidad, num_rows="fixed", width="stretch", hide_index=True, key=f"modalidad_oferta_editor_{id}")
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
        # Validar tendencias
        trends_data, trends_error = validar_trends_data(df_trends)
        if trends_error:
            st.error(f"Error en tendencias:\n{trends_error}")
            return
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
            # Show loading spinner
            spinner = show_loading_spinner("Guardando cambios y actualizando proyecto...")
            
            try:
                # Get a new connection for saving changes
                conn_guardar = get_connection()
                
                # Normalizar campos antes de guardar
                nombre_proyecto_1_norm = normalizar_texto(nombre_proyecto_1)
                nombre_proyecto_2_norm = normalizar_texto(nombre_proyecto_2)
                palabra_semrush_norm = normalizar_texto(palabra_semrush)
                carrera_linkedin_input_norm = normalizar_texto(carrera_linkedin_input)
                
                # Actualizar proyecto principal
                with conn_guardar.cursor() as cur:
                    cur.execute('''
                        UPDATE proyectos_tendencias SET
                            tipo_carpeta=%s, carrera_referencia=%s, carrera_estudio=%s, palabra_semrush=%s, codigo_ciiu=%s, carrera_linkedin=%s
                        WHERE id=%s
                    ''', (tipo_carpeta, nombre_proyecto_1_norm, nombre_proyecto_2_norm, palabra_semrush_norm, codigo_ciiu, carrera_linkedin_input_norm, id))

                # Eliminar tendencias
                with conn_guardar.cursor() as cur:
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=%s", (id,))

                # Insertar tendencias
                with conn_guardar.cursor() as cur:
                    for trend in trends_data:
                        cur.execute('''
                            INSERT INTO tendencias (proyecto_id, palabra, promedio)
                            VALUES (%s, %s, %s)
                        ''', (id, trend["palabra"], trend["promedio"]))

                # Eliminar modalidad de oferta
                with conn_guardar.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=%s", (id,))

                # Insertar modalidad de oferta
                if df_modalidad.shape[0] > 0:
                    presencial = df_modalidad.iloc[0].get("Presencial", "")
                    virtual = df_modalidad.iloc[0].get("Virtual", "")
                    with conn_guardar.cursor() as cur:
                        cur.execute('''
                            INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                            VALUES (%s, %s, %s)
                        ''', (id, presencial, virtual))

                # Commit all changes
                conn_guardar.commit()
                conn_guardar.close()
                
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    # Use a fresh connection for queue operations
                    conn_queue = get_connection()
                    with conn_queue.cursor() as cur:
                        cur.execute("DELETE FROM scraper_queue WHERE proyecto_id=%s AND status IN ('queued','retry')", (id,))
                    conn_queue.commit()
                    conn_queue.close()
                    
                    # Enqueue the job
                    enqueue_scraper_job(id, priority=PRIORIDAD_MAP[prioridad_label])
                    
                    # Show success message
                    loading_complete(spinner, "¡Cambios guardados y scraper encolado correctamente!")
                    
                    # Set session state variables for redirection
                    st.session_state["mensaje_exito"] = "Cambios guardados y scraper encolado correctamente."
                    st.session_state["mostrar_mensaje"] = True
                    st.session_state["exito_guardado"] = True
                    
                    # Redirect to projects page
                    st.session_state["page"] = "proyectos"
                    
                    # Allow success message to be visible before redirecting
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    spinner.empty()  # Remove spinner on error
                    st.warning(f"No se pudo encolar el scraper: {e}")
            except Exception as e:
                spinner.empty()  # Remove spinner on error
                st.error(f"Error al guardar cambios: {e}")
                # Try to rollback if possible
                try:
                    if 'conn_guardar' in locals() and conn_guardar:
                        conn_guardar.rollback()
                        conn_guardar.close()
                except:
                    pass