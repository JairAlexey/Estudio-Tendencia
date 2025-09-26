# VISTA DEL FORMUALRIO 
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
sys.path.append("../..")
from codigos import obtener_codigos_ciiu
import re
import pandas as pd
import unicodedata

# Listas de carreras para el selectbox de Carrera Linkedin
NOMBRES_POSTGRADO = [
    "MAESTRIA EN CREACION Y PRODUCCION DE CONTENIDOS DIGITALES",
    "M. DESARROLLO E INNOVACION DE ALIMENTOS",
    "M. INTERPRETACION MUSICAL",
    "M. CREACION MUSICAL",
    "DIRECCION DE COMPRAS MENCION EN PROCUREMENT",
    "DIRECCION DE NEGOCIOS DIGITALES",
    "EDUCACION BASICA",
    "INNOVACION ORGANIZACIONAL Y TRANSFORMACION ESTRATEGICA",
    "INTELIGENCIA ARTIFICIAL APLICADA AL MARKETING DIGITAL",
    "ENFERMERIA MENCION EN PRACTICA AVANZADA EN CUIDADOS CRITICOS",
    "ENFERMERIA MENCION EN PRACTICA AVANZADA EN ENFERMERIA QUIRURGICA",
    "M. ENFERMERIA NEONATAL",
    "M. IMAGENOLOGIA INTERVENCIONISTA",
    "M. ENFERMERIA MENCION EN LIDERAZGO Y GESTION DE ENFERMERIA",
    "MAESTRIA EN ADMINISTRACION Y GESTION DE NEGOCIOS VETERINARIOS",
    "M. ADMINISTRACIÓN DE SERVICIOS DE SALUD ESPECIALIZADOS",
    "M. TERAPIA Y ASESORÍA FAMILIAR SISTÉMICA",
    "M. PSICOTERAPIA",
    "MAESTRIA EN CIBERSEGURIDAD",
    "MAESTRIA EN TALENTO HUMANO",
    "COMUNICACION ESTRATEGICA Y GESTION CORPORATIVA",
    "MARKETING DIGITAL",
    "ESPECIALIDAD MEDICINA INTERNA",
    "MAESTRIA EN COMERCIO EXTERIOR",
    "GERENCIA POLITICA, GOBERNANZA Y GOBERNABILIDAD",
    "NEUROMARKETING",
    "GERIATRIA",
    "MAESTRIA DIRECCION NEGOCIOS DEPORTIVOS",
    "DIREECCION EMPRESARIAL EN ARQUITECTURA Y DISEÑO",
    "MAESTRIA GESTION ESTRATEGICA DE TALENTO HUMANO",
    "CARDIOLOGIA",
    "PEDIATRIA",
    "ORTODONCIA",
    "ODONTOPEDIATRIA",
    "NEURORREHABILITACION",
    "NEUMOLOGIA",
    "MEDICINA CRITICA Y CUIDADOS INTENSIVOS",
    "SALUD PUBLICA",
    "GINECOLOGIA",
    "ANESTESIOLOGIA",
    "MEDICINA DEL TRABAJO",
    "DERECHO PENAL, MENCION EN CRIMINALIDAD COMPLEJA",
    "ENDODONCIA",
    "REHABILITACION ORAL Y PROTESIS IMPLANTO ASISTIDA",
    "GERENCIA DE SISTEMAS Y TECNOLOGIA EMPRESARIAL",
    "ADMINISTRACION Y GERENCIA ORGANIZACIONAL MAGO",
    "MERCADOTECNIA, MENCION ESTRATEGIA DIGITAL",
    "ADMINISTRACION MBA",
    "FINANZAS CON MENCION EN MERCADO DE VALORES Y BANCA",
    "GESTION DE PROYECTOS",
    "TELECOMUNICACIONES",
    "EXPERIENCIA DEL USUARIO",
    "AGROINDUSTRIA, MENCION CALIDAD Y SEGURIDAD ALIMENTARIA",
    "DERECHO DIGITAL E INNOVACION MENCION ECONOMIA, CONFIANZA Y TRANS DIGITAL",
    "ARBITRAJE COMERCIAL Y DE INVERSIONES",
    "COMUNICACION POLITICA",
    "FILOSOFIA, POLITICA Y ECONOMIA (PPE)",
    "GESTION DE LA SEGURIDAD DE LA INFORMACION",
    "DIRECCION DE OPERACIONES Y SEGURIDAD INDUSTRIAL MDO",
    "DESARROLLO E INNOVACION DE ALIMENTOS",
    "URBANISMO MENCION GESTION DE LA CIUDAD",
    "DIRECCION Y POSTPRODUCCION AUDIOVISUAL DIGITAL",
    "GESTION DEL TALENTO HUMANO, MENCION DESARROLLO ORGANIZACIONAL",
    "DERECHO PROCESAL CONSTITUCIONAL",
    "TERAPIA RESPIRATORIA",
    "TERAPIA MANUAL ORTOPEDICA INTEGRAL",
    "NEUROLOGIA",
    "ENDOCRINOLOGIA",
    "CIRUGIA GENERAL",
    "ORTOPEDIA Y TRAUMATOLOGIA",
    "ENFERMERIA",
    "NEUROPSICOLOGIA CLINICA",
    "GESTION POR PROCESOS CON MENCION EN TRANSFORMACION DIGITAL",
    "MERCADOTECNIA, MENCION EN GERENCIA DE MARCA",
    "PERIODONCIA E IMPLANTOLOGIA QUIRURGICA",
    "DISEÑO ARQUITECTONICO",
    "ECONOMETRIA",
    "PEOPLE ANALYTICS"
]
NOMBRES_PREGRADO = [
    "CIENCIAS DE LA EDUCACIÓN",
    "DERECHO PRESENCIAL",
    "DERECHO EN LINEA",
    "REGULACION LEGAL DE LA INTELIGENCIA ARTIFICIAL",
    "INTERPRETACION MUSICAL",
    "CONTABILIDAD Y AUDITORIA",
    "INFORMATICA",
    "SEGURIDAD INFORMATICA Y PROTECCION DE DATOS",
    "MARKETING EN LINEA",
    "FINANZAS Y CONTABILIDAD",
    "LOGISTICA Y TRANSPORTE",
    "CIENCIA DE DATOS",
    "REALIDAD VIRTUAL Y VIDEOJUEGOS",
    "DISEÑO DE MODAS",
    "PSICOLOGIA ORGANIZACIONAL",
    "INGENIERIA AEROESPACIAL",
    "TECNOLOGIAS DE LA INFORMACION",
    "NEGOCIOS DEPORTIVOS",
    "PSICOLOGIA CLINICA",
    "TECNOLOGIA EN GASTRONOMIA",
    "MECANICA",
    "PSICOPEDAGOGIA",
    "AMBIENTAL",
    "EDUCACION INICIAL BILINGÜE",
    "EDUCACION",
    "ELECTRONICA Y AUTOMATIZACION",
    "BIOTECNOLOGIA",
    "MULTIMEDIA Y PRODUCCION AUDIOVISUAL",
    "CIENCIAS POLITICAS",
    "ADMINISTRACION DE EMPRESAS",
    "DISEÑO GRAFICO",
    "SONIDO Y ACUSTICA",
    "INDUSTRIAL",
    "ODONTOLOGIA",
    "SOFTWARE",
    "COMUNICACION",
    "ECONOMIA",
    "MUSICA",
    "ENFERMERIA",
    "PSICOLOGIA",
    "GASTRONOMIA",
    "NEGOCIOS INTERNACIONALES",
    "RELACIONES INTERNACIONALES",
    "DERECHO",
    "AGROINDUSTRIA",
    "MERCADOTECNIA",
    "NEGOCIOS DIGITALES",
    "TELECOMUNICACIONES",
    "PUBLICIDAD",
    "TURISMO",
    "FINANZAS",
    "CINE",
    "MEDICINA",
    "PERIODISMO",
    "DISEÑO DE PRODUCTOS",
    "FISIOTERAPIA",
    "VETERINARIA",
    "DISEÑO DE INTERIORES",
    "ARQUITECTURA"
]

# Definir mapeos de prioridad como constantes globales
PRIORITY_DEFAULT = 2  # Media por defecto
PRIORIDAD_MAP = {"Alta": 1, "Media": 2, "Baja": 3}
PRIORIDAD_INV_MAP = {1: "Alta", 2: "Media", 3: "Baja"}

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

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.upper()

def mostrar_formulario():
    # Tipo de carpeta fuera del formulario para actualización en tiempo real

    tipo_carpeta = st.selectbox("Tipo de carpeta", ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])
    
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
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."])
        # --- Carrera linkedin (nuevo selectbox dependiente del tipo de carpeta) ---
        if "posgrado" in tipo_carpeta.lower():
            opciones_linkedin = NOMBRES_POSTGRADO
        elif "pregrado" in tipo_carpeta.lower():
            opciones_linkedin = NOMBRES_PREGRADO
        else:
            opciones_linkedin = []
        carrera_linkedin_input = st.selectbox("Nombre de la Carrera Linkedin", opciones_linkedin)
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
                        for row in df_trends.to_dict("records"):
                            palabra = row.get("Palabra", "")
                            promedio = row.get("Promedio", None)
                            if palabra:
                                try:
                                    promedio_float = float(promedio)
                                except:
                                    promedio_float = None
                                cur.execute('''
                                    INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                    VALUES (%s, %s, %s)
                                ''', (proyecto_id, palabra, promedio_float))

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
        cur.execute("SELECT tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin FROM proyectos_tendencias WHERE id=%s", (id,))
        proyecto = cur.fetchone()
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, carrera_linkedin = proyecto

    # Obtener prioridad actual del proyecto
    with conn.cursor() as cur:
        cur.execute("SELECT priority FROM scraper_queue WHERE proyecto_id=%s ORDER BY created_at DESC LIMIT 1", (id,))
        row = cur.fetchone()
        prioridad_actual = row[0] if row else PRIORITY_DEFAULT

    # Tipo de carpeta y prioridad
    tipo_carpeta = st.selectbox("Tipo de carpeta", 
                               ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"], 
                               index=0 if "POSGRADOS" in tipo_carpeta else 1)
    
    prioridad_label = st.selectbox(
        "Prioridad de procesamiento", 
        ["Alta", "Media", "Baja"], 
        index=["Alta", "Media", "Baja"].index(PRIORIDAD_INV_MAP.get(prioridad_actual, "Media"))
    )

    # Tendencias
    with conn.cursor() as cur:
        cur.execute("SELECT palabra, promedio FROM tendencias WHERE proyecto_id=%s", (id,))
        tendencias = cur.fetchall()

    # Modalidad de oferta
    with conn.cursor() as cur:
        cur.execute("SELECT presencial, virtual FROM modalidad_oferta WHERE proyecto_id=%s", (id,))
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
    # --- Carrera linkedin (nuevo selectbox dependiente del tipo de carpeta) ---
    if "posgrado" in tipo_carpeta.lower():
        opciones_linkedin = NOMBRES_POSTGRADO
    elif "pregrado" in tipo_carpeta.lower():
        opciones_linkedin = NOMBRES_PREGRADO
    else:
        opciones_linkedin = []
    # Selecciona el valor actual si existe, si no el primero
    if carrera_linkedin and carrera_linkedin in opciones_linkedin:
        idx_linkedin = opciones_linkedin.index(carrera_linkedin)
    else:
        idx_linkedin = 0
    carrera_linkedin_input = st.selectbox("Nombre de la Carrera Linkedin", opciones_linkedin, index=idx_linkedin)
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
                # Normalizar campos antes de guardar
                nombre_proyecto_1_norm = normalizar_texto(nombre_proyecto_1)
                nombre_proyecto_2_norm = normalizar_texto(nombre_proyecto_2)
                palabra_semrush_norm = normalizar_texto(palabra_semrush)
                carrera_linkedin_input_norm = normalizar_texto(carrera_linkedin_input)
                # Actualizar proyecto principal
                with conn.cursor() as cur:
                    cur.execute('''
                        UPDATE proyectos_tendencias SET
                            tipo_carpeta=%s, carrera_referencia=%s, carrera_estudio=%s, palabra_semrush=%s, codigo_ciiu=%s, carrera_linkedin=%s
                        WHERE id=%s
                    ''', (tipo_carpeta, nombre_proyecto_1_norm, nombre_proyecto_2_norm, palabra_semrush_norm, codigo_ciiu, carrera_linkedin_input_norm, id))

                # Eliminar tendencias
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM tendencias WHERE proyecto_id=%s", (id,))

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
                                VALUES (%s, %s, %s)
                            ''', (id, palabra, promedio_float))

                # Eliminar modalidad de oferta
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM modalidad_oferta WHERE proyecto_id=%s", (id,))

                # Insertar modalidad de oferta
                if df_modalidad.shape[0] > 0:
                    presencial = df_modalidad.iloc[0].get("Presencial", "")
                    virtual = df_modalidad.iloc[0].get("Virtual", "")
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                            VALUES (%s, %s, %s)
                        ''', (id, presencial, virtual))

                conn.commit()
                try:
                    from scrapers.linkedin_modules.linkedin_database import enqueue_scraper_job
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM scraper_queue WHERE proyecto_id=%s AND status IN ('queued','retry')", (id,))
                        conn.commit()
                    enqueue_scraper_job(id, priority=PRIORIDAD_MAP[prioridad_label])
                    st.info("Scraper encolado para este proyecto.")
                    st.success("Cambios guardados correctamente.")
                except Exception as e:
                    st.warning(f"No se pudo encolar el scraper: {e}")
            except Exception as e:
                st.error(f"Error al guardar cambios: {e}")