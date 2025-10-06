import pandas as pd
import os
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla

ECU = 0.15
LATAM = 0.10

def calc_linkedin(proyecto_id):
    print(f"[LinkedIn] Calculando desde base de datos (proyecto_id={proyecto_id})")
    
    try:
        # Obtener datos desde la base de datos
        data = extraer_datos_tabla("linkedin", proyecto_id)
        if not data:
            print("ERROR: No se encontraron datos de LinkedIn en la base de datos.")
            return 0

        df = pd.DataFrame(data)
        print(f"[DEBUG] DataFrame LinkedIn shape: {df.shape}")
        print(f"[DEBUG] Columnas disponibles: {df.columns.tolist()}")

        # Verificar que tenemos los datos necesarios
        required_regions = ["Ecuador", "América Latina"]
        required_types = ["Referencia", "Estudio"]
        
        for region in required_regions:
            for tipo in required_types:
                subset = df[(df["region"] == region) & (df["tipo"] == tipo)]
                if subset.empty:
                    print(f"ERROR: Falta datos para {region} - {tipo}")
                    return 0

        # ECUADOR
        filtroEC = df["region"] == "Ecuador"
        data_ecuador = df[filtroEC]


        data_ecuadorRef = data_ecuador.loc[data_ecuador["tipo"] == "Referencia"].reset_index(drop=True)
        data_ecuadorCon = data_ecuador.loc[data_ecuador["tipo"] == "Estudio"].reset_index(drop=True)

        # Convertir todos los valores a float
        profesionalesRefEc = float(data_ecuadorRef["profesionales"][0])
        empleoRefEc = float(data_ecuadorRef["anunciosempleo"][0])
        if empleoRefEc is None or empleoRefEc == 0:
            empleoRefEc = 1
        anuncios_profesionalesRefEc = float(data_ecuadorRef["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesRefEc is None or anuncios_profesionalesRefEc == 0:
            anuncios_profesionalesRefEc = 1

        profesionalesConEc = float(data_ecuadorCon["profesionales"][0])
        empleoConEc = float(data_ecuadorCon["anunciosempleo"][0])
        if empleoConEc is None or empleoConEc == 0:
            empleoConEc = 1
        anuncios_profesionalesConEc = float(data_ecuadorCon["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesConEc is None or anuncios_profesionalesConEc == 0:
            anuncios_profesionalesConEc = 1

        resProfesionalesEc = ((profesionalesConEc * ECU) / profesionalesRefEc) * 100
        resEmpleoEc = ((empleoConEc * ECU) / empleoRefEc) * 100
        resAnunEmpEc = ((anuncios_profesionalesConEc * ECU) / anuncios_profesionalesRefEc) * 100

        resPromedioEc = round((resProfesionalesEc + resEmpleoEc + resAnunEmpEc) / 3, 2)

        # LATAM
        filtroLATAM = df["region"] == "América Latina"
        data_latam = df[filtroLATAM]

        data_latamRef = data_latam.loc[data_latam["tipo"] == "Referencia"].reset_index(drop=True)
        data_latamCon = data_latam.loc[data_latam["tipo"] == "Estudio"].reset_index(drop=True)

        profesionalesRefLat = float(data_latamRef["profesionales"][0])
        empleoRefLat = float(data_latamRef["anunciosempleo"][0])
        if empleoRefLat is None or empleoRefLat == 0:
            empleoRefLat = 1
        anuncios_profesionalesRefLat = float(data_latamRef["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesRefLat is None or anuncios_profesionalesRefLat == 0:
            anuncios_profesionalesRefLat = 1

        profesionalesConLat = float(data_latamCon["profesionales"][0])
        empleoConLat = float(data_latamCon["anunciosempleo"][0])
        if empleoConLat is None or empleoConLat == 0:
            empleoConLat = 1
        anuncios_profesionalesConLat = float(data_latamCon["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesConLat is None or anuncios_profesionalesConLat == 0:
            anuncios_profesionalesConLat = 1

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
    
    except Exception as e:
        print(f"ERROR en calc_linkedin: {e}")
        return 0
