import pandas as pd
from scrapers.linkedin_modules.linkedin_database import (
    extraer_datos_tabla,
    obtener_id_carrera,
    obtener_codigos_por_id_carrera,
)

MERCADO = 0.15
ARCHIVO_MERCADO = "db/mercado.xlsx"
HOJAS = ["Total Ingresos", "Ventas 12", "Ventas 0"]

def calc_mercado(proyecto_id):
    print(f"\n=== INFORMACIÓN DE ARCHIVOS ===")
    print(f"Archivo de datos de mercado (referencia): {ARCHIVO_MERCADO}")
    print(f"Proyecto ID: {proyecto_id}")

    # Obtener datos del proyecto desde la base de datos
    proyecto = extraer_datos_tabla("reporteLinkedin", proyecto_id)
    if not proyecto:
        print("ERROR: No se pudo obtener datos del proyecto.")
        return 0
    proyecto = proyecto[0]
    carrera_referencia = proyecto.get("ProyectoReferencia")
    codigo_ciiu_consultar = proyecto.get("CodigoCIIU")

    # Obtener ID de la carrera referencia
    try:
        id_carrera = obtener_id_carrera(carrera_referencia)
    except ValueError as e:
        print(f"ERROR: No se pudo obtener el ID de la carrera: {e}.")
        return 0

    # Obtener códigos CIIU de la carrera referencia
    try:
        codigos_referencia = obtener_codigos_por_id_carrera(id_carrera)
        codigos_referencia = [c.strip() for c in codigos_referencia]
    except ValueError as e:
        print(f"ERROR: No se pudieron obtener los códigos de la carrera referencia: {e}.")
        return 0

    # Código CIIU de la carrera a consultar (puede ser lista o string)
    codigos_consultar = [codigo_ciiu_consultar.strip()] if codigo_ciiu_consultar else []
    if not codigos_consultar:
        print("ERROR: No se encontró código CIIU para la carrera a consultar.")
        return 0

    resultados_carreraReferencia = {}
    resultados_carreraConsultar = {}

    for hoja in HOJAS:
        print(f"\n--- Procesando hoja: {hoja} ---")
        try:
            df = pd.read_excel(ARCHIVO_MERCADO, sheet_name=hoja)
            print(f"Filas totales en la hoja: {len(df)}")
        except Exception as e:
            print(f"ERROR: Fallo al leer la hoja '{hoja}' del archivo '{ARCHIVO_MERCADO}': {e}.")
            resultados_carreraReferencia[hoja] = 0
            resultados_carreraConsultar[hoja] = 0
            continue

        # Limpiar columna de códigos
        if "ACTIVIDAD ECONÓMICA" in df.columns:
            df["ACTIVIDAD ECONÓMICA"] = df["ACTIVIDAD ECONÓMICA"].astype(str).str.strip()
        else:
            print(f"ERROR: No se encontró columna 'ACTIVIDAD ECONÓMICA' en la hoja '{hoja}'.")
            resultados_carreraReferencia[hoja] = 0
            resultados_carreraConsultar[hoja] = 0
            continue

        # Referencia: sumar valores para todos los códigos de la carrera referencia
        df_ref = df[df["ACTIVIDAD ECONÓMICA"].isin(codigos_referencia)]
        total_ref = df_ref["2024"].sum() if "2024" in df_ref.columns else 0
        resultados_carreraReferencia[hoja] = total_ref

        # Consulta: sumar valores para el código CIIU de la carrera a consultar
        df_cons = df[df["ACTIVIDAD ECONÓMICA"].isin(codigos_consultar)]
        total_cons = df_cons["2024"].sum() if "2024" in df_cons.columns else 0
        resultados_carreraConsultar[hoja] = total_cons

        print(f"Referencia - códigos encontrados: {df_ref['ACTIVIDAD ECONÓMICA'].tolist()}")
        print(f"Referencia - valores 2024: {df_ref['2024'].tolist() if '2024' in df_ref.columns else []}")
        print(f"Total referencia para {hoja}: {total_ref}")

        print(f"Consulta - códigos encontrados: {df_cons['ACTIVIDAD ECONÓMICA'].tolist()}")
        print(f"Consulta - valores 2024: {df_cons['2024'].tolist() if '2024' in df_cons.columns else []}")
        print(f"Total consulta para {hoja}: {total_cons}")

    print(f"\n=== RESUMEN DE VALORES ===")
    print(f"Resultados carrera de referencia: {resultados_carreraReferencia}")
    print(f"Resultados carrera a consultar: {resultados_carreraConsultar}")
    print(f"Factor MERCADO: {MERCADO}")

    # Calcular el promedio
    print(f"\n=== PROCESO DE CÁLCULO ===")
    total = 0
    cantidad = 0
    hojas_procesadas = []
    hojas_omitidas = []

    for hoja in HOJAS:
        valor_ref = resultados_carreraReferencia.get(hoja, 0)
        valor_consultar = resultados_carreraConsultar.get(hoja, 0)

        print(f"\n--- Calculando para hoja: {hoja} ---")
        print(f"Valor referencia ({hoja}): {valor_ref} (tipo: {type(valor_ref)})")
        print(f"Valor consultar ({hoja}): {valor_consultar} (tipo: {type(valor_consultar)})")

        if valor_consultar is None or valor_consultar == 0:
            print(f"ADVERTENCIA: Valor consultar es None o 0 para hoja '{hoja}' - Esta hoja será omitida del cálculo")
            hojas_omitidas.append(f"{hoja} (valor_consultar={valor_consultar})")
            continue

        if valor_ref is None or valor_ref == 0:
            print(f"ADVERTENCIA: Valor referencia es None o 0 para hoja '{hoja}' - Esta hoja será omitida del cálculo")
            hojas_omitidas.append(f"{hoja} (valor_ref={valor_ref})")
            continue

        try:
            valor_ref = float(valor_ref)
            valor_consultar = float(valor_consultar)
        except (ValueError, TypeError) as e:
            print(f"ERROR: valor_ref o valor_consultar no es numérico en hoja '{hoja}': valor_ref={valor_ref}, valor_consultar={valor_consultar} - Error: {e}")
            hojas_omitidas.append(f"{hoja} (error conversión)")
            continue

        resultado = (valor_consultar * MERCADO / valor_ref) * 100
        print(f"Cálculo: ({valor_consultar} * {MERCADO} / {valor_ref}) * 100 = {resultado}")
        total += resultado
        cantidad += 1
        hojas_procesadas.append(hoja)
        print(f"Total acumulado: {total}, Cantidad: {cantidad}")

    print(f"\n=== RESULTADO FINAL ===")
    print(f"Hojas procesadas exitosamente: {hojas_procesadas}")
    print(f"Hojas omitidas: {hojas_omitidas}")
    print(f"Total suma de resultados: {total}")
    print(f"Cantidad de hojas procesadas: {cantidad}")

    promedio = round(total / cantidad, 2) if cantidad else 0
    print(f"Promedio calculado: {promedio}")

    if promedio >= 15:
        print(f"Promedio >= 15, limitando a 15")
        promedio = 15

    print(f"Promedio final retornado: {promedio}")

    if len(hojas_omitidas) > 0:
        print(f"\n=== DIAGNÓSTICO ===")
        print(f"Se omitieron {len(hojas_omitidas)} de {len(HOJAS)} hojas:")
        for hoja_omitida in hojas_omitidas:
            print(f"  - {hoja_omitida}")
        print(f"Esto puede indicar:")
        print(f"  - Datos faltantes en la fuente de consulta")
        print(f"  - Problemas de mapeo entre nombres de hojas/columnas")
        print(f"  - Datos no numéricos en las fuentes")

    return promedio