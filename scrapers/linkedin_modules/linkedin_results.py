import time
from selenium.webdriver.common.by import By

def esperar_resultados_o_banner(driver, hay_banner_error, TIEMPO_ESPERA_LARGO=4):
    """
    Espera a que aparezcan resultados (tarjetas o tabla) o que el banner de error persista.
    Devuelve 'resultados' si aparecen datos, 'banner' si persiste el banner, o 'timeout' si no hay nada.
    """
    end_time = time.time() + TIEMPO_ESPERA_LARGO
    while time.time() < end_time:
        if hay_banner_error(driver, timeout=0.5):
            print("Banner de error detectado")
            return 'banner'
        top_cards = driver.find_elements(By.CSS_SELECTOR, "li.overview-layout__top-card")
        if top_cards and len(top_cards) > 0:
            for card in top_cards:
                try:
                    valor = card.find_element(By.CSS_SELECTOR, ".overview-layout__top-card-value")
                    if valor and valor.text.strip():
                        return 'resultados'
                except:
                    continue
        tabla = driver.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
        if tabla and len(tabla) > 0:
            return 'resultados'
        time.sleep(0.5)
    return 'timeout'
