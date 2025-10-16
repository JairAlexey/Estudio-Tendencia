from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Configura aquí tu URL de reporte de estudio
REPORTE_URL = "https://www.linkedin.com/insights/report/talent/NzA2MzE2MTh8MTY4MzI0MDUyfDE1MjE5MDU2MnwxMzcyMzQxMzh8SA==/overview"

def test_aptitudes():
    driver = webdriver.Chrome()  # O tu driver preferido
    driver.get(REPORTE_URL)
    input("Inicia sesión manualmente y presiona ENTER aquí...")

    # Navega a la pestaña de aptitudes
    try:
        print("Buscando botón de aptitudes...")
        aptitudes_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-test-report-tab-item="skills"]'))
        )
        aptitudes_btn.click()
        print("Botón de aptitudes presionado.")
    except Exception as e:
        print(f"Error encontrando o presionando el botón de aptitudes: {e}")
        driver.quit()
        return

    aptitudes_data = []
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "most-common-skills-table"))
        )
        tabla = driver.find_element(By.CLASS_NAME, "most-common-skills-table")
        filas = tabla.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
        if not filas:
            filas = tabla.find_elements(By.TAG_NAME, "tr")
        print(f"[TEST] Filas de aptitudes encontradas: {len(filas)}")
        # Re-obtener filas justo antes de procesar cada una
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
                    nombre = nombre_elem[0].text.strip()
                    cantidad = cantidad_elem[0].text.strip()
                    porcentaje = porcentaje_elem[0].text.strip()
                    aptitudes_data.append({
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "porcentaje": porcentaje
                    })
                else:
                    print("Fila ignorada: no tiene todos los elementos necesarios")
            except Exception as e:
                print(f"Error procesando fila {idx+1}: {e}")
                continue
        # Guardar en JSON
        with open("aptitudes_test.json", "w", encoding="utf-8") as f:
            json.dump(aptitudes_data, f, ensure_ascii=False, indent=2)
        print("[INFO] Datos de aptitudes guardados en aptitudes_test.json")
    except Exception as e:
        print(f"Error encontrando la tabla de aptitudes: {e}")

    driver.quit()

if __name__ == "__main__":
    test_aptitudes()
