# VISTA DEL REPORTE 
import streamlit as st
import pandas as pd
from conexion import get_connection
import unicodedata
from scrapers.linkedin_modules.linkedin_database import listar_proyectos
import os
from data_process.mercado import calc_mercado
from data_process.linkedin import calc_linkedin
from data_process.busquedaWeb import calc_busquedaWeb
from data_process.competencia import calc_competencia_presencial, calc_competencia_virtual
from conexion import conn

# Función para normalizar texto (mayúsculas y sin tildes)
def normalizar_texto(texto):
    if not texto:
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.upper()

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
            # Ya no calculamos búsqueda web, se toma desde la base de datos
            # return calc_busquedaWeb(proyecto_id)  # COMENTADO: Ahora se guarda manualmente desde el form
            return 0  # Retornar 0 por defecto, el valor real se obtiene desde BD
        elif parametro == "LinkedIN":
            return calc_linkedin(proyecto_id)
        elif parametro == "Mercado":
            resultado = calc_mercado(proyecto_id)
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

# Función para procesar un proyecto
def procesar_proyecto(proyecto_id, nombre_archivo):
    presencialidad_resultados = []
    virtualidad_resultados = []
    # Obtener inteligencia_artificial_entrada desde la base de datos
    try:
        cur = conn.cursor()
        cur.execute("SELECT inteligencia_artificial_entrada FROM proyectos_tendencias WHERE id=%s", (proyecto_id,))
        row = cur.fetchone()
        valor_busqueda = float(row[0]) if row and row[0] is not None else 0.0
        cur.close()
    except Exception as e:
        st.warning(f"Error obteniendo inteligencia_artificial_entrada desde BD: {e}")
        valor_busqueda = 0.0
    
    # Calcular los demás valores requeridos una sola vez
    valor_linkedin = float(calcular_valor_general("LinkedIN", proyecto_id))
    valor_mercado = float(calcular_valor_general("Mercado", proyecto_id))
    valor_competencia_presencial = float(calcular_presencial_competencia(proyecto_id))
    valor_competencia_virtual = float(calcular_virtual_competencia(proyecto_id))
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
    # NOTA: valor_busqueda ya no se actualiza aquí, se guarda manualmente desde el formulario
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM grafico_radar_datos WHERE proyecto_id=%s", (proyecto_id,))
        existe = cur.fetchone()
        if existe:
            # Solo actualizar los valores calculados, no valor_busqueda
            cur.execute("""
                UPDATE grafico_radar_datos SET
                    valor_competencia_presencialidad=%s, valor_competencia_virtualidad=%s, valor_linkedin=%s, valor_mercado=%s, updated_at=CURRENT_TIMESTAMP
                WHERE proyecto_id=%s
            """, (
                float(valor_competencia_presencial),
                float(valor_competencia_virtual),
                float(valor_linkedin),
                float(valor_mercado),
                proyecto_id
            ))
        else:
            # Si no existe el registro, insertarlo con manejo de duplicados
            cur.execute("""
                INSERT INTO grafico_radar_datos (
                    proyecto_id, valor_busqueda, valor_competencia_presencialidad, valor_competencia_virtualidad, valor_linkedin, valor_mercado
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (proyecto_id) DO UPDATE SET
                    valor_competencia_presencialidad=EXCLUDED.valor_competencia_presencialidad,
                    valor_competencia_virtualidad=EXCLUDED.valor_competencia_virtualidad,
                    valor_linkedin=EXCLUDED.valor_linkedin,
                    valor_mercado=EXCLUDED.valor_mercado,
                    updated_at=CURRENT_TIMESTAMP;
            """, (
                proyecto_id,
                float(valor_busqueda),
                float(valor_competencia_presencial),
                float(valor_competencia_virtual),
                float(valor_linkedin),
                float(valor_mercado)
            ))
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
        "Presencialidad": [f"{v:.0f}%" for v in presencialidad_resultados],
        "Virtualidad": [f"{v:.0f}%" for v in virtualidad_resultados],
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
        # El formato ya incluye el símbolo %, así que no lo agregamos aquí
    )

    st.dataframe(styled_df, width="stretch", hide_index=True)

def mostrar_pagina_tabla(id):
    # Obtener nombre del proyecto con manejo de errores y rollback
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT palabra_semrush FROM proyectos_tendencias WHERE id=%s", (id,))
        row = cur.fetchone()
        nombre_proyecto = row[0] if row else "Proyecto desconocido"
        nombre_proyecto = " ".join([w.capitalize() for w in nombre_proyecto.split()])
        conn.commit()  # Commit successful read
    except Exception as e:
        conn.rollback()
        st.error(f"Error en la base de datos: {e}")
        return
    finally:
        cur.close()
        conn.close()

    # Procesar y mostrar el reporte
    try:
        proyectos = listar_proyectos()
        proyecto = next((p for p in proyectos if p["id"] == id), None)
        if not proyecto:
            st.error("Proyecto no encontrado.")
            return
        nombre_pestana = f"{proyecto['id']} - {proyecto['carrera_referencia']} vs {proyecto['carrera_estudio']}"
        st.subheader(f"Evaluación para {nombre_proyecto}")
        
        with st.spinner("Procesando reporte..."):
            procesar_proyecto(id, nombre_pestana)
            
        st.subheader("Rango Evaluación Final")
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
        st.dataframe(df_rango, width="stretch", hide_index=True)
    except Exception as e:
        st.error(f"ERROR mostrando reporte: {e}")