import time
import unicodedata
from selenium.webdriver.common.by import By

def normalizar_texto(texto):
    """
    Normaliza el texto eliminando tildes y convirtiendo a minúsculas.
    """
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.strip().lower()

def buscar_carpeta_en_pagina(driver, carpeta_buscar, TIEMPO_ESPERA_MEDIO=2):
    """
    Recorre los elementos de carpeta (articles) de la página actual y
    si encuentra la carpeta buscada, navega a su URL y retorna True.
    """
    folder_cards = driver.find_elements(By.CSS_SELECTOR, "article.saved-folder-card")
    for card in folder_cards:
        try:
            link_title = card.find_element(
                By.CSS_SELECTOR, "a.saved-folder-card__link-title"
            )
            nombre_carpeta = link_title.text.strip()
            href_carpeta = link_title.get_attribute("href")
            if normalizar_texto(nombre_carpeta) == normalizar_texto(carpeta_buscar):
                print(f"Carpeta encontrada: {nombre_carpeta}")
                driver.get(href_carpeta)
                time.sleep(TIEMPO_ESPERA_MEDIO)
                return True
        except Exception as e:
            print("Error al leer la carpeta:", e)
            continue
    return False
