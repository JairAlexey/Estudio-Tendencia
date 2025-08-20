
import streamlit as st
import sys
sys.path.append("..")
from conexion import conn, cursor
sys.path.append("../..")
from codigos import obtener_codigos_ciiu, obtener_valor_por_codigo
import re
import pandas as pd

# --- Lista de carreras ---
carreras_nivel = [
    {"Nivel": "Pregrado", "Carrera": "Ingeniería en Software"},
    {"Nivel": "Pregrado", "Carrera": "Derecho"},
    {"Nivel": "Pregrado", "Carrera": "Medicina"},
    {"Nivel": "Pregrado", "Carrera": "Odontología"},
    {"Nivel": "Pregrado", "Carrera": "Psicología"},
    {"Nivel": "Pregrado", "Carrera": "Enfermería"},
    {"Nivel": "Pregrado", "Carrera": "Multimedia y Prod. Audiov"},
    {"Nivel": "Pregrado", "Carrera": "Arquitectura"},
    {"Nivel": "Pregrado", "Carrera": "Negocios Internacionales"},
    {"Nivel": "Pregrado", "Carrera": "Relaciones Internacionales"},
    {"Nivel": "Pregrado", "Carrera": "Gastronomía"},
    {"Nivel": "Pregrado", "Carrera": "Artes Musicales"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en gerencia politica, gobernanza y gobernabilidad"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en administracion de empresas mba"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en psicoterapia"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en diseño arquitectonico avanzado"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en neuromarketing"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en direccion y postproduccion audiovisual"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en derecho procesal constitucional"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en transformacion digital y gestion de la innovacion"},
    {"Nivel": "Posgrado", "Carrera": "Especialidad en ortodoncia"},
    {"Nivel": "Posgrado", "Carrera": "Maestria en enfermeria"}
]


def mostrar_formulario():
    st.title("Formulario de Proyectos y Tendencias")

    # Tipo de carpeta fuera del formulario para actualización en tiempo real
    tipo_carpeta = st.selectbox("Tipo de carpeta", ["Seleccione un tipo...", "POSGRADOS TENDENCIA", "CARRERAS PREGRADO"])

    with st.form("form_proyectos"):
        # --- Proyecto 1: Carrera Referencia ---
        st.subheader("Carrera Referencia")
        tipo_carpeta_lower = tipo_carpeta.lower()
        carreras_filtradas = []
        if tipo_carpeta != "Seleccione un tipo...":
            if "pregrado" in tipo_carpeta_lower:
                carreras_filtradas = [c["Carrera"] for c in carreras_nivel if c["Nivel"].lower() == "pregrado"]
            elif "posgrado" in tipo_carpeta_lower:
                carreras_filtradas = [c["Carrera"] for c in carreras_nivel if c["Nivel"].lower() == "posgrado"]
        if carreras_filtradas:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."] + carreras_filtradas)
        else:
            nombre_proyecto_1 = st.selectbox("Nombre de la Carrera Referencia", ["Seleccione una carrera..."])

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
                # Comprobar CIIU y mostrar tabla
                try:
                    ingresos_2023 = obtener_valor_por_codigo(codigo_ciiu, hoja='Total Ingresos', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
                    ventas12_2023 = obtener_valor_por_codigo(codigo_ciiu, hoja='Ventas 12', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
                    ventas0_2023 = obtener_valor_por_codigo(codigo_ciiu, hoja='Ventas 0', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
                    st.session_state["ingresos_2023"] = ingresos_2023
                    st.session_state["ventas12_2023"] = ventas12_2023
                    st.session_state["ventas0_2023"] = ventas0_2023
                    df_ciiu = pd.DataFrame([
                        ["Ingresos 2023", ingresos_2023],
                        ["Ventas 12 2023", ventas12_2023],
                        ["Ventas 0 2023", ventas0_2023]
                    ], columns=["Concepto", "Valor"])
                    df_ciiu["Valor"] = df_ciiu["Valor"].map(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                    st.table(df_ciiu)
                except Exception as e:
                    st.error(f"Error al obtener valores CIIU: {e}")

                st.success("✅ Datos guardados correctamente")
                datos_para_bd = {
                    "tipo_carpeta": tipo_carpeta,
                    "carrera_referencia": nombre_proyecto_1,
                    "carrera_estudio": nombre_proyecto_2,
                    "palabra_semrush": palabra_semrush,
                    "trends": df_trends.to_dict("records"),
                    "codigo_ciiu": codigo_ciiu,
                    "modalidad_oferta": df_modalidad.to_dict("records"),
                    "ingresos_2023": st.session_state.get("ingresos_2023", None),
                    "ventas12_2023": st.session_state.get("ventas12_2023", None),
                    "ventas0_2023": st.session_state.get("ventas0_2023", None)
                }
                st.write("Datos para la base de datos:", datos_para_bd)

                # Guardar en la base de datos
                try:
                    # Usar un cursor exclusivo para la transacción
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO proyectos_tendencias (
                                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, ingresos_2023, ventas12_2023, ventas0_2023
                            ) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''',
                            tipo_carpeta,
                            nombre_proyecto_1,
                            nombre_proyecto_2,
                            palabra_semrush,
                            codigo_ciiu,
                            st.session_state.get("ingresos_2023", None),
                            st.session_state.get("ventas12_2023", None),
                            st.session_state.get("ventas0_2023", None)
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
                                cur.execute('''
                                    INSERT INTO tendencias (proyecto_id, palabra, promedio)
                                    VALUES (?, ?, ?)
                                ''', proyecto_id, palabra, promedio_float)

                        # Insertar modalidad de oferta (solo una fila)
                        if df_modalidad.shape[0] > 0:
                            presencial = df_modalidad.iloc[0].get("Presencial", "")
                            virtual = df_modalidad.iloc[0].get("Virtual", "")
                            cur.execute('''
                                INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                                VALUES (?, ?, ?)
                            ''', proyecto_id, presencial, virtual)

                        conn.commit()
                    st.success("Datos guardados en la base de datos correctamente.")
                except Exception as e:
                    st.error(f"Error al guardar en la base de datos: {e}")

