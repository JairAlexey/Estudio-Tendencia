import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def navegar_a_aptitudes(driver):
    """Navega a la sección de aptitudes"""
    try:
        # Buscar el enlace de aptitudes por su data-test-report-tab-item
        aptitudes_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-test-report-tab-item="skills"]')
            )
        )
        aptitudes_link.click()
        
        # Esperar a que cargue la tabla de aptitudes
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "most-common-skills-table"))
        )
        return True
    except Exception as e:
        print(f"Error navegando a aptitudes: {e}")
        return False

def extraer_aptitudes(driver, carrera):
    """Extrae las primeras 10 aptitudes de la tabla de aptitudes más habituales"""
    aptitudes = []
    try:
        # Esperar a que cargue la tabla principal
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "most-common-skills-table"))
        )
        # Espera adicional para asegurar que la tabla esté completamente cargada
        time.sleep(10)
        tabla = driver.find_element(By.CLASS_NAME, "most-common-skills-table")
        filas = tabla.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
        if not filas:
            filas = tabla.find_elements(By.TAG_NAME, "tr")
        print(f"[Aptitudes] Filas encontradas: {len(filas)}")
        for idx in range(min(10, len(filas))):
            try:
                filas_actualizadas = tabla.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
                if not filas_actualizadas:
                    filas_actualizadas = tabla.find_elements(By.TAG_NAME, "tr")
                fila = filas_actualizadas[idx]
                nombre_elem = fila.find_elements(By.CSS_SELECTOR, "td.table-cells__col-entity div.t-black")
                cantidad_elem = fila.find_elements(By.CSS_SELECTOR, "td.table-cells__col-xlarge-length button.table-cells__interactable-link")
                porcentaje_elem = fila.find_elements(By.CSS_SELECTOR, "td.table-cells__col-xlarge-length button.table-cells__percentage-button")
                if nombre_elem and cantidad_elem and porcentaje_elem:
                    nombre = nombre_elem[0].text.strip().replace("Agregar", "").strip()
                    cantidad_raw = cantidad_elem[0].text.strip().replace(",", "")
                    try:
                        cantidad = float(cantidad_raw)
                    except Exception:
                        cantidad = None
                    porcentaje = porcentaje_elem[0].text.strip()
                    aptitudes.append({
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "porcentaje": porcentaje
                    })
                else:
                    print("Fila ignorada: no tiene todos los elementos necesarios")
            except Exception as e:
                print(f"Error procesando fila de aptitud {idx+1}: {e}")
                continue
        print(f"[Aptitudes] Extraídas: {len(aptitudes)}")
        return aptitudes
    except Exception as e:
        print(f"Error extrayendo aptitudes: {e}")
        return []
