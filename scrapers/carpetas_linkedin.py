from scrapers.linkedin_modules.linkedin_pagination import paginar_y_buscar_carpeta
from scrapers.linkedin_modules.linkedin_folder import buscar_carpeta_en_pagina
from scrapers.linkedin_modules.driver_config import (
    limpiar_singleton_lock,
    crear_opciones_chrome,
    iniciar_driver,
    login_linkedin,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from dotenv import load_dotenv
from conexion import conn, cursor

# Configuración de tiempos - AUMENTADOS para LinkedIn lento
TIEMPO_ESPERA_CORTO = 8   # antes: 3
TIEMPO_ESPERA_MEDIO = 10  # antes: 5
TIEMPO_ESPERA_LARGO = 12  # antes: 8
TIEMPO_ESPERA_BANNER = 60 # antes: 60
TIEMPO_ESPERA_PAGINA = 9 # antes: 6

def guardar_proyecto_carpeta(tipo_carpeta, nombre_proyecto, url_proyecto=None):
    """Guarda o actualiza un proyecto en la base de datos"""
    try:
        cursor.execute("""
            INSERT INTO carpetas (tipo_carpeta, nombre_proyecto, url_proyecto)
            VALUES (%s, %s, %s)
            ON CONFLICT (tipo_carpeta, nombre_proyecto) 
            DO UPDATE SET url_proyecto = EXCLUDED.url_proyecto
        """, (tipo_carpeta, nombre_proyecto, url_proyecto))
        conn.commit()
    except Exception as e:
        conn.rollback()  # Rollback on error
        print(f"Error al guardar proyecto {nombre_proyecto} en carpeta {tipo_carpeta}: {e}")
        return False
    return True

def extraer_proyectos_pagina(driver):
    """Extrae todos los proyectos de la página actual"""
    proyectos = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr.artdeco-models-table-row")
    if rows:
        driver.execute_script("arguments[0].scrollIntoView(true);", rows[0])
        # Espera adicional para asegurar carga de la tabla
        time.sleep(TIEMPO_ESPERA_LARGO)

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
    """Procesa la paginación usando el selector correcto de los botones de página"""
    try:
        while True:
            # Extraer proyectos de la página actual
            proyectos_pagina = extraer_proyectos_pagina(driver)
            proyectos_lista.extend(proyectos_pagina)
            
            try:
                # Encuentra todos los botones de página
                botones = WebDriverWait(driver, 30).until(
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
                    btn = siguiente.find_element(By.TAG_NAME, "button")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(TIEMPO_ESPERA_PAGINA)
                else:
                    print("No hay más páginas disponibles")
                    break
                    
            except Exception as e:
                print(f"No hay más páginas o error en paginación: {e}")
                break
                
    except Exception as e:
        print(f"Error en paginación: {e}")

def listar_proyectos_en_carpeta(driver, carpeta_nombre, url):
    """Lista todos los proyectos en una carpeta específica"""
    proyectos = []
    
    try:
        encontrada = paginar_y_buscar_carpeta(
            driver, 
            carpeta_nombre,
            buscar_carpeta_en_pagina,
            url,
            TIEMPO_ESPERA_CORTO,
            TIEMPO_ESPERA_MEDIO
        )

        if not encontrada:
            print(f"❌ No se encontró la carpeta '{carpeta_nombre}'")
            return []

        print(f"\nProyectos en la carpeta '{carpeta_nombre}':")
        time.sleep(TIEMPO_ESPERA_MEDIO)
        
        # Procesar todas las páginas de proyectos
        procesar_paginacion(driver, proyectos)
        
        return proyectos

    except Exception as e:
        print(f"Error al listar proyectos: {e}")
        import traceback
        traceback.print_exc()
        return []

def scraper_carpetas():
    load_dotenv()
    EMAIL = os.getenv("LINKEDIN_USER")
    PASSWORD = os.getenv("LINKEDIN_PASS")

    if not EMAIL or not PASSWORD:
        print("❌ Faltan credenciales de LinkedIn.")
        return False

    CARPETAS = ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"]
    user_data_dir = r"C:\Usuarios\Alexey\Documents\TRABAJO - UDLA\Estudio-Tendencia\profile"
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

        total_proyectos = 0
        for carpeta in CARPETAS:
            print(f"\n=== Procesando carpeta: {carpeta} ===")
            # Usar la nueva función listar_proyectos_en_carpeta
            proyectos = listar_proyectos_en_carpeta(driver, carpeta, url)
            
            # Guardar cada proyecto en la base de datos
            for proyecto in proyectos:
                if guardar_proyecto_carpeta(carpeta, proyecto['titulo'], proyecto['url']):
                    print(f"✓ Guardado: {proyecto['titulo']} en {carpeta}")
                    total_proyectos += 1

            # Volver a la página principal de carpetas
            driver.get(url)
            time.sleep(TIEMPO_ESPERA_PAGINA)

        print(f"\n=== Resumen Final ===")
        print(f"Total de proyectos procesados: {total_proyectos}")
        return True

    except Exception as e:
        print(f"Error en el scraper: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n6. Cerrando el navegador...")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    scraper_carpetas()