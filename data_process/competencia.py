import pandas as pd
from data_process.busquedaWeb import calc_busquedaWeb
from scrapers.linkedin_modules.linkedin_database import extraer_datos_tabla

# Calcular resultado para competencia virtual y presencial
def obtener_resultado(busqueda, competencia):
    if busqueda >= 25:
        if competencia < 5:
            return 25
        else:
            return 20
    else:
        if competencia >= 5:
            return 15
        else:
            return 10


def calc_competencia_virtual(proyecto_id):
    try:
        # Cálculo búsqueda web para este proyecto
        busquedaWeb = calc_busquedaWeb(proyecto_id)
        
        # Extrayendo ofertas desde la base de datos
        dataOfertas = extraer_datos_tabla("modalidad_oferta", proyecto_id)
        if not dataOfertas:
            print("ERROR: No se encontraron datos de modalidad_oferta")
            return 0

        # Oferta virtual
        competencia_virtual = int(dataOfertas[0].get("virtual", 0))
        
        resVirtual = obtener_resultado(busquedaWeb, competencia_virtual)
        
        if resVirtual >= 25:
            resVirtual = 25

        print(f"[DEBUG] Competencia virtual - búsqueda: {busquedaWeb}, competencia: {competencia_virtual}, resultado: {resVirtual}")
        return resVirtual
        
    except Exception as e:
        print(f"ERROR en calc_competencia_virtual: {e}")
        return 0


def calc_competencia_presencial(proyecto_id):
    try:
        # Cálculo búsqueda web para este proyecto
        busquedaWeb = calc_busquedaWeb(proyecto_id)
        
        # Extrayendo ofertas desde la base de datos
        dataOfertas = extraer_datos_tabla("modalidad_oferta", proyecto_id)
        if not dataOfertas:
            print("ERROR: No se encontraron datos de modalidad_oferta")
            return 0

        # Oferta presencial  
        competencia_presencial = int(dataOfertas[0].get("presencial", 0))
        
        resPresencial = obtener_resultado(busquedaWeb, competencia_presencial)
        
        if resPresencial >= 25:
            resPresencial = 25

        print(f"[DEBUG] Competencia presencial - búsqueda: {busquedaWeb}, competencia: {competencia_presencial}, resultado: {resPresencial}")
        return resPresencial
        
    except Exception as e:
        print(f"ERROR en calc_competencia_presencial: {e}")
        return 0
