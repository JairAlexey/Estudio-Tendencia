import pandas as pd
import os
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla

ECU = 0.15
LATAM = 0.10

def calc_linkedin(source=None):
    """
    Calcula el puntaje LinkedIn a partir de:
    - DB: pasando source como int (proyecto_id)
    - Excel: pasando source como ruta de archivo (str)
    - Variable de entorno EXCEL_PATH si source es None
    """

    # Cargar datos desde DB si se pasa un proyecto_id (int)
    if isinstance(source, int):
        print(f"[LinkedIn] Fuente: Base de Datos (proyecto_id={source})")
        filas = extraer_datos_tabla("linkedin", source)
        if not filas:
            return 0
        # Normalizar a DataFrame con las columnas esperadas del Excel
        df = pd.DataFrame(filas)
        # Compatibilidad de nombres con Excel previo
        df = df.rename(columns={
            "PorcentajeAnunciosProfesionales": "%Anuncios/Profesionales",
            "AnunciosEmpleo": "Anuncios de empleo"
        })
        data = df
    else:
        # Excel: usar source como ruta o EXCEL_PATH
        if source is None:
            archivo = os.getenv("EXCEL_PATH")
        else:
            archivo = source
            print(f"Usando ruta específica: {archivo}")
        print(f"[LinkedIn] Fuente: Excel (archivo={archivo})")
        data = pd.read_excel(archivo, sheet_name='LinkedIn')

    # Validar columnas mínimas
    columnas_requeridas = {"Region", "Tipo", "Profesionales", "Anuncios de empleo", "%Anuncios/Profesionales"}
    if not columnas_requeridas.issubset(set(data.columns)):
        # Faltan columnas: no se puede calcular
        return 0

    # Separar datos por region
    # ECUADOR
    filtroEC = data["Region"] == "Ecuador"
    data_ecuador = data[filtroEC]

    # referencia
    data_ecuadorRef = data_ecuador.loc[data_ecuador["Tipo"] == "Referencia"].reset_index(drop=True)

    # estudio (antes 'Consulta')
    data_ecuadorCon = data_ecuador.loc[data_ecuador["Tipo"] == "Estudio"].reset_index(drop=True)

    if len(data_ecuadorRef) == 0 or len(data_ecuadorCon) == 0:
        return 0

    # CALCULOS ECUADOR
    # Referencia
    # Normalizar numéricos
    for subdf in [data_ecuadorRef, data_ecuadorCon]:
        for col in ["Profesionales", "Anuncios de empleo", "%Anuncios/Profesionales"]:
            if col in subdf.columns:
                subdf[col] = pd.to_numeric(subdf[col], errors='coerce')
    profesionalesRefEc = float(data_ecuadorRef["Profesionales"][0])
    empleoRefEc = float(data_ecuadorRef["Anuncios de empleo"][0])
    anuncios_profesionalesRefEc = float(data_ecuadorRef["%Anuncios/Profesionales"][0])

    # Consulta
    profesionalesConEc = float(data_ecuadorCon["Profesionales"][0])
    empleoConEc = float(data_ecuadorCon["Anuncios de empleo"][0])
    anuncios_profesionalesConEc = float(data_ecuadorCon["%Anuncios/Profesionales"][0])

    # Promedio
    resProfesionalesEc = ((profesionalesConEc * ECU) / profesionalesRefEc) * 100
    resEmpleoEc = ((empleoConEc * ECU) / empleoRefEc) * 100
    resAnunEmpEc = ((anuncios_profesionalesConEc * ECU) / anuncios_profesionalesRefEc) * 100

    resPromedioEc = round((resProfesionalesEc + resEmpleoEc + resAnunEmpEc) / 3, 2)

    # LATAM
    filtroLATAM = data["Region"] == "América Latina"
    data_latam = data[filtroLATAM]

    # referencia
    data_latamRef = data_latam.loc[data_latam["Tipo"] == "Referencia"].reset_index(drop=True)

    # estudio (antes 'Consulta')
    data_latamCon = data_latam.loc[data_latam["Tipo"] == "Estudio"].reset_index(drop=True)

    if len(data_latamRef) == 0 or len(data_latamCon) == 0:
        return 0

    # CALCULOS LATAM
    # Referencia
    for subdf in [data_latamRef, data_latamCon]:
        for col in ["Profesionales", "Anuncios de empleo", "%Anuncios/Profesionales"]:
            if col in subdf.columns:
                subdf[col] = pd.to_numeric(subdf[col], errors='coerce')
    profesionalesRefLat = float(data_latamRef["Profesionales"][0])
    empleoRefLat = float(data_latamRef["Anuncios de empleo"][0])
    anuncios_profesionalesRefLat = float(data_latamRef["%Anuncios/Profesionales"][0])

    # Consulta
    profesionalesConLat = float(data_latamCon["Profesionales"][0])
    empleoConLat = float(data_latamCon["Anuncios de empleo"][0])
    anuncios_profesionalesConLat = float(data_latamCon["%Anuncios/Profesionales"][0])

    # Promedio
    resProfesionalesLat = ((profesionalesConLat * LATAM) / profesionalesRefLat) * 100
    resEmpleoLat = ((empleoConLat * LATAM) / empleoRefLat) * 100
    resAnunEmpLat = (
        (anuncios_profesionalesConLat * LATAM) / anuncios_profesionalesRefLat
    ) * 100

    resPromedioLat = round((resProfesionalesLat + resEmpleoLat + resAnunEmpLat) / 3, 2)

    if resPromedioEc >= 15:
        resPromedioEc = 15

    if resPromedioLat >= 10:
        resPromedioLat = 10

    # Suma promedios
    promGeneral = resPromedioEc + resPromedioLat

    return promGeneral
