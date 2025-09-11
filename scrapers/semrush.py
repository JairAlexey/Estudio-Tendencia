import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import sys

# Importar funciones de la base de datos
from scrapers.linkedin_modules.linkedin_database import (
    extraer_datos_tabla,
    guardar_datos_sql,
)


def parse_k_notation(valor_str: str) -> float:
    """
    Convierte cadenas como '3,6K' => 3600, '1,3K' => 1300, '9.290' => 9290, etc.
    Retorna un float (puedes cambiarlo a int si prefieres).
    """
    original_str = valor_str  # Guardar el original para debugging
    
    try:
        valor_str = valor_str.strip().upper().replace(".", "").replace(",", ".")
        
        print(f"    parse_k_notation: '{original_str}' -> '{valor_str}'")
        
        if "K" in valor_str:
            # Ejemplo: '3.6K' => '3.6', multiplicamos *1000
            valor_str = valor_str.replace("K", "")
            print(f"    Despues de quitar K: '{valor_str}'")
            try:
                resultado = float(valor_str) * 1000
                print(f"    Resultado K: {resultado}")
                return resultado
            except ValueError as e:
                print(f"    Error convirtiendo '{valor_str}' a float: {e}")
                return 0
        else:
            # Sin K, solo convertir directamente
            try:
                resultado = float(valor_str)
                print(f"    Resultado directo: {resultado}")
                return resultado
            except ValueError as e:
                print(f"    Error convirtiendo '{valor_str}' a float: {e}")
                return 0
    except Exception as e:
        print(f"    Error general en parse_k_notation con '{original_str}': {e}")
        return 0


def buscar_carrera_semrush(driver, carrera):
    """
    Funcion auxiliar para buscar una carrera especifica en Semrush
    Retorna True si la busqueda fue exitosa, False en caso contrario
    """
    try:
        print(f"Localizando campo de busqueda...")
        time.sleep(4)  # Esperar a que la pagina cargue completamente
        # Localizar el div con contenteditable
        input_div = driver.find_element(
            By.CSS_SELECTOR, 'div[data-slate-editor="true"]'
        )
        input_div.click()
        time.sleep(1)
        
        print(f"Escribiendo carrera: '{carrera}'")
        # Limpiar el campo primero
        input_div.send_keys(Keys.CONTROL + 'a')
        time.sleep(0.5)
        input_div.send_keys(Keys.DELETE)
        time.sleep(0.5)

        # Escribir la carrera caracter por caracter
        for ch in carrera:
            input_div.send_keys(ch)
            time.sleep(0.05)  # pequeno delay para cada caracter

        time.sleep(1)
        print(f"Texto escrito: '{input_div.text.strip()}'")

        # Buscar el boton "Buscar" con diferentes metodos
        print(f"Buscando boton de busqueda...")
        boton_buscar = None
        
        # Metodo 1: Por texto del span
        try:
            boton_buscar = driver.find_element(By.XPATH, "//span[contains(text(), 'Buscar')]")
            print("Boton encontrado por texto 'Buscar'")
        except:
            pass
        
        # Metodo 2: Por tipo de boton
        if not boton_buscar:
            try:
                boton_buscar = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                print("Boton encontrado por tipo submit")
            except:
                pass
        
        # Metodo 3: Por clase o atributo
        if not boton_buscar:
            try:
                boton_buscar = driver.find_element(By.CSS_SELECTOR, '[class*="search"] button, [class*="submit"] button')
                print("Boton encontrado por clase")
            except:
                pass
        
        if boton_buscar:
            boton_buscar.click()
            print(f"Busqueda iniciada para: {carrera}")
        else:
            # Si no encontramos el boton, intentar con Enter
            print("No se encontro boton, intentando con Enter...")
            input_div.send_keys(Keys.RETURN)
            
        # Esperar a que la pagina actualice
        time.sleep(5)
        
        # Verificar que la busqueda se realizo
        current_url = driver.current_url
        if "keyword" in current_url.lower() or len(current_url) > 60:  # URL cambio
            print(f"Busqueda completada - URL: {current_url[:80]}...")
            return True
        else:
            print(f"La URL no cambio mucho, puede que la busqueda no se haya completado")
            return False
            
    except Exception as e:
        print("No se pudo enviar la carrera o hacer clic en 'Buscar':", e)
        return False


def extraer_datos_semrush(driver, carrera):
    """
    Extrae los datos de Semrush de forma directa y fluida:
    - Vision General: span.kwo-widget-total[data-testid="volume-total"]
    - Si hay valor, navega a Magic Tool y extrae:
        - Palabras: div.sm-keywords-table-header__item-value[data-testid="all-keywords"]
        - Volumen: div.sm-keywords-table-header__item-value[data-testid="total-volume"]
    """
    time.sleep(6)  # Esperar carga inicial

    # 1. VISION GENERAL
    vision_general = 0
    try:
        elem = driver.find_element(By.CSS_SELECTOR, 'span.kwo-widget-total[data-testid="volume-total"]')
        vision_general_str = elem.text.strip()
        if not vision_general_str or vision_general_str.lower() in ['n/d', 'n/a', '-', '--', '', 'sin datos', 'no data']:
            print("Vision General no disponible o N/D, pero continuando con Magic Tool...")
            vision_general = 0
        else:
            vision_general = parse_k_notation(vision_general_str)
            print(f"Vision General: {vision_general_str} -> {vision_general}")
    except Exception as e:
        print(f"No se encontro Vision General ({str(e)[:50]}...), pero continuando con Magic Tool...")
        vision_general = 0

    # 2. NAVEGAR A MAGIC TOOL (SIEMPRE, independientemente de Vision General)
    print("Navegando a Magic Tool para verificar otros datos...")
    try:
        magic_tool_button = driver.find_element(
            By.CSS_SELECTOR, 'srf-sidebar-list-item[label="Keyword Magic Tool"]'
        )
        magic_tool_href = magic_tool_button.get_attribute("href")
        if magic_tool_href:
            driver.get(magic_tool_href)
            print("Navegando a Keyword Magic Tool...")
        else:
            print("No se encontro href de Magic Tool")
            # No devolver aqui, intentar con la URL actual
    except Exception as e:
        print(f"No se pudo encontrar/enlazar al 'Keyword Magic Tool': {e}")
        print("Intentando continuar en la pagina actual...")

    time.sleep(6)  # Esperar carga Magic Tool

    # 3. PALABRAS Y VOLUMEN TOTAL
    palabras = 0
    volumen = 0
    
    # Intentar extraer Palabras
    try:
        palabras_elem = driver.find_element(
            By.CSS_SELECTOR, 'div.sm-keywords-table-header__item-value[data-testid="all-keywords"]'
        )
        palabras_str = palabras_elem.text.strip()
        if palabras_str and any(char.isdigit() for char in palabras_str):
            palabras = parse_k_notation(palabras_str)
            print(f"Palabras: {palabras_str} -> {palabras}")
        else:
            print(f"Palabras encontradas pero valor no valido: '{palabras_str}'")
    except Exception as e:
        print(f"No se pudo extraer Palabras: {str(e)[:50]}...")

    # Intentar extraer Volumen
    try:
        volumen_elem = driver.find_element(
            By.CSS_SELECTOR, 'div.sm-keywords-table-header__item-value[data-testid="total-volume"]'
        )
        volumen_str = volumen_elem.text.strip()
        if volumen_str and any(char.isdigit() for char in volumen_str):
            volumen = parse_k_notation(volumen_str)
            print(f"Volumen: {volumen_str} -> {volumen}")
        else:
            print(f"Volumen encontrado pero valor no valido: '{volumen_str}'")
    except Exception as e:
        print(f"No se pudo extraer Volumen: {str(e)[:50]}...")

    # 4. VERIFICACION FINAL Y LOGGING DETALLADO
    datos_encontrados = []
    if vision_general > 0:
        datos_encontrados.append(f"Vision General: {vision_general}")
    if palabras > 0:
        datos_encontrados.append(f"Palabras: {palabras}")
    if volumen > 0:
        datos_encontrados.append(f"Volumen: {volumen}")

    if datos_encontrados:
        print(f"DATOS EXTRAIDOS EXITOSAMENTE: {', '.join(datos_encontrados)}")
    else:
        print("ADVERTENCIA: No se encontraron datos validos en ninguna metrica")
        print("Intentando busqueda de emergencia en la pagina actual...")
        
        # BUSQUEDA DE EMERGENCIA - buscar cualquier numero relevante en la pagina
        try:
            # Buscar elementos que podrian contener datos numericos
            all_numeric_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'K') or contains(text(), '.') or contains(text(), ',')]")
            emergency_candidates = []
            
            for elem in all_numeric_elements[:15]:  # Limitar la busqueda
                try:
                    text = elem.text.strip()
                    if (text and any(char.isdigit() for char in text) and 
                        len(text) < 20 and ('K' in text.upper() or '.' in text or ',' in text)):
                        emergency_candidates.append(text)
                except:
                    continue
            
            if emergency_candidates:
                print(f"Posibles datos encontrados en busqueda de emergencia: {emergency_candidates[:5]}")
                print("Sugerencia: Verificar manualmente si estos valores son relevantes")
            else:
                print("Busqueda de emergencia no encontro candidatos numericos")
                
        except Exception as emergency_e:
            print(f"Error en busqueda de emergencia: {emergency_e}")

    print(f"\nRESUMEN DE DATOS EXTRAIDOS:")
    print(f"   Vision General: {vision_general}")
    print(f"   Palabras: {palabras}")
    print(f"   Volumen: {volumen}")

    return vision_general, palabras, volumen


def semrush_scraper():
    # -----------------------------------------------------------------------------
    # CONFIGURACION: Cargar variables de entorno y definir parametros iniciales
    # -----------------------------------------------------------------------------
    
    load_dotenv()
    EMAIL = os.getenv("SEMRUSH_USER")
    PASSWORD = os.getenv("SEMRUSH_PASS")

    if not EMAIL or not PASSWORD:
        print("Faltan credenciales de Semrush. Verifica las variables de entorno SEMRUSH_USER y SEMRUSH_PASS.")
        return

    if len(sys.argv) < 2:
        print("Uso: python semrush.py <proyecto_id>")
        return
    proyecto_id = int(sys.argv[1])

    # CONFIGURACION
    user_data_dir = r"C:\Users\Alexey\Documents\TRABAJO - UDLA\Estudio-Tendencia\profile"
    profile_directory = "Default"

    # LIMPIEZA DEL LOCK
    full_profile_path = os.path.join(user_data_dir, profile_directory)
    singleton_lock = os.path.join(full_profile_path, "SingletonLock")
    if os.path.exists(singleton_lock):
        print("Eliminando archivo de bloqueo previo (SingletonLock)...")
        os.remove(singleton_lock)

    # OPCIONES DE CHROME
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_directory}")

    # LANZAR EL DRIVER (UNA SOLA VEZ)
    driver = uc.Chrome(options=options)

    try:
        # 1. INICIAR SESION EN SEMRUSH (UNA SOLA VEZ)
        driver.get("https://es.semrush.com/login/?src=header&redirect_to=%2F")
        time.sleep(1.5)

        if "login" not in driver.current_url:
            print("Sesion ya iniciada (no hace falta login).")
        else:
            print("Iniciando sesion en Semrush...")
            try:
                input_email = driver.find_element(By.ID, "email")
                input_password = driver.find_element(By.ID, "password")

                input_email.clear()
                input_email.send_keys(EMAIL)
                input_password.clear()
                input_password.send_keys(PASSWORD)

                input_password.send_keys(Keys.RETURN)
                time.sleep(10)

                if "login" in driver.current_url:
                    print("Parece que no se pudo iniciar sesion. Revisa tus credenciales.")
                    return
                else:
                    print("Sesion iniciada correctamente.")
            except Exception as e:
                print("Error al intentar loguearse:", e)
                return

        # 2. OBTENER CONFIGURACION DEL PROYECTO DESDE LA BASE DE DATOS
        proyecto_config = extraer_datos_tabla("reporteLinkedin", proyecto_id)
        if not proyecto_config:
            print(f"No se encontraron datos para el proyecto {proyecto_id}")
            return

        # Extraer la palabra clave para Semrush
        palabra_semrush = proyecto_config[0].get("PalabraSemrush")
        if not palabra_semrush:
            print(f"No se encontro la palabra clave para Semrush en el proyecto {proyecto_id}")
            return

        print(f"Palabra clave a buscar: {palabra_semrush}")

        # 3. PROCESAR LA PALABRA CLAVE
        try:
            # 4. IR A LA PAGINA DE KEYWORD OVERVIEW
            driver.get("https://es.semrush.com/analytics/keywordoverview/?db=ec")
            time.sleep(2)

            # 5. BUSCAR LA PALABRA CLAVE
            if not buscar_carrera_semrush(driver, palabra_semrush):
                print(f"No se pudo buscar la palabra clave '{palabra_semrush}' para el proyecto {proyecto_id}")
                return

            # 6. EXTRAER DATOS
            vision_general, palabras, volumen = extraer_datos_semrush(driver, palabra_semrush)
            
            # 7. GUARDAR DATOS EN LA BASE DE DATOS
            datos_para_guardar = [
                {
                    "VisionGeneral": str(vision_general),
                    "Palabras": palabras,
                    "Volumen": volumen,
                }
            ]

            try:
                guardar_datos_sql(datos_para_guardar, "semrush", proyecto_id)
                print(f"Datos guardados correctamente para el proyecto {proyecto_id}")
            except Exception as e:
                print(f"Error guardando datos en la base de datos para proyecto {proyecto_id}: {e}")

        except Exception as e:
            print(f"Error procesando proyecto {proyecto_id}: {e}")

    except Exception as main_e:
        print(f"Error general en el scraper: {main_e}")
    
    finally:
        try:
            driver.quit()
            print(f"\nProceso SEMrush finalizado para el proyecto {proyecto_id}.")
        except:
            pass


if __name__ == "__main__":
    semrush_scraper()
