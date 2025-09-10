from selenium.webdriver.common.by import By
import time
from scrapers.linkedin_modules.linkedin_utils import normalizar_texto
import unicodedata

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.upper()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto.strip()

def buscar_proyecto_en_pagina(
    driver, proyecto_buscar, ubicaciones, carpeta_nombre, resultados_finales, extraer_datos_reporte, TIEMPO_ESPERA_MEDIO=2
):
    """
    Recorre las filas (reportes) de la tabla en la página actual.
    Si encuentra el reporte cuyo nombre coincide con 'proyecto_buscar',
    navega a su URL, y para cada ubicación definida llama a extraer_datos_reporte().
    Devuelve True si se encontró y procesó el proyecto.
    """
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
    if rows:
        driver.execute_script("arguments[0].scrollIntoView(true);", rows[0])

    for row in rows:
        try:
            span = row.find_element(
                By.CSS_SELECTOR,
                "td.saved-reports-table__table-cell--display-name a div span",
            )
            texto = span.text.strip()
            print("🔍 Revisando reporte:", texto)
            if normalizar_texto(texto) == normalizar_texto(proyecto_buscar):
                print("Proyecto encontrado:", texto)
                enlace = row.find_element(
                    By.CSS_SELECTOR,
                    "td.saved-reports-table__table-cell--display-name a",
                )
                href = enlace.get_attribute("href")
                print("Navegando a:", href)
                driver.get(href)
                time.sleep(TIEMPO_ESPERA_MEDIO)
                resultados_ubicacion = []
                ubicaciones_exitosas = 0
                for UBICACION in ubicaciones:
                    print(f"\nAplicando ubicación: {UBICACION}")
                    datos = extraer_datos_reporte(
                        driver, UBICACION, carpeta_nombre, texto
                    )
                    if datos:
                        resultados_ubicacion.append(datos)
                        ubicaciones_exitosas += 1
                if resultados_ubicacion:
                    resultados_finales.extend(resultados_ubicacion)
                    if ubicaciones_exitosas < len(ubicaciones):
                        print(f"Solo {ubicaciones_exitosas}/{len(ubicaciones)} ubicaciones procesadas exitosamente para '{texto}'")
                else:
                    print(f"Ninguna ubicación pudo ser procesada para '{texto}'")
                return True
        except Exception as e:
            print("Error revisando fila de reporte:", e)
            continue
    return False
