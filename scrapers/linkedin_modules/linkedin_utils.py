import time
import unicodedata
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ERROR_SELECTORS = [
    "div.artdeco-toast-item[data-test-artdeco-toast-item-type='error']",
    "div[data-test-artdeco-toast-item-type='error']",
    "div.search-filters__notice-v2"
]

TIEMPO_ESPERA_CORTO = 1
TIEMPO_ESPERA_MEDIO = 2
TIEMPO_ESPERA_LARGO = 4

def normalizar_texto(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.strip().lower()

def hay_banner_error(driver, timeout=TIEMPO_ESPERA_CORTO):
    try:
        banner_error = driver.find_element(By.CSS_SELECTOR, 'div[data-test-artdeco-toast-item-type="error"]')
        if banner_error and banner_error.is_displayed():
            mensaje = banner_error.text.lower()
            if "modifica la búsqueda" in mensaje or "modify your search" in mensaje or "informe" in mensaje:
                return True
    except (NoSuchElementException, StaleElementReferenceException):
        pass
    try:
        for selector in ERROR_SELECTORS:
            elementos = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elementos:
                if el.is_displayed():
                    texto = el.text.lower()
                    if "modifica la búsqueda" in texto or "modify your search" in texto:
                        return True
    except Exception:
        pass
    return False

def esperar_elemento(driver, by, selector, timeout=TIEMPO_ESPERA_LARGO):
    try:
        return WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(by, selector)
        )
    except TimeoutException:
        return None

def esperar_elemento_visible(driver, by, selector, timeout=TIEMPO_ESPERA_LARGO):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
    except TimeoutException:
        return None
