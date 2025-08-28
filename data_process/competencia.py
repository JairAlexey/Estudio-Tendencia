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


def calc_competencia_virtual(source=None):
    if isinstance(source, int):
        print(f"[Competencia Virtual] Fuente: Base de Datos (proyecto_id={source})")
    else:
        print(f"[Competencia Virtual] Fuente: Excel")
    # Calculo busqueda web (DB si source es int)
    busquedaWeb = calc_busquedaWeb(source)
    
    # Extrayendo ofertas: usar DB tabla modalidad_oferta si source es int
    if isinstance(source, int):
        dataOfertas = extraer_datos_tabla("modalidad_oferta", source)
    else:
        dataOfertas = []

    # oferta virtual
    if not dataOfertas:
        print("No se encontraron datos de ofertas (virtual). Retornando 0.")
        return 0
    fila = dataOfertas[0]
    competencia_virtual = fila.get("virtual") or fila.get("Virtualidad") or 0

    try:
        competencia_virtual_f = float(str(competencia_virtual).replace(',', '.'))
    except Exception:
        competencia_virtual_f = 0.0
    try:
        busquedaWeb_f = float(str(busquedaWeb).replace(',', '.')) if busquedaWeb is not None else 0.0
    except Exception:
        busquedaWeb_f = 0.0
    resVirtual = obtener_resultado(busquedaWeb_f, competencia_virtual_f)

    if resVirtual >= 25:
        resVirtual = 25

    return resVirtual


def calc_competencia_presencial(source=None):
    if isinstance(source, int):
        print(f"[Competencia Presencial] Fuente: Base de Datos (proyecto_id={source})")
    else:
        print(f"[Competencia Presencial] Fuente: Excel")
    # Calculo busqueda web (DB si source es int)
    busquedaWeb = calc_busquedaWeb(source)
    
    # Extrayendo ofertas
    if isinstance(source, int):
        dataOfertas = extraer_datos_tabla("modalidad_oferta", source)
    else:
        dataOfertas = []

    # oferta presencial
    if not dataOfertas:
        print("No se encontraron datos de ofertas (presencial). Retornando 0.")
        return 0
    fila = dataOfertas[0]
    competencia_presencial = fila.get("presencial") or fila.get("Presencialidad") or 0

    try:
        competencia_presencial_f = float(str(competencia_presencial).replace(',', '.'))
    except Exception:
        competencia_presencial_f = 0.0
    try:
        busquedaWeb_f = float(str(busquedaWeb).replace(',', '.')) if busquedaWeb is not None else 0.0
    except Exception:
        busquedaWeb_f = 0.0
    resPresencial = obtener_resultado(busquedaWeb_f, competencia_presencial_f)

    if resPresencial >= 25:
        resPresencial = 25

    return resPresencial
