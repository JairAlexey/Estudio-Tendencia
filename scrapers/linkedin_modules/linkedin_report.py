import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.linkedin_modules.linkedin_utils import (
    normalizar_texto,
    hay_banner_error,
    esperar_elemento,
)

def extraer_datos_reporte(driver, UBICACION, carpeta_nombre, proyecto_nombre,
                         TIEMPO_ESPERA_CORTO=1, TIEMPO_ESPERA_MEDIO=2, TIEMPO_ESPERA_LARGO=4,
                         TIEMPO_ESPERA_BANNER=40, TIEMPO_ESPERA_PAGINA=3,
                         esperar_resultados_o_banner=None,
                         esperar_y_refrescar_si_banner=None):
    """
    Aplica el filtro de ubicación y extrae los datos (profesionales, anuncios y demanda)
    de la página de un reporte.
    Devuelve un diccionario con los datos extraídos.
    """
    datos = {}
    def aplicar_filtro(driver, UBICACION):
        try:
            # VERIFICACIÓN INICIAL DE BANNER antes de cualquier interacción
            if hay_banner_error(driver):
                print(f"Banner detectado al inicio de aplicar_filtro para '{UBICACION}'")
                return False
            
            div_ubicacion = None
            for _ in range(2):
                try:
                    div_ubicacion = esperar_elemento(driver, By.CSS_SELECTOR, 'div.query-facet[data-query-type="LOCATION"]', timeout=TIEMPO_ESPERA_LARGO)
                    if div_ubicacion:
                        break
                except StaleElementReferenceException:
                    continue
            if not div_ubicacion:
                print("No se encontró el filtro de ubicación para aplicar.")
                return False
            driver.execute_script("arguments[0].scrollIntoView(true);", div_ubicacion)
            time.sleep(TIEMPO_ESPERA_MEDIO)
            
            # VERIFICACIÓN DE BANNER después de localizar elementos
            if hay_banner_error(driver):
                print(f"Banner detectado después de localizar filtro para '{UBICACION}'")
                return False
            # --- Comprobar si la ubicación ya está aplicada ---
            # Verificar solo en la barra de filtros (método más confiable)
            ubicaciones_aplicadas = []
            ub_comparar = normalizar_texto(UBICACION)
            
            print(f"Verificando barra de filtros para '{UBICACION}'...")
            
            # Múltiples intentos para leer elementos de la barra de filtros
            filters_bar_elements = []
            for intento_lectura in range(5):  # Hasta 5 intentos
                try:
                    # Esperar antes de cada intento
                    time.sleep(TIEMPO_ESPERA_MEDIO)
                    
                    filters_bar_elements = driver.find_elements(By.CSS_SELECTOR, 'span.filters-bar__filter-item[data-test-talent-filters-bar-location-filter]')
                    print(f"Intento {intento_lectura + 1}: Encontrados {len(filters_bar_elements)} elementos")
                    
                    if filters_bar_elements:
                        # Verificar si al menos uno tiene texto no vacío
                        elementos_con_texto = 0
                        for elem in filters_bar_elements:
                            try:
                                if elem.text.strip():
                                    elementos_con_texto += 1
                            except:
                                continue
                        
                        if elementos_con_texto > 0:
                            print(f"   {elementos_con_texto} elementos con texto encontrados")
                            break
                        else:
                            print(f"Elementos encontrados pero todos están vacíos, esperando más...")
                            if intento_lectura < 4:  # No esperar en el último intento
                                time.sleep(TIEMPO_ESPERA_LARGO)
                    else:
                        print(f"No se encontraron elementos, esperando más...")
                        if intento_lectura < 4:  # No esperar en el último intento
                            time.sleep(TIEMPO_ESPERA_LARGO)
                            
                except Exception as e:
                    print(f"Error en intento {intento_lectura + 1}: {e}")
                    if intento_lectura < 4:
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                    continue
            
            # Procesar elementos encontrados
            if filters_bar_elements:
                for i, filter_elem in enumerate(filters_bar_elements):
                    try:
                        # Intentar leer el texto con múltiples intentos
                        filter_text = ""
                        for intento_texto in range(3):
                            try:
                                time.sleep(TIEMPO_ESPERA_CORTO)
                                filter_text = filter_elem.text.strip()
                                if filter_text:  # Si encontró texto, salir del loop
                                    break
                                elif intento_texto < 2:  # Si no hay texto, esperar un poco más
                                    time.sleep(TIEMPO_ESPERA_MEDIO)
                            except:
                                if intento_texto < 2:
                                    time.sleep(TIEMPO_ESPERA_MEDIO)
                                continue
                        
                        print(f"   Elemento {i+1}: '{filter_text}'")
                        
                        if filter_text:
                            clean_text = normalizar_texto(filter_text)
                            # Verificar coincidencia exacta con la ubicación buscada
                            if ub_comparar == clean_text:
                                print(f"Coincidencia exacta encontrada: '{filter_text}' = '{UBICACION}'")
                                ubicaciones_aplicadas.append(clean_text)
                            else:
                                print(f"No coincide: '{clean_text}' ≠ '{ub_comparar}'")
                        else:
                            print(f"Elemento {i+1} está vacío después de múltiples intentos")
                            
                    except Exception as e:
                        print(f"Error procesando elemento {i+1}: {e}")
                        continue
            else:
                print(f"No se encontraron elementos de barra de filtros después de múltiples intentos")
            
            # Mostrar filtros detectados para debugging
            if ubicaciones_aplicadas:
                print(f"Filtros aplicados: {ubicaciones_aplicadas}")
            else:
                print(f"Filtros aplicados: [''] (ningún filtro detectado)")
            
            # SIEMPRE limpiar filtros antes de aplicar uno nuevo (excepto si es exactamente el mismo)
            if len(ubicaciones_aplicadas) == 1 and ub_comparar in ubicaciones_aplicadas:
                print(f"Filtro '{UBICACION}' ya aplicado correctamente")
                return True
            else:
                # VERIFICACIÓN DE BANNER antes de limpiar filtros
                if hay_banner_error(driver):
                    print(f"Banner detectado antes de limpiar filtros para '{UBICACION}'")
                    return False
                
                # Limpiar TODOS los filtros existentes
                print(f"Limpiando filtros existentes antes de aplicar '{UBICACION}'")
                try:
                    boton_borrar = div_ubicacion.find_element(By.CSS_SELECTOR, "button[data-test-clear-all]")
                    if boton_borrar and boton_borrar.is_displayed():
                        boton_borrar.click()
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                        print(f"Filtros limpiados")
                except NoSuchElementException:
                    print(f"No se encontró botón de limpiar todo, intentando limpiar individualmente")
                    # Intentar método alternativo: hacer clic en las X de cada chip
                    try:
                        chips_remove = div_ubicacion.find_elements(By.CSS_SELECTOR, "button.facet-pill__remove")
                        if chips_remove:
                            for chip_remove in chips_remove:
                                if chip_remove.is_displayed():
                                    chip_remove.click()
                                    time.sleep(0.5)
                            print(f"Filtros limpiados individualmente")
                        else:
                            print(f"ℹNo hay filtros que limpiar")
                    except Exception as e2:
                        print(f"No se pudieron limpiar filtros individualmente: {e2}")
                except Exception as e:
                    print(f"Error general limpiando filtros: {e}")
                    # Intentar método alternativo: hacer clic en las X de cada chip
                    try:
                        chips_remove = div_ubicacion.find_elements(By.CSS_SELECTOR, "button.facet-pill__remove")
                        if chips_remove:
                            for chip_remove in chips_remove:
                                if chip_remove.is_displayed():
                                    chip_remove.click()
                                    time.sleep(0.5)
                            print(f"Filtros limpiados individualmente")
                    except Exception as e2:
                        print(f"No se pudieron limpiar filtros individualmente: {e2}")
            
            # Asegurar que el input esté limpio y visible
            try:
                btn_mostrar_input = div_ubicacion.find_element(By.CSS_SELECTOR, "button.query-facet__add-button")
                if btn_mostrar_input and btn_mostrar_input.is_displayed():
                    btn_mostrar_input.click()
                    time.sleep(TIEMPO_ESPERA_MEDIO)
            except Exception:
                pass
            
            # VERIFICACIÓN DE BANNER antes de intentar escribir en el campo
            if hay_banner_error(driver):
                print(f"Banner detectado antes de escribir en campo para '{UBICACION}'")
                return False
            
            # Limpiar e ingresar nueva ubicación
            try:
                input_field = div_ubicacion.find_element(By.CSS_SELECTOR, "input.artdeco-typeahead__input")
                if not input_field:
                    print(f"No se encontró el campo de entrada")
                    return False
                
                # Asegurar que el campo esté completamente limpio
                input_field.clear()
                time.sleep(0.5)
                input_field.send_keys(Keys.CONTROL + "a")  # Seleccionar todo
                input_field.send_keys(Keys.DELETE)  # Borrar
                time.sleep(0.5)
                
                print(f"Escribiendo '{UBICACION}' en el campo de ubicación")
                input_field.send_keys(UBICACION)
                time.sleep(TIEMPO_ESPERA_MEDIO)
            except NoSuchElementException:
                print(f"Campo de entrada no encontrado, posible problema de carga de página")
                # Verificar si hay banner que esté causando el problema
                if hay_banner_error(driver):
                    print(f"Banner detectado cuando falta campo de entrada")
                    return False
                # Si no hay banner, podría ser un problema de timing, devolver False para reintentar
                return False
            except Exception as e:
                print(f"Error al interactuar con el campo de entrada: {e}")
                return False
            
            # Buscar y seleccionar sugerencia
            try:
                # Esperar a que aparezcan las sugerencias
                WebDriverWait(driver, TIEMPO_ESPERA_LARGO).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "ul.artdeco-typeahead__results-list li")
                )
                
                sugerencias = div_ubicacion.find_elements(By.CSS_SELECTOR, "ul.artdeco-typeahead__results-list li")
                match = False
                
                print(f"Buscando coincidencia para '{UBICACION}' entre {len(sugerencias)} sugerencias")
                
                for i, sug in enumerate(sugerencias):
                    try:
                        txt_sug = sug.text.strip().lower()
                        print(f"   {i+1}. '{txt_sug}'")
                        
                        # Coincidencia exacta o si la ubicación está contenida en la sugerencia
                        if UBICACION.lower() == txt_sug or UBICACION.lower() in txt_sug:
                            print(f"Coincidencia encontrada: '{txt_sug}'")
                            time.sleep(TIEMPO_ESPERA_CORTO)
                            
                            # Seleccionar sugerencia con ActionChains
                            try:
                                ActionChains(driver).move_to_element(sug).click().perform()
                                time.sleep(TIEMPO_ESPERA_MEDIO)
                                match = True
                            except Exception as e:
                                print(f"Error seleccionando sugerencia: {e}")
                                continue
                            
                            break
                    except Exception as e:
                        print(f"Error procesando sugerencia {i+1}: {e}")
                        continue
                
                if not match:
                    print(f"No se encontró coincidencia para '{UBICACION}'")
                    return False
                    
                print(f"Sugerencia seleccionada para '{UBICACION}'")
                
                # Buscar y hacer clic en cualquier botón de confirmación que pueda aparecer
                try:
                    # Esperar un momento para que aparezca el botón de confirmación si existe
                    time.sleep(TIEMPO_ESPERA_MEDIO)
                    
                    # Buscar diferentes tipos de botones de confirmación
                    botones_confirmacion = [
                        "button.artdeco-pill__button",
                        "button[data-test-typeahead-result-add-btn]",
                        "button.artdeco-typeahead__add-button",
                        "button.facet-pill__confirm-button",
                        "button[aria-label*='Add']",
                        "button[title*='Add']"
                    ]
                    
                    confirmacion_encontrada = False
                    for selector_boton in botones_confirmacion:
                        try:
                            btn_confirmar_inmediato = div_ubicacion.find_element(By.CSS_SELECTOR, selector_boton)
                            if btn_confirmar_inmediato and btn_confirmar_inmediato.is_displayed() and btn_confirmar_inmediato.is_enabled():
                                print(f"Confirmando selección con botón: {selector_boton}")
                                btn_confirmar_inmediato.click()
                                time.sleep(TIEMPO_ESPERA_MEDIO)
                                confirmacion_encontrada = True
                                break
                        except Exception:
                            continue
                    
                    if not confirmacion_encontrada:
                        # Estrategia alternativa: Presionar ENTER en el input si aún está visible
                        try:
                            input_field = div_ubicacion.find_element(By.CSS_SELECTOR, "input.artdeco-typeahead__input")
                            if input_field.is_displayed():
                                input_field.send_keys(Keys.ENTER)
                                time.sleep(TIEMPO_ESPERA_MEDIO)
                        except Exception:
                            pass
                            
                except Exception:
                    pass
            except TimeoutException:
                print(f"Timeout esperando sugerencias para '{UBICACION}'")
                return False
            except Exception as e:
                print(f"Error al seleccionar sugerencia: {e}")
                return False
            
            time.sleep(TIEMPO_ESPERA_LARGO)  # Esperar para que se procese la selección
            
            # Si después de la selección no hay filtros, intentar una estrategia manual
            try:
                chips_verificacion_final = div_ubicacion.find_elements(By.CSS_SELECTOR, "div.facet-pill__pill-text")
                if not chips_verificacion_final:
                    # Buscar específicamente el texto de la ubicación en toda la sección y hacer clic
                    elementos_con_texto = div_ubicacion.find_elements(By.XPATH, f".//*[contains(text(), '{UBICACION}') or contains(text(), '{UBICACION.lower()}')]")
                    for elem in elementos_con_texto:
                        try:
                            if elem.is_displayed():
                                driver.execute_script("arguments[0].click();", elem)
                                time.sleep(TIEMPO_ESPERA_MEDIO)
                                # Verificar si apareció el chip
                                chips_post_manual = div_ubicacion.find_elements(By.CSS_SELECTOR, "div.facet-pill__pill-text")
                                if chips_post_manual:
                                    break
                        except Exception:
                            continue
            except Exception:
                pass
            
            # Confirmar ubicación (si existe el botón de confirmación principal)
            try:
                btn_confirmar = div_ubicacion.find_element(By.CSS_SELECTOR, "button.artdeco-pill__button")
                if btn_confirmar and btn_confirmar.is_displayed():
                    print(f"Confirmando selección de '{UBICACION}' con botón principal")
                    btn_confirmar.click()
                    time.sleep(TIEMPO_ESPERA_LARGO)
            except Exception:
                # No siempre existe el botón de confirmación, continuar
                pass
            
            # Verificar que el filtro se aplicó correctamente antes de proceder
            print(f"Verificando que el filtro '{UBICACION}' se aplicó correctamente...")
            filtro_aplicado_correctamente = False
            
            # Intentar verificar hasta 5 veces con esperas incrementales
            for intento_verificacion in range(5):
                try:
                    time.sleep(TIEMPO_ESPERA_MEDIO)  # Esperar antes de cada verificación
                    
                    # Re-obtener el div_ubicacion por si se ha actualizado
                    div_ubicacion_verificacion = esperar_elemento(driver, By.CSS_SELECTOR, 'div.query-facet[data-query-type="LOCATION"]', timeout=TIEMPO_ESPERA_LARGO)
                    if not div_ubicacion_verificacion:
                        continue
                        
                    chips_verificacion = div_ubicacion_verificacion.find_elements(By.CSS_SELECTOR, "div.facet-pill__pill-text")
                    ubicaciones_verificacion = []
                    
                    for chip in chips_verificacion:
                        try:
                            raw_text = chip.text.strip()
                            if raw_text:
                                clean_text = normalizar_texto(raw_text)
                                ubicaciones_verificacion.append(clean_text)
                        except Exception:
                            continue
                    
                    ub_verificar = normalizar_texto(UBICACION)
                    print(f"   Intento {intento_verificacion + 1}: Filtros actuales: {ubicaciones_verificacion}")
                    
                    if ub_verificar in ubicaciones_verificacion:
                        print(f"Filtro '{UBICACION}' aplicado correctamente")
                        filtro_aplicado_correctamente = True
                        break
                    else:
                        # Si no se aplicó, esperar más tiempo antes del siguiente intento
                        if intento_verificacion < 4:  # No esperar en el último intento
                            time.sleep(TIEMPO_ESPERA_MEDIO)
                        
                except Exception as e:
                    print(f"   Error en verificación {intento_verificacion + 1}: {e}")
                    continue
            
            if not filtro_aplicado_correctamente:
                print(f"Filtro '{UBICACION}' no se aplicó correctamente después de 5 verificaciones")
                return False
            # Aplicar filtro
            try:
                WebDriverWait(driver, TIEMPO_ESPERA_LARGO).until(
                    lambda d: (
                        (btn := d.find_element(By.CSS_SELECTOR, "button[data-test-search-filters-apply-btn]")) and
                        btn.is_enabled() and btn.get_attribute("disabled") is None
                    )
                )
                btn_aplicar = driver.find_element(By.CSS_SELECTOR, "button[data-test-search-filters-apply-btn]")
                if not btn_aplicar:
                    return False
                
                btn_aplicar.click()
                time.sleep(TIEMPO_ESPERA_MEDIO)
                
                # Esperar a que se procese la búsqueda (manejar callback opcional)
                if callable(esperar_resultados_o_banner):
                    resultado = esperar_resultados_o_banner(driver, timeout=TIEMPO_ESPERA_LARGO * 2)
                    if resultado == 'resultados':
                        return True
                    elif resultado == 'banner':
                        print(f"Error en búsqueda para '{UBICACION}' - Banner detectado")
                        return False
                    else:
                        print(f"Timeout esperando resultados para '{UBICACION}'")
                        return False
                else:
                    # Fallback: esperar a que aparezcan tarjetas de resultados o se detecte banner
                    try:
                        WebDriverWait(driver, TIEMPO_ESPERA_LARGO * 2).until(
                            lambda d: (
                                hay_banner_error(d) or
                                len(d.find_elements(By.CSS_SELECTOR, "li.overview-layout__top-card")) > 0
                            )
                        )
                    except Exception:
                        pass
                    if hay_banner_error(driver):
                        print(f"Error en búsqueda para '{UBICACION}' - Banner detectado")
                        return False
                    # Si hay tarjetas, continuar; de lo contrario, considerar timeout pero continuar para reintentos externos
                    top_cards_presentes = driver.find_elements(By.CSS_SELECTOR, "li.overview-layout__top-card")
                    if top_cards_presentes:
                        return True
                    print(f"Timeout esperando resultados para '{UBICACION}'")
                    return False
            except (TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException):
                return False
            
            return True
        except Exception as e:
            print(f"Error aplicando filtro de ubicación: {e}")
            return False
    try:
        intentos = 0
        max_intentos = 5
        exito = False
        
        while intentos < max_intentos:
            intentos += 1
            print(f"Aplicando '{UBICACION}' (Intento {intentos}/{max_intentos})")
            
            resultado_filtro = aplicar_filtro(driver, UBICACION)
            
            if resultado_filtro is True:
                # Verificar que haya datos disponibles
                top_cards = driver.find_elements(By.CSS_SELECTOR, "li.overview-layout__top-card")
                if top_cards and len(top_cards) > 0:
                    # Verificar que las tarjetas tienen datos reales
                    tiene_datos = False
                    for card in top_cards:
                        try:
                            valor = card.find_element(By.CSS_SELECTOR, ".overview-layout__top-card-value")
                            if valor and valor.text.strip() and valor.text.strip() != "--":
                                tiene_datos = True
                                break
                        except:
                            continue
                    if tiene_datos:
                        exito = True
                        break
                    else:
                        print(f"Sin datos válidos para '{UBICACION}', esperando {TIEMPO_ESPERA_BANNER}s, refrescando y reintentando...")
                        time.sleep(TIEMPO_ESPERA_BANNER)
                        print(f"Refrescando página tras espera...")
                        driver.refresh()
                        time.sleep(TIEMPO_ESPERA_PAGINA)
                        
                        # Verificar que el filtro de ubicación esté disponible tras refresh
                        div_ubicacion_check = esperar_elemento(driver, By.CSS_SELECTOR, 'div.query-facet[data-query-type="LOCATION"]', timeout=TIEMPO_ESPERA_LARGO)
                        if not div_ubicacion_check:
                            print(f"Filtro de ubicación no disponible tras refresh")
                            continue
                else:
                    print(f"Sin resultados para '{UBICACION}', esperando {TIEMPO_ESPERA_BANNER}s, refrescando y reintentando...")
                    time.sleep(TIEMPO_ESPERA_BANNER)
                    print(f"Refrescando página tras espera...")
                    driver.refresh()
                    time.sleep(TIEMPO_ESPERA_PAGINA)
                    
                    # Verificar que el filtro de ubicación esté disponible tras refresh
                    div_ubicacion_check = esperar_elemento(driver, By.CSS_SELECTOR, 'div.query-facet[data-query-type="LOCATION"]', timeout=TIEMPO_ESPERA_LARGO)
                    if not div_ubicacion_check:
                        print(f"Filtro de ubicación no disponible tras refresh")
                        continue
                continue
            else:
                print(f"Fallo en intento {intentos}")
                # Si hay banner de error, esperar 40s antes de refrescar
                if hay_banner_error(driver):
                    print(f"Banner detectado tras fallo, esperando {TIEMPO_ESPERA_BANNER}s antes de refrescar...")
                    if callable(esperar_y_refrescar_si_banner):
                        if not esperar_y_refrescar_si_banner(
                            driver,
                            max_intentos=1,
                            espera_seg=TIEMPO_ESPERA_BANNER,
                            ubicacion=UBICACION,
                            re_aplicar_filtro=aplicar_filtro,
                        ):
                            continue
                    else:
                        # Fallback básico: esperar, refrescar y volver a intentar aplicar filtro
                        time.sleep(TIEMPO_ESPERA_BANNER)
                        driver.refresh()
                        time.sleep(TIEMPO_ESPERA_PAGINA)
                        if not aplicar_filtro(driver, UBICACION):
                            continue
        
        if not exito:
            print(f"OMITIDO: '{UBICACION}' tras {max_intentos} intentos")
            return None
            
        # Verificación final de banner antes de extraer datos
        if hay_banner_error(driver):
            print(f"Banner detectado antes de extraer datos, esperando {TIEMPO_ESPERA_BANNER}s antes de refrescar...")
            if callable(esperar_y_refrescar_si_banner):
                if not esperar_y_refrescar_si_banner(
                    driver,
                    max_intentos=2,
                    espera_seg=TIEMPO_ESPERA_BANNER,
                    ubicacion=UBICACION,
                    re_aplicar_filtro=aplicar_filtro,
                ):
                    print(f"OMITIDO: '{UBICACION}' por errores persistentes")
                    return None
            else:
                time.sleep(TIEMPO_ESPERA_BANNER)
                driver.refresh()
                time.sleep(TIEMPO_ESPERA_PAGINA)
                if not aplicar_filtro(driver, UBICACION):
                    print(f"OMITIDO: '{UBICACION}' por errores persistentes")
                    return None
        
        time.sleep(TIEMPO_ESPERA_CORTO)
        print(f"Extrayendo datos para '{UBICACION}'...")
        
        # Verificar una vez más que no aparezca el banner durante la extracción
        if hay_banner_error(driver):
            print(f"OMITIDO: '{UBICACION}' - Banner aparece durante extracción")
            return None
        
        # Extraer datos de las tarjetas
        top_cards = driver.find_elements(By.CSS_SELECTOR, "li.overview-layout__top-card")
        profesionales = anuncios_empleo = None
        for card in top_cards:
            try:
                tipo = card.find_element(By.CSS_SELECTOR, ".overview-layout__top-card-type").text.strip().lower()
                valor = card.find_element(By.CSS_SELECTOR, ".overview-layout__top-card-value").text.strip()
                if "profesionales" == tipo:
                    profesionales = valor
                elif "anuncio de empleo" in tipo or "anuncios de empleo" in tipo:
                    anuncios_empleo = valor
            except Exception:
                continue

        # Extraer demanda de contratación
        try:
            span_demanda = driver.find_element(By.CSS_SELECTOR, "div.overview-layout__hdi--reading span.overview-layout__hdi--value")
            demanda_contratacion = span_demanda.text.strip()
        except Exception:
            demanda_contratacion = None

        datos = {
            "carpeta": carpeta_nombre,
            "proyecto": proyecto_nombre,
            "ubicacion": UBICACION,
            "profesionales": profesionales,
            "anuncios_empleo": anuncios_empleo,
            "demanda_contratacion": demanda_contratacion,
        }
        
        # Verificar que todos los datos esenciales fueron extraídos
        datos_extraidos = []
        datos_faltantes = []
        
        if profesionales is not None and profesionales != "--":
            datos_extraidos.append(f"profesionales: {profesionales}")
        else:
            datos_faltantes.append("profesionales")
            
        # Para anuncios_empleo, consideramos válido cualquier valor (incluido None, "", "--")
        # porque se normaliza automáticamente a "1" en utils.py
        if anuncios_empleo is not None and anuncios_empleo != "--":
            datos_extraidos.append(f"anuncios: {anuncios_empleo}")
        else:
            datos_extraidos.append(f"anuncios: 1 (normalizado)")  # Mostrar que se normalizará
            
        if demanda_contratacion is not None and demanda_contratacion != "--":
            datos_extraidos.append(f"demanda: {demanda_contratacion}")
        else:
            datos_faltantes.append("demanda_contratacion")
        
        # Resultado final de la extracción
        if datos_extraidos:
            print(f"EXTRACCIÓN EXITOSA '{UBICACION}': {', '.join(datos_extraidos)}")
            if datos_faltantes:
                print(f"Datos faltantes: {', '.join(datos_faltantes)}")
        else:
            print(f"EXTRACCIÓN FALLIDA '{UBICACION}': No se obtuvieron datos válidos")
            
        time.sleep(TIEMPO_ESPERA_CORTO)
        return datos
        
    except Exception as e:
        print(f"ERROR: {UBICACION} - {str(e)[:50]}...")
        return None