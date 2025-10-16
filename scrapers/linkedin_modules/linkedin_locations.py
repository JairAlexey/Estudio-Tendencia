import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navegar_a_ubicaciones(driver):
    """Navega a la pestaña de ubicaciones"""
    try:
        ubicaciones_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-test-report-tab-item="location"]'))
        )
        ubicaciones_btn.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "insights-table__table"))
        )
        # Espera adicional para asegurar carga completa
        time.sleep(5)
        return True
    except Exception as e:
        print(f"Error navegando a ubicaciones: {e}")
        return False

def extraer_ubicaciones(driver):
    """Extrae las 10 primeras ubicaciones y su cantidad de profesionales"""
    ubicaciones = []
    try:
        tabla = driver.find_element(By.CLASS_NAME, "insights-table__table")
        filas = tabla.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
        if not filas:
            filas = tabla.find_elements(By.TAG_NAME, "tr")
        print(f"[Ubicaciones] Filas encontradas: {len(filas)}")
        for idx in range(min(10, len(filas))):
            try:
                filas_actualizadas = tabla.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
                if not filas_actualizadas:
                    filas_actualizadas = tabla.find_elements(By.TAG_NAME, "tr")
                fila = filas_actualizadas[idx]
                # Ubicación
                ubicacion_elem = fila.find_elements(By.CSS_SELECTOR, "td.table-cells__col-entity div.t-black")
                # Profesionales
                cantidad_elem = fila.find_elements(By.CSS_SELECTOR, "td.table-cells__col-medium-length button.table-cells__interactable-link")
                if ubicacion_elem and cantidad_elem:
                    ubicacion = ubicacion_elem[0].text.strip()
                    cantidad_raw = cantidad_elem[0].text.strip().replace(",", "")
                    try:
                        cantidad = float(cantidad_raw)
                    except Exception:
                        cantidad = None
                    ubicaciones.append({
                        "ubicacion": ubicacion,
                        "profesionales": cantidad
                    })
                else:
                    print("Fila ignorada: no tiene todos los elementos necesarios")
            except Exception as e:
                print(f"Error procesando fila de ubicación {idx+1}: {e}")
                continue
        print(f"[Ubicaciones] Extraídas: {len(ubicaciones)}")
        return ubicaciones
    except Exception as e:
        print(f"Error extrayendo ubicaciones: {e}")
        return []
