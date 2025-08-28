import pandas as pd
import os
from scrapers.linkedin_modules.linkedin_database import (
    obtener_id_carrera,
    extraer_datos_tabla,
    obtener_semrush_base_por_id,
    obtener_trends_base_por_id,
)

SEMRUSH = 0.15
TRENDS = 0.20

def calc_busquedaWeb(source=None):

    # Extraer carrera refereencia (desde DB siempre, usando proyecto_id cuando source es int)
    if isinstance(source, int):
        print(f"[Búsqueda Web] Fuente: Base de Datos (proyecto_id={source})")
        filas_ref = extraer_datos_tabla("reporteLinkedin", source)
        if not filas_ref:
            print("No se pudo obtener la carrera de referencia (reporteLinkedin vacío).")
            return 0
        carreraReferencia = filas_ref[0].get("ProyectoReferencia")
    else:
        print(f"[Búsqueda Web] Fuente: Excel")
        carreraReferencia = extraer_datos_tabla("carreraReferencia", source)
    if not carreraReferencia:
        print("No se pudo obtener la carrera de referencia.")
        return 0

    # Obtener ID Carrera referencia
    idCarrera = obtener_id_carrera(carreraReferencia)

    # Ubicacion archivo - usar ruta específica o fallback a variable de entorno
    if not isinstance(source, int):
        if source is None:
            archivo = os.getenv("EXCEL_PATH")
        else:
            archivo = source

    # Lectura archivo
    data = pd.read_excel(archivo, sheet_name=None) if not isinstance(source, int) else None

    # --- SEMRUSH ---
    if isinstance(source, int):
        try:
            semrush_base_dict = obtener_semrush_base_por_id(idCarrera)
        except Exception as e:
            print(f"No se pudo obtener semrush_base: {e}")
            return 0
        semrush_consulta_rows = extraer_datos_tabla("semrush", source)
        if not semrush_consulta_rows:
            print("No se encontraron datos de semrush para el proyecto.")
            return 0
        hjSemrushBase = pd.DataFrame([{
            'Visión General': semrush_base_dict.get('VisionGeneral', 0),
            'Palabras': semrush_base_dict.get('Palabras', 0),
            'Volumen': semrush_base_dict.get('Volumen', 0),
            'ID Carrera': idCarrera,
        }])
        hjSemrush = pd.DataFrame([{
            'Visión General': semrush_consulta_rows[0].get('VisionGeneral', 0),
            'Palabras': semrush_consulta_rows[0].get('Palabras', 0),
            'Volumen': semrush_consulta_rows[0].get('Volumen', 0),
        }])
        # Normalizar a numérico
        for col in ['Visión General', 'Palabras', 'Volumen']:
            hjSemrushBase[col] = pd.to_numeric(hjSemrushBase[col], errors='coerce').fillna(0)
            hjSemrush[col] = pd.to_numeric(hjSemrush[col], errors='coerce').fillna(0)
    else:
        if data is None or "SemrushBase" not in data or "Semrush" not in data:
            print("No se encontraron hojas 'SemrushBase' o 'Semrush' en el Excel.")
            return 0
        hjSemrushBase = data["SemrushBase"]
        hjSemrush = data["Semrush"]

    # --- CALCULO SEMRUSH ---
    # Filtrar en SemrushBase el ID Carrera por el id de la carrera referencia
    filtroCarrera = hjSemrushBase["ID Carrera"] == idCarrera if "ID Carrera" in hjSemrushBase.columns else [True] * len(hjSemrushBase)
    datosSemrushCarrera = hjSemrushBase[filtroCarrera]
    if datosSemrushCarrera.empty:
        print("Semrush base para la carrera no disponible.")
        return 0
    datosSemrushCarrera_dict = datosSemrushCarrera[['Visión General', 'Palabras', 'Volumen']].iloc[0].to_dict()

    # Guardar en un diccionario datos semrush consultados
    datosSemrushConsulta_dict = hjSemrush.iloc[0].to_dict()

    # Calculos
    # Vision general
    visionGeneralBase = datosSemrushCarrera_dict['Visión General']
    visionGeneralConsulta = datosSemrushConsulta_dict['Visión General']

    if visionGeneralBase != 0:
        resVisionGeneral = ((visionGeneralConsulta * SEMRUSH) / visionGeneralBase) * 100
    else:
        resVisionGeneral = 0  # O algún valor por defecto, o puedes lanzar un warning

    # Palabras
    palabrasBase = datosSemrushCarrera_dict['Palabras']
    palabrasConsulta = datosSemrushConsulta_dict['Palabras']

    if palabrasBase != 0:
        resPalabras = ((palabrasConsulta * SEMRUSH) / palabrasBase) * 100
    else:
        resPalabras = 0

    # Volumen
    volumenBase = datosSemrushCarrera_dict['Volumen']
    volumenConsulta = datosSemrushConsulta_dict['Volumen']

    if volumenBase != 0:
        resVolumen = ((volumenConsulta * SEMRUSH) / volumenBase) * 100
    else:
        resVolumen = 0

    # Calcular el promedio de las 3 columnas
    promedioSemrush = round(((resVisionGeneral + resPalabras + resVolumen) / 3), 2)

    # --- TRENDS ---
    if isinstance(source, int):
        try:
            trends_base_rows = obtener_trends_base_por_id(idCarrera)
        except Exception as e:
            print(f"No se pudo obtener tendencias base: {e}")
            return 0
        hjTrendsBase = pd.DataFrame(trends_base_rows)
        hjTrendsBase = hjTrendsBase.rename(columns={"Palabra": "Palabra", "Cantidad": "Cantidad"})
        hjTrends = pd.DataFrame(extraer_datos_tabla("tendencias", source))
        if hjTrends.empty:
            print("No se encontraron tendencias para el proyecto.")
            return 0
        hjTrends = hjTrends.rename(columns={"promedio": "Cantidad", "palabra": "Palabra"})
        # Normalizar a numérico
        hjTrends["Cantidad"] = (
            hjTrends["Cantidad"].astype(str).str.replace(",", ".", regex=False)
        )
        hjTrends["Cantidad"] = pd.to_numeric(hjTrends["Cantidad"], errors="coerce").fillna(0)
    else:
        if data is None or "GoogleTrendsBase" not in data:
            print("No se encontró la hoja 'GoogleTrendsBase' en el Excel.")
            return 0
        hjTrendsBase = data["GoogleTrendsBase"]
        hjTrends = pd.DataFrame(extraer_datos_tabla("palabrasTrends"))

    # 🔧 Normalizar columna 'Cantidad'
    hjTrends["Cantidad"] = hjTrends["Cantidad"].astype(str).str.replace(",", ".", regex=False)
    hjTrends["Cantidad"] = pd.to_numeric(hjTrends["Cantidad"], errors="coerce")

    # Extraer palabras trends base segun id
    if "ID Carrera" in hjTrendsBase.columns:
        palabrasCarreraBase = hjTrendsBase.loc[hjTrendsBase["ID Carrera"] == idCarrera]
    else:
        palabrasCarreraBase = hjTrendsBase

    # Obtener el promedio de los 6 valores más altos de la columna 'Cantidad'
    promedio_basePalabras = palabrasCarreraBase["Cantidad"].nlargest(6).mean()
    promedio_consultaPalabras = hjTrends["Cantidad"].nlargest(6).mean()

    # Sumar los promedios
    if promedio_basePalabras != 0:
        promedioTrends = round(((promedio_consultaPalabras * TRENDS) / promedio_basePalabras) * 100, 2)
    else:
        promedioTrends = 0

    # --- CALCULO TOTAL ---
    # Suma promedios plataformas semrush y trends

    if promedioSemrush >= 15:
        promedioSemrush = 15

    if promedioTrends >= 20:
        promedioTrends = 20

    resBusqueda = round(promedioSemrush + promedioTrends, 2)

    return resBusqueda
