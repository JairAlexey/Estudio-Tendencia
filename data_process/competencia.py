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
    if not isinstance(proyecto_id, int):
        print("ERROR: calc_competencia_virtual ahora solo acepta proyecto_id (int)")
        return 0

    print(f"[Competencia Virtual] Fuente: Base de Datos (proyecto_id={proyecto_id})")
    
    # Calculo busqueda web
    busquedaWeb = calc_busquedaWeb(proyecto_id)
    print(f"[DEBUG] Valor búsqueda web recibido: {busquedaWeb}")
    
    # Extrayendo ofertas desde DB
    dataOfertas = extraer_datos_tabla("modalidad_oferta", proyecto_id)
    print(f"[DEBUG] Datos ofertas obtenidos: {dataOfertas}")

    # oferta virtual
    if not dataOfertas:
        print("No se encontraron datos de ofertas (virtual). Retornando 0.")
        return 0
    fila = dataOfertas[0]
    competencia_virtual = fila.get("virtual") or fila.get("Virtualidad") or 0
    print(f"[DEBUG] Competencia virtual raw: {competencia_virtual}")

    try:
        competencia_virtual_f = float(str(competencia_virtual).replace(',', '.'))
    except Exception:
        competencia_virtual_f = 0.0
    try:
        busquedaWeb_f = float(str(busquedaWeb).replace(',', '.')) if busquedaWeb is not None else 0.0
    except Exception:
        busquedaWeb_f = 0.0
    
    print(f"[DEBUG] Valores para cálculo - Búsqueda: {busquedaWeb_f}, Competencia: {competencia_virtual_f}")
    resVirtual = obtener_resultado(busquedaWeb_f, competencia_virtual_f)
    print(f"[DEBUG] Resultado inicial virtual: {resVirtual}")

    if resVirtual >= 25:
        resVirtual = 25

    print(f"[DEBUG] RESULTADO FINAL COMPETENCIA VIRTUAL: {resVirtual}")
    return resVirtual


def calc_competencia_presencial(proyecto_id):
    if not isinstance(proyecto_id, int):
        print("ERROR: calc_competencia_presencial ahora solo acepta proyecto_id (int)")
        return 0

    print(f"[Competencia Presencial] Fuente: Base de Datos (proyecto_id={proyecto_id})")
    
    # Calculo busqueda web
    busquedaWeb = calc_busquedaWeb(proyecto_id)
    print(f"[DEBUG] Valor búsqueda web recibido: {busquedaWeb}")
    
    # Extrayendo ofertas desde DB
    dataOfertas = extraer_datos_tabla("modalidad_oferta", proyecto_id)
    print(f"[DEBUG] Datos ofertas obtenidos: {dataOfertas}")

    # oferta presencial
    if not dataOfertas:
        print("No se encontraron datos de ofertas (presencial). Retornando 0.")
        return 0
    fila = dataOfertas[0]
    competencia_presencial = fila.get("presencial") or fila.get("Presencialidad") or 0
    print(f"[DEBUG] Competencia presencial raw: {competencia_presencial}")

    try:
        competencia_presencial_f = float(str(competencia_presencial).replace(',', '.'))
    except Exception:
        competencia_presencial_f = 0.0
    try:
        busquedaWeb_f = float(str(busquedaWeb).replace(',', '.')) if busquedaWeb is not None else 0.0
    except Exception:
        busquedaWeb_f = 0.0
    
    print(f"[DEBUG] Valores para cálculo - Búsqueda: {busquedaWeb_f}, Competencia: {competencia_presencial_f}")
    resPresencial = obtener_resultado(busquedaWeb_f, competencia_presencial_f)
    print(f"[DEBUG] Resultado inicial presencial: {resPresencial}")

    if resPresencial >= 25:
        resPresencial = 25

    print(f"[DEBUG] RESULTADO FINAL COMPETENCIA PRESENCIAL: {resPresencial}")
    return resPresencial
    print(f"[DEBUG] RESULTADO FINAL COMPETENCIA PRESENCIAL: {resPresencial}")
    return resPresencial
