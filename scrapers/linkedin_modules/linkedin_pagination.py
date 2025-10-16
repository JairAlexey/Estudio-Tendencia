from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from scrapers.linkedin_modules.linkedin_project import buscar_proyecto_en_pagina

def paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO=3, TIEMPO_ESPERA_MEDIO=5):
    """
    Busca la carpeta en la página actual y en todas las páginas de paginación.
    Devuelve True si la carpeta fue encontrada y navega a ella.
    """
    # Agregar espera adicional para carga inicial
    time.sleep(TIEMPO_ESPERA_MEDIO * 2)
    try:
        encontrada = buscar_carpeta_en_pagina(driver, carpeta_buscar)
    except Exception as e:
        print(f"Error buscando carpeta en página: {e}")
        encontrada = False
    if encontrada:
        return True

    try:
        # Espera explícita por la paginación
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                ".saved-folders-layout .artdeco-pagination ul.artdeco-pagination__pages li"
            ))
        )
        paginacion_carpetas = driver.find_elements(
            By.CSS_SELECTOR,
            ".saved-folders-layout .artdeco-pagination ul.artdeco-pagination__pages li",
        )
    except Exception as e:
        print(f"Error localizando paginación de carpetas: {e}")
        paginacion_carpetas = []

    if paginacion_carpetas:
        for li in paginacion_carpetas:
            class_attr = li.get_attribute("class")
            if class_attr and "selected" in class_attr:
                continue
            try:
                btn = li.find_element(By.TAG_NAME, "button")
                ActionChains(driver).move_to_element(btn).click().perform()
                time.sleep(TIEMPO_ESPERA_CORTO)
                try:
                    if buscar_carpeta_en_pagina(driver, carpeta_buscar):
                        return True
                except Exception as e:
                    print(f"Error buscando carpeta tras paginación: {e}")
            except Exception as e:
                print("Error al cambiar página de carpetas:", e)
                continue
    return False

def paginar_y_buscar_proyecto(driver, proyecto_buscar, UBICACIONES, carpeta_buscar, resultados_finales, 
                            buscar_proyecto_en_pagina, extraer_datos_reporte, TIEMPO_ESPERA_CORTO=3, 
                            TIEMPO_ESPERA_PAGINA=6, proyecto_id=None, tipo=None):
    """
    Busca el proyecto en la página actual y en todas las páginas de paginación.
    """
    try:
        proyecto_encontrado = buscar_proyecto_en_pagina(
            driver, proyecto_buscar, UBICACIONES, carpeta_buscar, 
            resultados_finales, extraer_datos_reporte, proyecto_id, tipo
        )
    except Exception as e:
        print(f"Error en buscar_proyecto_en_pagina: {e}")
        proyecto_encontrado = False
    if proyecto_encontrado:
        return True

    try:
        paginacion_reports = driver.find_elements(
            By.CSS_SELECTOR,
            "div.artdeco-models-table-pagination__pagination-cmpt ul.artdeco-pagination__pages li",
        )
    except Exception as e:
        print("Error al localizar la sección de reportes:", e)
        paginacion_reports = []

    if paginacion_reports:
        num_pag = len(paginacion_reports)
        for i in range(num_pag):
            paginacion_reports = driver.find_elements(
                By.CSS_SELECTOR,
                "div.artdeco-models-table-pagination__pagination-cmpt ul.artdeco-pagination__pages li",
            )
            if not paginacion_reports or i >= len(paginacion_reports):
                print(f"Índice {i} fuera de rango para paginacion_reports (tamaño: {len(paginacion_reports)})")
                break
            li = paginacion_reports[i]
            class_attr = li.get_attribute("class")
            if class_attr and "selected" in class_attr:
                continue
            try:
                btn = li.find_element(By.TAG_NAME, "button")
                ActionChains(driver).move_to_element(btn).click().perform()
                time.sleep(TIEMPO_ESPERA_CORTO)
                try:
                    if buscar_proyecto_en_pagina(
                        driver,
                        proyecto_buscar,
                        UBICACIONES,
                        carpeta_buscar,
                        resultados_finales,
                        extraer_datos_reporte,
                        proyecto_id,
                        tipo
                    ):
                        return True
                except Exception as e:
                    print(f"Error en buscar_proyecto_en_pagina tras paginación: {e}")
            except Exception as e:
                print("Error al cambiar página de reportes:", e)
                continue
    return False

def reintentar_elementos_fallidos(
    driver, elementos_fallidos, url, UBICACIONES,
    buscar_carpeta_en_pagina, buscar_proyecto_en_pagina, extraer_datos_reporte,
    TIEMPO_ESPERA_CORTO=3, TIEMPO_ESPERA_MEDIO=5, TIEMPO_ESPERA_PAGINA=6,
    proyecto_id=None, tipo=None
):
    """
    Reintenta procesar los elementos fallidos (carpetas/proyectos) recorriendo la paginación.
    """
    if not elementos_fallidos:
        print("No hay elementos fallidos para reintentar.")
        return

    print(f"\nREINTENTANDO {len(elementos_fallidos)} elemento(s) que fallaron:")
    for i, fallido in enumerate(elementos_fallidos.copy(), 1):
        elemento = fallido.get('elemento', {})
        carpeta_buscar = fallido.get('carpeta', '')
        proyecto_buscar = fallido.get('proyecto', '')
        razon = fallido.get('razon', '')

        print(f"\nReintento {i}/{len(elementos_fallidos)}: {carpeta_buscar} -> {proyecto_buscar}")
        print(f"   Razón del fallo anterior: {razon}")

        try:
            driver.get(url)
            time.sleep(TIEMPO_ESPERA_MEDIO)
        except Exception as e:
            print(f"Error navegando a url en reintento: {e}")
            continue

        try:
            encontrada = paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO)
        except Exception as e:
            print(f"Error en paginar_y_buscar_carpeta durante reintento: {e}")
            encontrada = False
        if not encontrada:
            print(f"Reintento fallido: Carpeta '{carpeta_buscar}' sigue sin encontrarse")
            continue

        try:
            proyecto_encontrado = buscar_proyecto_en_pagina(
                driver, proyecto_buscar, UBICACIONES, carpeta_buscar, 
                [], extraer_datos_reporte, proyecto_id, tipo
            )
        except Exception as e:
            print(f"Error en buscar_proyecto_en_pagina durante reintento: {e}")
            proyecto_encontrado = False
        if proyecto_encontrado:
            print(f"Reintento exitoso: '{proyecto_buscar}' procesado correctamente")
            elementos_fallidos.remove(fallido)
        else:
            print(f"Reintento fallido: '{proyecto_buscar}' sigue sin encontrarse")
