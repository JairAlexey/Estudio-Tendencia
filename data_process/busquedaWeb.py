import pandas as pd
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla, obtener_id_carrera

SEMRUSH = 0.15
TRENDS = 0.20

def calc_busquedaWeb(proyecto_id):
    try:
        print(f"[BusquedaWeb] Calculando desde base de datos (proyecto_id={proyecto_id})")

        # Obtener datos del proyecto
        proyecto_data = extraer_datos_tabla("reporteLinkedin", proyecto_id)
        if not proyecto_data:
            print("ERROR: No se pudo obtener datos del proyecto.")
            return 0

        carrera_referencia = proyecto_data[0].get("ProyectoReferencia")
        print(f"Carrera de referencia: {carrera_referencia}")

        # Obtener ID Carrera referencia
        try:
            idCarrera = obtener_id_carrera(carrera_referencia)
            print(f"ID Carrera: {idCarrera}")
        except ValueError as e:
            print(f"ERROR: {e}")
            return 0

        # --- SEMRUSH ---
        # Obtener datos base de Semrush para la carrera referencia
        from conexion import conn, cursor
        cursor.execute("""
            SELECT Vision_General, Palabras, Volumen 
            FROM semrush_base 
            WHERE ID_Carrera = %s
        """, (idCarrera,))
        semrush_base_row = cursor.fetchone()
        
        if not semrush_base_row:
            print(f"ERROR: No se encontraron datos base de Semrush para ID_Carrera {idCarrera}")
            return 0

        # Obtener datos de consulta de Semrush para este proyecto
        semrush_consulta = extraer_datos_tabla("semrush", proyecto_id)
        if not semrush_consulta:
            print("ERROR: No se encontraron datos de Semrush para el proyecto")
            return 0

        # Datos base
        visionGeneralBase = float(semrush_base_row[0])
        palabrasBase = float(semrush_base_row[1])
        volumenBase = float(semrush_base_row[2])

        # Datos consulta
        vision_general_str = semrush_consulta[0].get("visiongeneral", "0")
        # Extraer número de la cadena si está en formato de cadena
        try:
            visionGeneralConsulta = float(vision_general_str.replace(",", "").replace(" ", ""))
        except (ValueError, AttributeError):
            visionGeneralConsulta = 0.0
            
        palabrasConsulta = float(semrush_consulta[0].get("palabras", 0))
        volumenConsulta = float(semrush_consulta[0].get("volumen", 0))

        print(f"Semrush Base - Visión: {visionGeneralBase}, Palabras: {palabrasBase}, Volumen: {volumenBase}")
        print(f"Semrush Consulta - Visión: {visionGeneralConsulta}, Palabras: {palabrasConsulta}, Volumen: {volumenConsulta}")

        # Calculos Semrush
        resVisionGeneral = ((visionGeneralConsulta * SEMRUSH) / visionGeneralBase) * 100 if visionGeneralBase != 0 else 0
        resPalabras = ((palabrasConsulta * SEMRUSH) / palabrasBase) * 100 if palabrasBase != 0 else 0
        resVolumen = ((volumenConsulta * SEMRUSH) / volumenBase) * 100 if volumenBase != 0 else 0

        promedioSemrush = round((resVisionGeneral + resPalabras + resVolumen) / 3, 2)
        print(f"Promedio Semrush: {promedioSemrush}")

        # --- GOOGLE TRENDS ---
        # Obtener datos base de Trends para la carrera referencia
        cursor.execute("""
            SELECT Cantidad 
            FROM tendencias_carrera 
            WHERE ID_Carrera = %s
            ORDER BY Cantidad DESC
            LIMIT 6
        """, (idCarrera,))
        trends_base_rows = cursor.fetchall()
        
        if not trends_base_rows:
            print(f"ERROR: No se encontraron datos base de Trends para ID_Carrera {idCarrera}")
            return 0

        # Obtener datos de consulta de Trends para este proyecto
        trends_consulta = extraer_datos_tabla("tendencias", proyecto_id)
        if not trends_consulta:
            print("ERROR: No se encontraron datos de Trends para el proyecto")
            return 0

        # Calcular promedios
        promedio_basePalabras = sum([float(row[0]) for row in trends_base_rows]) / len(trends_base_rows)
        
        # Obtener los 6 valores más altos de consulta
        valores_consulta = [float(item.get("promedio", 0)) for item in trends_consulta]
        valores_consulta_top6 = sorted(valores_consulta, reverse=True)[:6]
        promedio_consultaPalabras = sum(valores_consulta_top6) / len(valores_consulta_top6) if valores_consulta_top6 else 0

        print(f"Trends Base - Promedio top 6: {promedio_basePalabras}")
        print(f"Trends Consulta - Promedio top 6: {promedio_consultaPalabras}")

        promedioTrends = round(((promedio_consultaPalabras * TRENDS) / promedio_basePalabras) * 100, 2) if promedio_basePalabras != 0 else 0
        print(f"Promedio Trends: {promedioTrends}")

        # --- CALCULO TOTAL ---
        if promedioSemrush >= 15:
            promedioSemrush = 15

        if promedioTrends >= 20:
            promedioTrends = 20

        resBusqueda = round(promedioSemrush + promedioTrends, 2)
        print(f"Resultado final búsqueda web: {resBusqueda}")

        return resBusqueda
        
    except Exception as e:
        print(f"ERROR en calc_busquedaWeb: {e}")
        return 0
