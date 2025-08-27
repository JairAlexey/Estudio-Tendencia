from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from scrapers.linkedin_modules.linkedin_project import buscar_proyecto_en_pagina

def paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO=1, TIEMPO_ESPERA_MEDIO=2):
    """
    Busca la carpeta en la página actual y en todas las páginas de paginación.
    Devuelve True si la carpeta fue encontrada y navega a ella.
    """
    encontrada = buscar_carpeta_en_pagina(driver, carpeta_buscar)
    if encontrada:
        return True

    try:
        paginacion_carpetas = driver.find_elements(
            By.CSS_SELECTOR,
            ".saved-folders-layout .artdeco-pagination ul.artdeco-pagination__pages li",
        )
    except:
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
                if buscar_carpeta_en_pagina(driver, carpeta_buscar):
                    return True
            except Exception as e:
                print("⚠️ Error al cambiar página de carpetas:", e)
                continue
    return False

def paginar_y_buscar_proyecto(driver, proyecto_buscar, UBICACIONES, carpeta_buscar, resultados_finales, buscar_proyecto_en_pagina, extraer_datos_reporte, TIEMPO_ESPERA_CORTO=1, TIEMPO_ESPERA_PAGINA=3):
    """
    Busca el proyecto en la página actual y en todas las páginas de paginación.
    Devuelve True si el proyecto fue encontrado y procesado.
    """
    proyecto_encontrado = buscar_proyecto_en_pagina(
        driver, proyecto_buscar, UBICACIONES, carpeta_buscar, resultados_finales, extraer_datos_reporte
    )
    if proyecto_encontrado:
        return True

    try:
        paginacion_reports = driver.find_elements(
            By.CSS_SELECTOR,
            "div.artdeco-models-table-pagination__pagination-cmpt ul.artdeco-pagination__pages li",
        )
    except Exception as e:
        print("❌ Error al localizar la sección de reportes:", e)
        paginacion_reports = []

    if paginacion_reports:
        num_pag = len(paginacion_reports)
        for i in range(num_pag):
            paginacion_reports = driver.find_elements(
                By.CSS_SELECTOR,
                "div.artdeco-models-table-pagination__pagination-cmpt ul.artdeco-pagination__pages li",
            )
            li = paginacion_reports[i]
            class_attr = li.get_attribute("class")
            if class_attr and "selected" in class_attr:
                continue
            try:
                btn = li.find_element(By.TAG_NAME, "button")
                ActionChains(driver).move_to_element(btn).click().perform()
                time.sleep(TIEMPO_ESPERA_CORTO)
                if buscar_proyecto_en_pagina(
                    driver,
                    proyecto_buscar,
                    UBICACIONES,
                    carpeta_buscar,
                    resultados_finales,
                    extraer_datos_reporte
                ):
                    return True
            except Exception as e:
                print("⚠️ Error al cambiar página de reportes:", e)
                continue
    return False

def reintentar_elementos_fallidos(driver, elementos_fallidos, url, UBICACIONES, buscar_carpeta_en_pagina, buscar_proyecto_en_pagina, extraer_datos_reporte, TIEMPO_ESPERA_CORTO=1, TIEMPO_ESPERA_MEDIO=2, TIEMPO_ESPERA_PAGINA=3):
    """
    Reintenta procesar los elementos fallidos (carpetas/proyectos) recorriendo la paginación.
    """
    if not elementos_fallidos:
        return

    print(f"\n🔄 REINTENTANDO {len(elementos_fallidos)} elemento(s) que fallaron:")
    for i, fallido in enumerate(elementos_fallidos.copy(), 1):
        elemento = fallido['elemento']
        carpeta_buscar = fallido['carpeta']
        proyecto_buscar = fallido['proyecto']
        razon = fallido['razon']

        print(f"\n🔄 Reintento {i}/{len(elementos_fallidos)}: {carpeta_buscar} -> {proyecto_buscar}")
        print(f"   Razón del fallo anterior: {razon}")

        driver.get(url)
        time.sleep(TIEMPO_ESPERA_MEDIO)

        encontrada = paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO)
        if not encontrada:
            print(f"❌ Reintento fallido: Carpeta '{carpeta_buscar}' sigue sin encontrarse")
            continue

        proyecto_encontrado = paginar_y_buscar_proyecto(
            driver, proyecto_buscar, UBICACIONES, carpeta_buscar, fallido.get('resultados_finales', []),
            buscar_proyecto_en_pagina, extraer_datos_reporte, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_PAGINA
        )
        if proyecto_encontrado:
            print(f"✅ Reintento exitoso: '{proyecto_buscar}' procesado correctamente")
            elementos_fallidos.remove(fallido)
        else:
            print(f"❌ Reintento fallido: '{proyecto_buscar}' sigue sin encontrarse")
