from scrapers.linkedin_modules.driver_config import (
    limpiar_singleton_lock,
    crear_opciones_chrome,
    iniciar_driver,
    login_linkedin,
)
from scrapers.linkedin_modules.linkedin_folder import buscar_carpeta_en_pagina
from scrapers.linkedin_modules.linkedin_pagination import paginar_y_buscar_carpeta
import os
import time
from dotenv import load_dotenv
from conexion import conn, cursor

TIEMPO_ESPERA_CORTO = 1
TIEMPO_ESPERA_MEDIO = 2
TIEMPO_ESPERA_PAGINA = 3

def guardar_proyecto_carpeta(tipo_carpeta, nombre_proyecto):
    try:
        cursor.execute("""
            INSERT INTO carpetas (tipo_carpeta, nombre_proyecto)
            VALUES (%s, %s)
            ON CONFLICT (tipo_carpeta, nombre_proyecto) DO NOTHING
        """, (tipo_carpeta, nombre_proyecto))
        conn.commit()
    except Exception as e:
        print(f"Error al guardar proyecto {nombre_proyecto} en carpeta {tipo_carpeta}: {e}")

def extraer_proyectos_carpeta(driver, carpeta):
    proyectos = []
    try:
        # Esperar a que cargue la lista de proyectos
        time.sleep(TIEMPO_ESPERA_MEDIO)
        
        # Obtener todos los elementos de proyecto
        elementos_proyecto = driver.find_elements("css selector", "a.saved-search-card__title-link")
        
        for elemento in elementos_proyecto:
            nombre_proyecto = elemento.text.strip()
            if nombre_proyecto:
                proyectos.append(nombre_proyecto)
                
    except Exception as e:
        print(f"Error extrayendo proyectos de la carpeta {carpeta}: {e}")
    
    return proyectos

def scraper_carpetas():
    load_dotenv()
    EMAIL = os.getenv("LINKEDIN_USER")
    PASSWORD = os.getenv("LINKEDIN_PASS")

    if not EMAIL or not PASSWORD:
        print("❌ Faltan credenciales de LinkedIn.")
        return False

    CARPETAS = ["POSGRADOS TENDENCIA", "CARRERAS PREGRADO"]
    user_data_dir = r"C:\Users\User\Documents\TRABAJO - UDLA\Estudio-Tendencia\profile"
    profile_directory = "Default"
    
    limpiar_singleton_lock(user_data_dir, profile_directory)
    options = crear_opciones_chrome(user_data_dir, profile_directory)
    driver = iniciar_driver(options)
    
    try:
        if not login_linkedin(driver, EMAIL, PASSWORD):
            return False

        url = "https://www.linkedin.com/insights/saved?reportType=talent&tab=folders"
        driver.get(url)
        time.sleep(TIEMPO_ESPERA_MEDIO)

        for carpeta in CARPETAS:
            print(f"\n=== Procesando carpeta: {carpeta} ===")
            
            encontrada = paginar_y_buscar_carpeta(
                driver, 
                carpeta, 
                buscar_carpeta_en_pagina,
                url,
                TIEMPO_ESPERA_CORTO,
                TIEMPO_ESPERA_MEDIO
            )

            if not encontrada:
                print(f"❌ No se encontró la carpeta '{carpeta}'")
                continue

            # Extraer proyectos de la carpeta actual
            proyectos = extraer_proyectos_carpeta(driver, carpeta)
            
            # Guardar cada proyecto en la base de datos
            for proyecto in proyectos:
                guardar_proyecto_carpeta(carpeta, proyecto)
                print(f"✓ Guardado: {proyecto} en {carpeta}")

            # Volver a la página principal de carpetas
            driver.get(url)
            time.sleep(TIEMPO_ESPERA_PAGINA)

        return True

    except Exception as e:
        print(f"Error en el scraper: {e}")
        return False
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    scraper_carpetas()