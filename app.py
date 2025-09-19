import streamlit as st
import pandas as pd
import os
from data_process.mercado import calc_mercado
from data_process.linkedin import calc_linkedin
from data_process.busquedaWeb import calc_busquedaWeb
from data_process.competencia import calc_competencia_presencial, calc_competencia_virtual
from scrapers.linkedin_modules.linkedin_database import listar_proyectos
from conexion import conn

# Configuración de la página
st.set_page_config(
    page_title="Certificaciones", 
    layout="centered"
)


# Listar proyectos desde la base de datos
try:
    proyectos = listar_proyectos()
    if not proyectos:
        st.error("❌ No se encontraron proyectos en la base de datos.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error al cargar proyectos desde la base de datos: {e}")
    st.stop()

# Crear nombres para las pestañas desde DB
nombres_pestanas = [f"{p['id']} - {p['carrera_referencia']} vs {p['carrera_estudio']}" for p in proyectos]

# Si se pasó PROJECT_ID en el entorno, preseleccionarlo
preselected_index = 0
pref_id = os.getenv("PROJECT_ID")
if pref_id is not None:
    try:
        pref_id_int = int(pref_id)
        for idx, p in enumerate(proyectos):
            if p["id"] == pref_id_int:
                preselected_index = idx
                break
    except Exception:
        pass

# Título principal
st.title("Certificaciones")

# Lista de parámetros
parametros = ["Búsqueda Web", "LinkedIN", "Competencia", "Mercado", "Total"]

# Distribución deseada
distribucion_valores = {
    "Búsqueda Web": 0.35,
    "LinkedIN": 0.25,
    "Competencia": 0.25,
    "Mercado": 0.15,
}

# Función para calcular la distribución
def calcular_distribucion(parametro):
    return (
        sum(distribucion_valores.values())
        if parametro == "Total"
        else distribucion_valores.get(parametro, 0)
    )

# Función general para presencialidad y virtualidad cuando comparten lógica
def calcular_valor_general(parametro, proyecto_id):
    try:
        if parametro == "Búsqueda Web":
            return calc_busquedaWeb(proyecto_id)
        elif parametro == "LinkedIN":
            return calc_linkedin(proyecto_id)
        elif parametro == "Mercado":
            resultado = calc_mercado(proyecto_id)
            if resultado == 0:
                st.warning("No se encontraron datos de Mercado en el archivo Excel.")
            return resultado
        return 0
    except Exception as e:
        st.error(f"Error calculando {parametro}: {e}")
        return 0

# Funciones específicas para "Competencia"
def calcular_presencial_competencia(proyecto_id):
    try:
        return calc_competencia_presencial(proyecto_id)
    except Exception as e:
        st.error(f"Error calculando competencia presencial: {e}")
        return 0

def calcular_virtual_competencia(proyecto_id):
    try:
        return calc_competencia_virtual(proyecto_id)
    except Exception as e:
        st.error(f"Error calculando competencia virtual: {e}")
        return 0

# Función para procesar un archivo Excel específico
def procesar_proyecto(proyecto_id, nombre_archivo):
    presencialidad_resultados = []
    virtualidad_resultados = []
    # Calcular todos los valores requeridos una sola vez
    valor_busqueda = calcular_valor_general("Búsqueda Web", proyecto_id)
    valor_linkedin = calcular_valor_general("LinkedIN", proyecto_id)
    valor_mercado = calcular_valor_general("Mercado", proyecto_id)
    valor_competencia_presencial = calcular_presencial_competencia(proyecto_id)
    valor_competencia_virtual = calcular_virtual_competencia(proyecto_id)
    for i, parametro in enumerate(parametros):
        if parametro == "Competencia":
            presencialidad_resultados.append(valor_competencia_presencial)
            virtualidad_resultados.append(valor_competencia_virtual)
        elif parametro == "Total":
            total_presencial = round(sum(presencialidad_resultados), 2)
            total_virtual = round(sum(virtualidad_resultados), 2)
            presencialidad_resultados.append(total_presencial)
            virtualidad_resultados.append(total_virtual)
        elif parametro == "Búsqueda Web":
            presencialidad_resultados.append(valor_busqueda)
            virtualidad_resultados.append(valor_busqueda)
        elif parametro == "LinkedIN":
            presencialidad_resultados.append(valor_linkedin)
            virtualidad_resultados.append(valor_linkedin)
        elif parametro == "Mercado":
            presencialidad_resultados.append(valor_mercado)
            virtualidad_resultados.append(valor_mercado)
    # Guardar/actualizar en grafico_radar_datos
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM grafico_radar_datos WHERE proyecto_id=%s", (proyecto_id,))
        existe = cur.fetchone()
        if existe:
            cur.execute("""
                UPDATE grafico_radar_datos SET
                    valor_busqueda=%s, valor_competencia_presencialidad=%s, valor_competencia_virtualidad=%s, valor_linkedin=%s, valor_mercado=%s, updated_at=CURRENT_TIMESTAMP
                WHERE proyecto_id=%s
            """, (valor_busqueda, valor_competencia_presencial, valor_competencia_virtual, valor_linkedin, valor_mercado, proyecto_id))
        else:
            cur.execute("""
                INSERT INTO grafico_radar_datos (
                    proyecto_id, valor_busqueda, valor_competencia_presencialidad, valor_competencia_virtualidad, valor_linkedin, valor_mercado
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (proyecto_id, valor_busqueda, valor_competencia_presencial, valor_competencia_virtual, valor_linkedin, valor_mercado))
        conn.commit()
        cur.close()
    except Exception as e:
        st.error(f"Error actualizando datos de grafico_radar_datos: {e}")

    # Construcción del DataFrame
    datos = {
        "Parámetros": parametros,
        "Distribución": [
            (
                f"{calcular_distribucion(p) * 100:.0f}%"
                if p != "Total"
                else f"{calcular_distribucion(p) * 100:.0f}%"
            )
            for p in parametros
        ],
        "Presencialidad": presencialidad_resultados,
        "Virtualidad": virtualidad_resultados,
    }

    df = pd.DataFrame(datos)

    def resaltar_filas(row):
        return (
            ["background-color: #C10230; color: white"] * len(row)
            if row["Parámetros"] == "Total"
            else ["background-color: white"] * len(row)
        )

    styled_df = (
        df.style.apply(resaltar_filas, axis=1)
        .set_table_styles([{"selector": "th", "props": [("color", "black")]}])
        .format({"Presencialidad": lambda x: f"{x:.0f}%", "Virtualidad": lambda x: f"{x:.0f}%"})
    )

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

df_rango = pd.DataFrame(
    {
        "Rango": ["0% - 60%", "61% - 70%", "71% - 100%"],
        "Evaluación": [
            "Definitivamente No Viable",
            "Para revisión adicional",
            "Viable",
        ],
    }
)
