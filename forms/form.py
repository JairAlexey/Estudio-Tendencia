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
def obtener_codigos_ciiu(hoja_origen="Total Ingresos", tipo_carpeta=None):
    """
    Obtiene los códigos CIIU según el tipo de carpeta.
    
    Args:
        hoja_origen: Nombre de la hoja (default: "Total Ingresos")
        tipo_carpeta: Tipo de carpeta seleccionado. Si es "CARRERAS PREGRADO CR" usa cr_mercado_datos,
                     de lo contrario usa mercado_datos
    
    Returns:
        Lista de códigos CIIU
    """
    try:
        # Determinar qué tabla usar según el tipo de carpeta
        if tipo_carpeta and "pregrado cr" in tipo_carpeta.lower():
            tabla = "cr_mercado_datos"
        else:
            tabla = "mercado_datos"
        
        cursor.execute(
            f"SELECT DISTINCT actividad_economica FROM {tabla} WHERE hoja_origen = %s AND actividad_economica IS NOT NULL",
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

def obtener_tipos_carpeta():
    """Obtiene los tipos de carpeta disponibles desde la base de datos"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT tipo_carpeta 
                FROM carpetas 
                ORDER BY tipo_carpeta
            """)
            return [row[0] for row in cur.fetchall()]
    except Exception as e:
        st.error(f"Error al consultar tipos de carpeta: {e}")
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
    
    # ID Ticket
    id_ticket = st.text_input("ID del Ticket", placeholder="Ingrese el ID del ticket")
    
    # Tipo de carpeta fuera del formulario para actualización en tiempo real
    tipos_carpeta_disponibles = obtener_tipos_carpeta()
    tipos_carpeta_opciones = ["Seleccione un tipo..."] + tipos_carpeta_disponibles if tipos_carpeta_disponibles else ["Seleccione un tipo..."]
    
    tipo_carpeta = st.selectbox("Tipo de carpeta", tipos_carpeta_opciones)
    
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
            # Si es específicamente Costa Rica
            if "pregrado cr" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Pregrado CR")
            # Si contiene "pregrado" pero no CR
            elif "pregrado" in tipo_carpeta_lower:
                carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
            # Si contiene "posgrado" o "maestria"
            elif "posgrado" in tipo_carpeta_lower or "maestria" in tipo_carpeta_lower:
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

        # --- Valor Búsqueda Web ---
        valor_busqueda_web = st.number_input(
            "Inteligencia Artificial Entrenada", 
            min_value=0, 
            max_value=35, 
            value=0, 
            step=1,
            help="Ingresa el valor de la inteligencia artificial entrenada"
        )

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
        codigos_ciiu = obtener_codigos_ciiu(tipo_carpeta=tipo_carpeta)
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
            if not id_ticket.strip():
                errores.append("El campo 'ID del Ticket' es obligatorio.")
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
                    # Preparar datos para la inserción
                    from database.db_utils import insertar_proyecto_con_reintentos
                    
                    # Preparar los datos del proyecto
                    datos_proyecto = {
                        'tipo_carpeta': tipo_carpeta,
                        'carrera_referencia': nombre_proyecto_1_norm,
                        'carrera_estudio': nombre_proyecto_2_norm,
                        'palabra_semrush': palabra_semrush_norm,
                        'codigo_ciiu': codigo_ciiu,
                        'carrera_linkedin': carrera_linkedin_input_norm,
                        'id_ticket': id_ticket.strip(),
                        'inteligencia_artificial_entrada': float(valor_busqueda_web),
                        'trends': trends_data,
                        'modalidad': None
                    }
                    
                    # Añadir modalidad si existe
                    if df_modalidad.shape[0] > 0:
                        datos_proyecto['modalidad'] = {
                            'presencial': df_modalidad.iloc[0].get("Presencial", ""),
                            'virtual': df_modalidad.iloc[0].get("Virtual", "")
                        }
                    
                    # Intentar insertar el proyecto con reintentos
                    exito, proyecto_id, error = insertar_proyecto_con_reintentos(datos_proyecto)
                    
                    if not exito:
                        raise Exception(error)
                    
                    if proyecto_id is None:
                        raise Exception("No se pudo obtener el ID del proyecto insertado.")

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
            cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin, id_ticket, inteligencia_artificial_entrada FROM proyectos_tendencias WHERE id=%s", (id,))
            proyecto = cur.fetchone()
            if not proyecto:
                st.error("Proyecto no encontrado.")
                conn_proyecto.close()
                return
            tipo_carpeta_original, carrera_referencia_original, carrera_estudio_original, palabra_semrush_original, codigo_ciiu_original, carrera_linkedin_original, id_ticket_actual, inteligencia_artificial_entrada_actual = proyecto
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

    # Obtener valor_busqueda_web actual
    valor_busqueda_web_actual = inteligencia_artificial_entrada_actual if inteligencia_artificial_entrada_actual is not None else 0

    # ID Ticket
    id_ticket = st.text_input("ID del Ticket", value=id_ticket_actual, key=f"id_ticket_{id}")

    # Tipo de carpeta y prioridad (primer selectbox)
    tipos_carpeta_disponibles = obtener_tipos_carpeta()
    tipos_carpeta_opciones = tipos_carpeta_disponibles if tipos_carpeta_disponibles else [tipo_carpeta_original]
    
    # Encontrar el índice del tipo de carpeta original
    try:
        tipo_index = tipos_carpeta_opciones.index(tipo_carpeta_original) if tipo_carpeta_original in tipos_carpeta_opciones else 0
    except:
        tipo_index = 0
    
    tipo_carpeta = st.selectbox("Tipo de carpeta", 
                               tipos_carpeta_opciones, 
                               index=tipo_index,
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
    # Si es específicamente Costa Rica
    if "pregrado cr" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Pregrado CR")
    # Si contiene "pregrado" pero no CR
    elif "pregrado" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Pregrado")
    # Si contiene "posgrado" o "maestria"
    elif "posgrado" in tipo_carpeta_lower or "maestria" in tipo_carpeta_lower:
        carreras_filtradas = obtener_carreras_por_nivel("Posgrado")
    if carreras_filtradas:
        if carrera_referencia_original in carreras_filtradas:
            carrera_ref_index = carreras_filtradas.index(carrera_referencia_original)
        else:
            carreras_filtradas = [carrera_referencia_original] + [c for c in carreras_filtradas if c != carrera_referencia_original]
            carrera_ref_index = 0
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", carreras_filtradas, index=carrera_ref_index)
    else:
        nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", [carrera_referencia_original])
    
    # --- Carrera linkedin (usando datos de la base de datos) ---
    proyectos_linkedin = obtener_proyectos_carpeta(tipo_carpeta)
    carrera_actual_index = 0
    if carrera_linkedin_original in proyectos_linkedin:
        carrera_actual_index = proyectos_linkedin.index(carrera_linkedin_original)
    carrera_linkedin_input = st.selectbox(
        "Nombre de la Carrera Referencia en Linkedin", 
        proyectos_linkedin,
        index=carrera_actual_index
    )
    
    # --- Proyecto 2: Carrera Estudio (usando los mismos datos de LinkedIn) ---
    # FIX: Properly initialize the second project name dropdown with current value
    carrera_estudio_index = 0
    if carrera_estudio_original in proyectos_linkedin:
        carrera_estudio_index = proyectos_linkedin.index(carrera_estudio_original)
    nombre_proyecto_2 = st.selectbox(
        "Nombre de la Carrera Estudio en Linkedin",
        proyectos_linkedin,
        index=carrera_estudio_index,
        key=f"carrera_estudio_{id}"
    )

    # --- SEMRUSH ---
    st.subheader("Palabra a consultar en SEMRUSH")
    palabra_semrush = st.text_input("Palabra clave", value=palabra_semrush_original)

    # --- Inteligencia Artificial Entrenada ---
    valor_busqueda_web = st.number_input(
        "Inteligencia Artificial Entrenada", 
        min_value=0, 
        max_value=35, 
        value=int(valor_busqueda_web_actual), 
        step=1,
        help="Ingrese el valor de inteligencia artificial entrenada",
        key=f"valor_busqueda_web_{id}"
    )

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
    codigos_ciiu = obtener_codigos_ciiu(tipo_carpeta=tipo_carpeta)
    codigo_ciiu = st.selectbox("Seleccione el código CIIU", codigos_ciiu, index=codigos_ciiu.index(codigo_ciiu_original) if codigo_ciiu_original in codigos_ciiu else 0)
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
        if not id_ticket.strip():
            errores.append("El campo 'ID del Ticket' es obligatorio.")
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
                            tipo_carpeta=%s, carrera_referencia=%s, carrera_estudio=%s, palabra_semrush=%s, codigo_ciiu=%s, carrera_linkedin=%s, id_ticket=%s, inteligencia_artificial_entrada=%s
                        WHERE id=%s
                    ''', (tipo_carpeta, nombre_proyecto_1_norm, nombre_proyecto_2_norm, palabra_semrush_norm, codigo_ciiu, carrera_linkedin_input_norm, id_ticket.strip(), int(valor_busqueda_web), id))

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

                # Actualizar valor_busqueda_web en grafico_radar_datos
                with conn_guardar.cursor() as cur:
                    cur.execute('''
                        UPDATE grafico_radar_datos 
                        SET valor_busqueda=%s, updated_at=CURRENT_TIMESTAMP
                        WHERE proyecto_id=%s
                    ''', (float(valor_busqueda_web), id))

                # Commit all changes
                conn_guardar.commit()
                conn_guardar.close()
                
                # Comparar valores originales con los nuevos para determinar si se necesita reencolar el scraper
                hay_cambios_significativos = False
                
                # Normalizar valores originales para comparación
                nombre_proyecto_1_original_norm = normalizar_texto(carrera_referencia_original)
                nombre_proyecto_2_original_norm = normalizar_texto(carrera_estudio_original)
                palabra_semrush_original_norm = normalizar_texto(palabra_semrush_original)
                carrera_linkedin_original_norm = normalizar_texto(carrera_linkedin_original)
                
                # Comparar campos principales
                if (tipo_carpeta != tipo_carpeta_original or
                    nombre_proyecto_1_norm != nombre_proyecto_1_original_norm or
                    nombre_proyecto_2_norm != nombre_proyecto_2_original_norm or
                    palabra_semrush_norm != palabra_semrush_original_norm or
                    codigo_ciiu != codigo_ciiu_original or
                    carrera_linkedin_input_norm != carrera_linkedin_original_norm):
                    hay_cambios_significativos = True
                
                # Comparar tendencias
                if not hay_cambios_significativos:
                    tendencias_originales = {(row[0], row[1]) for row in tendencias}
                    tendencias_nuevas = {(trend["palabra"], trend["promedio"]) for trend in trends_data}
                    if tendencias_originales != tendencias_nuevas:
                        hay_cambios_significativos = True
                
                # Comparar modalidad de oferta
                if not hay_cambios_significativos:
                    if modalidad:
                        presencial_original = modalidad[0][0] if len(modalidad[0]) > 0 else ""
                        virtual_original = modalidad[0][1] if len(modalidad[0]) > 1 else ""
                        presencial_nuevo = df_modalidad.iloc[0].get("Presencial", "") if df_modalidad.shape[0] > 0 else ""
                        virtual_nuevo = df_modalidad.iloc[0].get("Virtual", "") if df_modalidad.shape[0] > 0 else ""
                        if presencial_original != presencial_nuevo or virtual_original != virtual_nuevo:
                            hay_cambios_significativos = True
                
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    
                    if hay_cambios_significativos:
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
                    else:
                        # Show success message without re-enqueuing
                        loading_complete(spinner, "¡Cambios guardados correctamente!")
                        
                        # Set session state variables for redirection
                        st.session_state["mensaje_exito"] = "Cambios guardados correctamente."
                    
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