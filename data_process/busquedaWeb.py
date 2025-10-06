import pandas as pd
from scrapers.linkedin_modules.linkedin_database import (
    obtener_id_carrera,
    extraer_datos_tabla,
    obtener_semrush_base_por_id,
    obtener_trends_base_por_id,
)

SEMRUSH = 0.15
TRENDS = 0.20

def calc_busquedaWeb(proyecto_id):
    if not isinstance(proyecto_id, int):
        print("ERROR: calc_busquedaWeb ahora solo acepta proyecto_id (int)")
        return 0

    print(f"[Búsqueda Web] Fuente: Base de Datos (proyecto_id={proyecto_id})")
    
    # Extraer carrera referencia desde DB
    filas_ref = extraer_datos_tabla("reporteLinkedin", proyecto_id)
    if not filas_ref:
        print("No se pudo obtener la carrera de referencia (reporteLinkedin vacío).")
        return 0
    carreraReferencia = filas_ref[0].get("ProyectoReferencia")
    print(f"[DEBUG] Carrera referencia obtenida: {carreraReferencia}")
    
    if not carreraReferencia:
        print("No se pudo obtener la carrera de referencia.")
        return 0

    # Obtener ID Carrera referencia
    idCarrera = obtener_id_carrera(carreraReferencia)
    print(f"[DEBUG] ID Carrera obtenido: {idCarrera}")

    # --- SEMRUSH ---
    try:
        semrush_base_dict = obtener_semrush_base_por_id(idCarrera)
        print(f"[DEBUG] Semrush base dict: {semrush_base_dict}")
    except Exception as e:
        print(f"No se pudo obtener semrush_base: {e}")
        return 0
    
    semrush_consulta_rows = extraer_datos_tabla("semrush", proyecto_id)
    print(f"[DEBUG] Semrush consulta rows: {semrush_consulta_rows}")
    if not semrush_consulta_rows:
        print("No se encontraron datos de semrush para el proyecto.")
        return 0
    
    # Buscar la primera fila con datos válidos (no todos ceros)
    fila_valida = None
    for i, fila in enumerate(semrush_consulta_rows):
        vision_val = fila.get('VisionGeneral', 0)
        palabras_val = fila.get('Palabras', 0)
        volumen_val = fila.get('Volumen', 0)
        
        # Convertir a numérico para verificar
        try:
            vision_num = float(str(vision_val).replace(',', '.')) if vision_val else 0
            palabras_num = float(str(palabras_val).replace(',', '.')) if palabras_val else 0
            volumen_num = float(str(volumen_val).replace(',', '.')) if volumen_val else 0
            
            # Si al menos uno de los valores no es cero, usar esta fila
            if vision_num > 0 or palabras_num > 0 or volumen_num > 0:
                fila_valida = fila
                print(f"[DEBUG] Usando fila {i} de semrush (tiene datos válidos): vision={vision_num}, palabras={palabras_num}, volumen={volumen_num}")
                break
        except:
            continue
    
    if not fila_valida:
        print("ERROR: No se encontró ninguna fila válida en semrush (todas son cero)")
        return 0
    
    hjSemrushBase = pd.DataFrame([{
        'visiongeneral': semrush_base_dict.get('VisionGeneral', 0),
        'palabras': semrush_base_dict.get('Palabras', 0),
        'volumen': semrush_base_dict.get('Volumen', 0),
        'id_carrera': idCarrera,
    }])
    hjSemrush = pd.DataFrame([{
        'visiongeneral': fila_valida.get('VisionGeneral', 0),
        'palabras': fila_valida.get('Palabras', 0),
        'volumen': fila_valida.get('Volumen', 0),
    }])
    print(f"[DEBUG] hjSemrushBase DataFrame:\n{hjSemrushBase}")
    print(f"[DEBUG] hjSemrush DataFrame:\n{hjSemrush}")
    
    # Normalizar a numérico
    for col in ['visiongeneral', 'palabras', 'volumen']:
        hjSemrushBase[col] = pd.to_numeric(hjSemrushBase[col], errors='coerce').fillna(0)
        hjSemrush[col] = pd.to_numeric(hjSemrush[col], errors='coerce').fillna(0)

    # --- CALCULO SEMRUSH ---
    datosSemrushCarrera_dict = hjSemrushBase[['visiongeneral', 'palabras', 'volumen']].iloc[0].to_dict()
    print(f"[DEBUG] Datos Semrush carrera dict: {datosSemrushCarrera_dict}")

    # Guardar en un diccionario datos semrush consultados
    datosSemrushConsulta_dict = hjSemrush.iloc[0].to_dict()
    print(f"[DEBUG] Datos Semrush consulta dict: {datosSemrushConsulta_dict}")

    # Calculos
    # Vision general
    visionGeneralBase = datosSemrushCarrera_dict['visiongeneral']
    visionGeneralConsulta = datosSemrushConsulta_dict['visiongeneral']
    print(f"[DEBUG] Visión General - Base: {visionGeneralBase}, Consulta: {visionGeneralConsulta}")

    if visionGeneralBase != 0:
        resVisionGeneral = ((visionGeneralConsulta * SEMRUSH) / visionGeneralBase) * 100
    else:
        resVisionGeneral = 0
    print(f"[DEBUG] Resultado Visión General: {resVisionGeneral}")

    # Palabras
    palabrasBase = datosSemrushCarrera_dict['palabras']
    palabrasConsulta = datosSemrushConsulta_dict['palabras']
    print(f"[DEBUG] Palabras - Base: {palabrasBase}, Consulta: {palabrasConsulta}")

    if palabrasBase != 0:
        resPalabras = ((palabrasConsulta * SEMRUSH) / palabrasBase) * 100
    else:
        resPalabras = 0
    print(f"[DEBUG] Resultado Palabras: {resPalabras}")

    # Volumen
    volumenBase = datosSemrushCarrera_dict['volumen']
    volumenConsulta = datosSemrushConsulta_dict['volumen']
    print(f"[DEBUG] Volumen - Base: {volumenBase}, Consulta: {volumenConsulta}")

    if volumenBase != 0:
        resVolumen = ((volumenConsulta * SEMRUSH) / volumenBase) * 100
    else:
        resVolumen = 0
    print(f"[DEBUG] Resultado Volumen: {resVolumen}")

    # Calcular el promedio de las 3 columnas
    promedioSemrush = round(((resVisionGeneral + resPalabras + resVolumen) / 3), 2)
    print(f"[DEBUG] Promedio Semrush: {promedioSemrush}")

    # --- TRENDS ---
    try:
        trends_base_rows = obtener_trends_base_por_id(idCarrera)
        print(f"[DEBUG] Trends base rows: {trends_base_rows}")
    except Exception as e:
        print(f"No se pudo obtener tendencias base: {e}")
        return 0
    
    hjTrendsBase = pd.DataFrame(trends_base_rows)
    hjTrendsBase = hjTrendsBase.rename(columns={"Palabra": "Palabra", "Cantidad": "Cantidad"})
    hjTrends = pd.DataFrame(extraer_datos_tabla("tendencias", proyecto_id))
    print(f"[DEBUG] Trends consulta: {extraer_datos_tabla('tendencias', proyecto_id)}")
    if hjTrends.empty:
        print("No se encontraron tendencias para el proyecto.")
        return 0
    hjTrends = hjTrends.rename(columns={"promedio": "Cantidad", "palabra": "Palabra"})
    
    # Normalizar a numérico
    hjTrends["Cantidad"] = (
        hjTrends["Cantidad"].astype(str).str.replace(",", ".", regex=False)
    )
    hjTrends["Cantidad"] = pd.to_numeric(hjTrends["Cantidad"], errors="coerce").fillna(0)

    # Extraer palabras trends base segun id
    if "ID Carrera" in hjTrendsBase.columns:
        palabrasCarreraBase = hjTrendsBase.loc[hjTrendsBase["ID Carrera"] == idCarrera]
    else:
        palabrasCarreraBase = hjTrendsBase

    # Obtener el promedio de los 6 valores más altos de la columna 'Cantidad'
    promedio_basePalabras = palabrasCarreraBase["Cantidad"].nlargest(6).mean()
    promedio_consultaPalabras = hjTrends["Cantidad"].nlargest(6).mean()
    print(f"[DEBUG] Promedio base palabras: {promedio_basePalabras}")
    print(f"[DEBUG] Promedio consulta palabras: {promedio_consultaPalabras}")

    # Sumar los promedios
    if promedio_basePalabras != 0:
        promedioTrends = round(((promedio_consultaPalabras * TRENDS) / promedio_basePalabras) * 100, 2)
    else:
        promedioTrends = 0
    print(f"[DEBUG] Promedio Trends: {promedioTrends}")

    # --- CALCULO TOTAL ---
    # Suma promedios plataformas semrush y trends
    print(f"[DEBUG] Antes de límites - Semrush: {promedioSemrush}, Trends: {promedioTrends}")

    if promedioSemrush >= 15:
        promedioSemrush = 15

    if promedioTrends >= 20:
        promedioTrends = 20

    print(f"[DEBUG] Después de límites - Semrush: {promedioSemrush}, Trends: {promedioTrends}")

    resBusqueda = round(promedioSemrush + promedioTrends, 2)
    print(f"[DEBUG] RESULTADO FINAL BÚSQUEDA WEB: {resBusqueda}")

    return resBusqueda
