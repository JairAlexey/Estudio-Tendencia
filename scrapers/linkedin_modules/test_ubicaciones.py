from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from linkedin_locations import navegar_a_ubicaciones, extraer_ubicaciones

# Configura aquí tu URL de reporte de estudio (América Latina)
REPORTE_URL = "https://www.linkedin.com/insights/report/talent/NzA2MzE2MTh8MTY4MzI0MDUyfDE1MjE5MDU2MnwxMzcyMzQxMzh8SA==/location"

def test_ubicaciones():
    driver = webdriver.Chrome()
    driver.get(REPORTE_URL)
    input("Inicia sesión manualmente y presiona ENTER aquí...")

    try:
        print("Navegando a la pestaña de ubicaciones...")
        if navegar_a_ubicaciones(driver):
            ubicaciones_data = extraer_ubicaciones(driver)
            with open("ubicaciones_test.json", "w", encoding="utf-8") as f:
                json.dump(ubicaciones_data, f, ensure_ascii=False, indent=2)
            print("[INFO] Datos de ubicaciones guardados en ubicaciones_test.json")
        else:
            print("No se pudo navegar a la pestaña de ubicaciones.")
    except Exception as e:
        print(f"Error en test de ubicaciones: {e}")

    driver.quit()

if __name__ == "__main__":
    test_ubicaciones()
