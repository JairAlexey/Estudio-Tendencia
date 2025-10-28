import pandas as pd
import os
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla

ECU = 0.15
LATAM = 0.10

def obtener_ubicaciones_por_tipo_carpeta(proyecto_id):
    from conexion import conn
    cur = conn.cursor()
    cur.execute("SELECT tipo_carpeta FROM proyectos_tendencias WHERE id=%s", (proyecto_id,))
    row = cur.fetchone()
    cur.close()
    if row and row[0] and "pregrado cr" in row[0].lower():
        return ["Costa Rica", "América Latina"]
    else:
        return ["Ecuador", "América Latina"]

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

        required_regions = obtener_ubicaciones_por_tipo_carpeta(proyecto_id)
        required_types = ["Referencia", "Estudio"]
        
        for region in required_regions:
            for tipo in required_types:
                subset = df[(df["region"] == region) & (df["tipo"] == tipo)]
                if subset.empty:
                    print(f"ERROR: Falta datos para {region} - {tipo}")
                    return 0

        # ECUADOR o COSTA RICA
        region1 = required_regions[0]
        filtroR1 = df["region"] == region1
        data_r1 = df[filtroR1]
        data_r1Ref = data_r1.loc[data_r1["tipo"] == "Referencia"].reset_index(drop=True)
        data_r1Con = data_r1.loc[data_r1["tipo"] == "Estudio"].reset_index(drop=True)

        profesionalesRefR1 = float(data_r1Ref["profesionales"][0])
        empleoRefR1 = float(data_r1Ref["anunciosempleo"][0])
        if empleoRefR1 is None or empleoRefR1 == 0:
            empleoRefR1 = 1
        anuncios_profesionalesRefR1 = float(data_r1Ref["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesRefR1 is None or anuncios_profesionalesRefR1 == 0:
            anuncios_profesionalesRefR1 = 1

        profesionalesConR1 = float(data_r1Con["profesionales"][0])
        empleoConR1 = float(data_r1Con["anunciosempleo"][0])
        if empleoConR1 is None or empleoConR1 == 0:
            empleoConR1 = 1
        anuncios_profesionalesConR1 = float(data_r1Con["porcentajeanunciosprofesionales"][0])
        if anuncios_profesionalesConR1 is None or anuncios_profesionalesConR1 == 0:
            anuncios_profesionalesConR1 = 1

        peso_r1 = ECU if region1 == "Ecuador" else LATAM if region1 == "América Latina" else 0.15 if region1 == "Costa Rica" else 0.15
        resProfesionalesR1 = ((profesionalesConR1 * peso_r1) / profesionalesRefR1) * 100
        resEmpleoR1 = ((empleoConR1 * peso_r1) / empleoRefR1) * 100
        resAnunEmpR1 = ((anuncios_profesionalesConR1 * peso_r1) / anuncios_profesionalesRefR1) * 100
        resPromedioR1 = round((resProfesionalesR1 + resEmpleoR1 + resAnunEmpR1) / 3, 2)

        # AMÉRICA LATINA
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

        # Limitar los valores máximos
        if resPromedioR1 >= 15:
            resPromedioR1 = 15
        if resPromedioLat >= 10:
            resPromedioLat = 10

        promGeneral = resPromedioR1 + resPromedioLat
        return promGeneral

    except Exception as e:
        print(f"ERROR en calc_linkedin: {e}")
        return 0
