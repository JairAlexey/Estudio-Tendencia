import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def esperar_y_refrescar_si_banner(
    driver, hay_banner_error, esperar_elemento, TIEMPO_ESPERA_BANNER, TIEMPO_ESPERA_PAGINA, TIEMPO_ESPERA_MEDIO, TIEMPO_ESPERA_CORTO,
    max_intentos=3, espera_seg=None, ubicacion=None, re_aplicar_filtro=None
):
    """
    Si aparece el banner, espera `espera_seg` segundos, refresca y reintenta.
    Después de refrescar, verifica y re-aplica el filtro de ubicación si es necesario.
    Devuelve True  -> el banner desapareció (OK para continuar)
             False -> persiste tras `max_intentos` (hay que omitir el reporte)
    """
    if espera_seg is None:
        espera_seg = TIEMPO_ESPERA_BANNER
    intento = 0
    # Si no se pasa una función válida para re_aplicar_filtro, usar una dummy
    if re_aplicar_filtro is None:
        def re_aplicar_filtro(driver, ubicacion):
            print("No hay función de re-aplicación de filtro definida.")
            return False
    while hay_banner_error(driver) and intento < max_intentos:
        intento += 1
        print(f"🔄 Banner error - Refrescando... ({intento}/{max_intentos})")
        time.sleep(espera_seg)
        driver.refresh()
        time.sleep(TIEMPO_ESPERA_PAGINA * 2)
        if hay_banner_error(driver):
            print(f"⚠️ Banner aún presente después del refresh {intento}")
            continue
        filtro_ok = False
        for intento_filtro in range(5):
            div_ubicacion = esperar_elemento(driver, By.CSS_SELECTOR, 'div.query-facet[data-query-type="LOCATION"]', timeout=4)
            if div_ubicacion:
                try:
                    if div_ubicacion.is_displayed() and div_ubicacion.is_enabled():
                        filtro_ok = True
                        break
                except:
                    pass
            time.sleep(TIEMPO_ESPERA_MEDIO)
        if not filtro_ok:
            print(f"❌ Filtro de ubicación no disponible después de refresh {intento}")
            return False
        try:
            time.sleep(TIEMPO_ESPERA_MEDIO)
            boton_borrar = div_ubicacion.find_element(By.CSS_SELECTOR, "button[data-test-clear-all]")
            if boton_borrar and boton_borrar.is_displayed():
                print(f"🧹 Limpiando filtros tras refresh")
                boton_borrar.click()
                time.sleep(TIEMPO_ESPERA_MEDIO)
        except NoSuchElementException:
            try:
                chips_remove = div_ubicacion.find_elements(By.CSS_SELECTOR, "button.facet-pill__remove")
                if chips_remove:
                    print(f"🧹 Limpiando filtros individualmente tras refresh")
                    for chip_remove in chips_remove:
                        if chip_remove.is_displayed():
                            chip_remove.click()
                            time.sleep(0.5)
                else:
                    print(f"ℹ️ No hay filtros que limpiar tras refresh")
            except Exception as e:
                print(f"⚠️ No se pudieron limpiar filtros tras refresh: {e}")
        except Exception as e:
            print(f"⚠️ Error general limpiando filtros tras refresh: {e}")
        if re_aplicar_filtro and ubicacion:
            if hay_banner_error(driver):
                print(f"⚠️ Banner detectado antes de re-aplicar filtro")
                return False
            if not re_aplicar_filtro(driver, ubicacion):
                return False
            time.sleep(TIEMPO_ESPERA_MEDIO)
    return not hay_banner_error(driver)
