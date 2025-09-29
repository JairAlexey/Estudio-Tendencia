from scrapers.linkedin_modules.linkedin_pagination import (
    paginar_y_buscar_carpeta,
)
from scrapers.linkedin_modules.linkedin_folder import buscar_carpeta_en_pagina
from scrapers.linkedin_modules.driver_config import (
    limpiar_singleton_lock,
    crear_opciones_chrome,
    iniciar_driver,
    login_linkedin,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from dotenv import load_dotenv

# Configuración de tiempos (igual que en linkedin.py)
TIEMPO_ESPERA_CORTO = 1
TIEMPO_ESPERA_MEDIO = 2
TIEMPO_ESPERA_LARGO = 4
TIEMPO_ESPERA_BANNER = 40
TIEMPO_ESPERA_PAGINA = 3

def extraer_proyectos_pagina(driver):
    """
    Extrae todos los proyectos de la página actual usando la misma lógica
    que linkedin_project.py
    """
    proyectos = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
    if rows:
        driver.execute_script("arguments[0].scrollIntoView(true);", rows[0])

    for row in rows:
        try:
            span = row.find_element(
                By.CSS_SELECTOR,
                "td.saved-reports-table__table-cell--display-name a div span"
            )
            titulo = span.text.strip()
            enlace = row.find_element(
                By.CSS_SELECTOR,
                "td.saved-reports-table__table-cell--display-name a"
            )
            url = enlace.get_attribute("href")
            
            print(f"  - {titulo}")
            proyectos.append({
                'titulo': titulo,
                'url': url
            })
        except Exception as e:
            print(f"Error al extraer proyecto: {e}")
            continue
            
    return proyectos

def procesar_paginacion(driver, proyectos_lista):
    """
    Procesa la paginación usando el selector correcto de los botones de página
    """
    try:
        while True:
            # Extraer proyectos de la página actual
            proyectos_pagina = extraer_proyectos_pagina(driver)
            proyectos_lista.extend(proyectos_pagina)
            
            # Esperar a que los botones de paginación estén presentes
            try:
                # Encuentra todos los botones de página
                botones = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, 
                        "ul.artdeco-pagination__pages--number li.artdeco-pagination__indicator--number"
                    ))
                )
                
                # Encuentra el botón activo actual
                pagina_actual = None
                siguiente = None
                
                for i, boton in enumerate(botones):
                    if 'active selected' in boton.get_attribute('class'):
                        pagina_actual = i
                        if i + 1 < len(botones):  # Si hay una página siguiente
                            siguiente = botones[i + 1]
                        break
                
                if siguiente:
                    print(f"Navegando a la siguiente página...")
                    # Hacer clic usando JavaScript para mayor confiabilidad
                    btn = siguiente.find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(TIEMPO_ESPERA_MEDIO)  # Esperar a que cargue la nueva página
                else:
                    print("No hay más páginas disponibles")
                    break
                    
            except Exception as e:
                print(f"No hay más páginas o error en paginación: {e}")
                break
                
    except Exception as e:
        print(f"Error en paginación: {e}")

def listar_proyectos_en_carpeta(driver, carpeta_nombre):
    """Lista todos los proyectos en una carpeta específica"""
    proyectos = []
    
    try:
        # Usar la función existente para encontrar y abrir la carpeta
        encontrada = paginar_y_buscar_carpeta(
            driver, 
            carpeta_nombre,
            buscar_carpeta_en_pagina,
            "https://www.linkedin.com/insights/saved?reportType=talent&tab=folders",
            TIEMPO_ESPERA_CORTO,
            TIEMPO_ESPERA_MEDIO
        )

        if not encontrada:
            print(f"❌ No se encontró la carpeta '{carpeta_nombre}'")
            return []

        print(f"\nProyectos en la carpeta '{carpeta_nombre}':")
        time.sleep(TIEMPO_ESPERA_MEDIO)  # Esperar a que cargue la página de la carpeta
        
        # Procesar todas las páginas de proyectos
        procesar_paginacion(driver, proyectos)
        
        return proyectos

    except Exception as e:
        print(f"Error al listar proyectos: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_carpetas():
    load_dotenv()
    EMAIL = os.getenv("LINKEDIN_USER")
    PASSWORD = os.getenv("LINKEDIN_PASS")

    if not EMAIL or not PASSWORD:
        print("❌ Faltan credenciales de LinkedIn.")
        return False

    user_data_dir = r"C:\Users\User\Documents\TRABAJO - UDLA\Estudio-Tendencia\profile"
    profile_directory = "Default"
    
    print("1. Limpiando perfil anterior...")
    limpiar_singleton_lock(user_data_dir, profile_directory)
    
    print("2. Configurando opciones de Chrome...")
    options = crear_opciones_chrome(user_data_dir, profile_directory)
    
    print("3. Iniciando driver...")
    driver = iniciar_driver(options)
    
    try:
        print("4. Intentando login...")
        if not login_linkedin(driver, EMAIL, PASSWORD):
            print("❌ Falló el login")
            return False

        print("5. Navegando a la página de carpetas...")
        url = "https://www.linkedin.com/insights/saved?reportType=talent&tab=folders"
        driver.get(url)
        time.sleep(TIEMPO_ESPERA_MEDIO)

        # Lista de carpetas a procesar
        carpetas_objetivo = ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"]
        
        todos_los_proyectos = {}
        for carpeta in carpetas_objetivo:
            print(f"\n=== Procesando carpeta: {carpeta} ===")
            proyectos = listar_proyectos_en_carpeta(driver, carpeta)
            todos_los_proyectos[carpeta] = proyectos
            print(f"Encontrados {len(proyectos)} proyectos en {carpeta}")
            
            # Volver a la página principal de carpetas
            driver.get(url)
            time.sleep(TIEMPO_ESPERA_MEDIO)

        # Mostrar resumen final
        print("\n=== Resumen Final ===")
        for carpeta, proyectos in todos_los_proyectos.items():
            print(f"\nCarpeta: {carpeta}")
            print(f"Total proyectos: {len(proyectos)}")
            for proyecto in proyectos:
                print(f"  - {proyecto['titulo']}")

        return True

    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n6. Cerrando el navegador...")
        driver.quit()

if __name__ == "__main__":
    print("=== Iniciando prueba de búsqueda de carpetas ===")
    test_carpetas()