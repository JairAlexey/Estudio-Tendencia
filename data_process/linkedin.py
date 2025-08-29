import pandas as pd
import os
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla

ECU = 0.15
LATAM = 0.10

def calc_linkedin(proyecto_id):
    # Obtener datos desde la base de datos
    data = extraer_datos_tabla("linkedin", proyecto_id)
    if not data:
        print("ERROR: No se encontraron datos de LinkedIN en la base de datos.")
        return 0

    df = pd.DataFrame(data)

    # ECUADOR
    filtroEC = df["Region"] == "Ecuador"
    data_ecuador = df[filtroEC]

    data_ecuadorRef = data_ecuador.loc[data_ecuador["Tipo"] == "Referencia"].reset_index(drop=True)
    data_ecuadorCon = data_ecuador.loc[data_ecuador["Tipo"] == "Estudio"].reset_index(drop=True)

    # Convertir todos los valores a float
    profesionalesRefEc = float(data_ecuadorRef["Profesionales"][0])
    empleoRefEc = float(data_ecuadorRef["AnunciosEmpleo"][0])
    anuncios_profesionalesRefEc = float(data_ecuadorRef["PorcentajeAnunciosProfesionales"][0])

    profesionalesConEc = float(data_ecuadorCon["Profesionales"][0])
    empleoConEc = float(data_ecuadorCon["AnunciosEmpleo"][0])
    anuncios_profesionalesConEc = float(data_ecuadorCon["PorcentajeAnunciosProfesionales"][0])

    resProfesionalesEc = ((profesionalesConEc * ECU) / profesionalesRefEc) * 100
    resEmpleoEc = ((empleoConEc * ECU) / empleoRefEc) * 100
    resAnunEmpEc = ((anuncios_profesionalesConEc * ECU) / anuncios_profesionalesRefEc) * 100

    resPromedioEc = round((resProfesionalesEc + resEmpleoEc + resAnunEmpEc) / 3, 2)

    # LATAM
    filtroLATAM = df["Region"] == "América Latina"
    data_latam = df[filtroLATAM]

    data_latamRef = data_latam.loc[data_latam["Tipo"] == "Referencia"].reset_index(drop=True)
    data_latamCon = data_latam.loc[data_latam["Tipo"] == "Estudio"].reset_index(drop=True)

    profesionalesRefLat = float(data_latamRef["Profesionales"][0])
    empleoRefLat = float(data_latamRef["AnunciosEmpleo"][0])
    anuncios_profesionalesRefLat = float(data_latamRef["PorcentajeAnunciosProfesionales"][0])

    profesionalesConLat = float(data_latamCon["Profesionales"][0])
    empleoConLat = float(data_latamCon["AnunciosEmpleo"][0])
    anuncios_profesionalesConLat = float(data_latamCon["PorcentajeAnunciosProfesionales"][0])

    resProfesionalesLat = ((profesionalesConLat * LATAM) / profesionalesRefLat) * 100
    resEmpleoLat = ((empleoConLat * LATAM) / empleoRefLat) * 100
    resAnunEmpLat = ((anuncios_profesionalesConLat * LATAM) / anuncios_profesionalesRefLat) * 100

    resPromedioLat = round((resProfesionalesLat + resEmpleoLat + resAnunEmpLat) / 3, 2)

    if resPromedioEc >= 15:
        resPromedioEc = 15

    if resPromedioLat >= 10:
        resPromedioLat = 10

    promGeneral = resPromedioEc + resPromedioLat

    return promGeneral
