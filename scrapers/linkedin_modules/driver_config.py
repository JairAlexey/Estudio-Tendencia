import undetected_chromedriver as uc
import os
import time
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIEMPO_ESPERA_CORTO = 3   # Increased from 1 to 3
TIEMPO_ESPERA_MEDIO = 5   # Increased from 2 to 5
TIEMPO_ESPERA_LARGO = 8   # New longer wait time

def limpiar_perfil_completo(user_data_dir, profile_directory, espera_inicial=5, espera_recreacion=3):
    """
    Elimina completamente la carpeta de perfil y la vuelve a crear.
    Se ejecuta al inicio de cada proyecto para limpiar el estado del navegador.
    
    Args:
        user_data_dir: Directorio base del perfil de Chrome
        profile_directory: Nombre del directorio del perfil específico
        espera_inicial: Tiempo de espera antes de iniciar la limpieza
        espera_recreacion: Tiempo de espera después de recrear la carpeta
    """
    print(f"🧹 Iniciando limpieza completa del perfil de Chrome...")
    
    # Espera inicial para evitar conflictos con otros procesos
    if espera_inicial > 0:
        print(f"   Esperando {espera_inicial}s antes de limpiar perfil...")
        time.sleep(espera_inicial)
    
    full_profile_path = os.path.join(user_data_dir, profile_directory)
    
    try:
        # Verificar si la carpeta existe
        if os.path.exists(full_profile_path):
            print(f"   Eliminando carpeta de perfil: {full_profile_path}")
            
            # Intentar eliminar archivos de bloqueo primero
            try:
                singleton_lock = os.path.join(full_profile_path, "SingletonLock")
                if os.path.exists(singleton_lock):
                    os.remove(singleton_lock)
                    print(f"   Archivo SingletonLock eliminado")
            except Exception as e:
                print(f"   Advertencia al eliminar SingletonLock: {e}")
            
            # Eliminar toda la carpeta del perfil
            for intento in range(3):  # Hasta 3 intentos
                try:
                    shutil.rmtree(full_profile_path, ignore_errors=True)
                    
                    # Verificar que se eliminó completamente
                    if not os.path.exists(full_profile_path):
                        print(f"   ✅ Carpeta de perfil eliminada exitosamente")
                        break
                    else:
                        print(f"   Intento {intento + 1}: Carpeta aún existe, reintentando...")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"   Error en intento {intento + 1} de eliminación: {e}")
                    if intento < 2:  # Si no es el último intento
                        time.sleep(2)
                        continue
                    else:
                        print(f"   ⚠️ No se pudo eliminar completamente la carpeta después de 3 intentos")
        else:
            print(f"   Carpeta de perfil no existe: {full_profile_path}")
        
        # Recrear la estructura de directorios
        print(f"   Recreando estructura de directorios...")
        os.makedirs(full_profile_path, exist_ok=True)
        
        # Espera después de recrear para estabilizar
        if espera_recreacion > 0:
            print(f"   Esperando {espera_recreacion}s después de recrear perfil...")
            time.sleep(espera_recreacion)
        
        print(f"✅ Limpieza completa del perfil finalizada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza completa del perfil: {e}")
        return False

def limpiar_singleton_lock(user_data_dir, profile_directory):
    """
    Función existente para limpiar solo el archivo de bloqueo.
    Mantenida para compatibilidad con código existente.
    """
    full_profile_path = os.path.join(user_data_dir, profile_directory)
    singleton_lock = os.path.join(full_profile_path, "SingletonLock")
    if os.path.exists(singleton_lock):
        print("Eliminando archivo de bloqueo previo (SingletonLock)...")
        try:
            os.remove(singleton_lock)
            print("✅ SingletonLock eliminado")
        except Exception as e:
            print(f"⚠️ Error eliminando SingletonLock: {e}")

def crear_opciones_chrome(user_data_dir, profile_directory):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--profile-directory={profile_directory}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-features=EnableChromeSignin")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    return options

def iniciar_driver(options):
    return uc.Chrome(options=options)

def login_linkedin(driver, email, password, max_intentos=3):
    """
    Intenta hacer login en LinkedIn con reintentos automáticos
    """
    for intento in range(max_intentos):
        print(f"Intento de login {intento + 1}/{max_intentos}...")
        
        try:
            # Navegar a la página de login
            print("Abriendo LinkedIn Login...")
            driver.get("https://www.linkedin.com/login")
            time.sleep(TIEMPO_ESPERA_MEDIO)

            # Verificar si ya estamos logueados
            if "feed" in driver.current_url or "mynetwork" in driver.current_url:
                print("Ya estabas logueado. Sesión activa detectada.")
                return True

            # Verificar que estamos en la página de login
            if "login" not in driver.current_url:
                print(f"No estamos en la página de login. URL actual: {driver.current_url}")
                if intento < max_intentos - 1:
                    time.sleep(TIEMPO_ESPERA_LARGO)
                    continue
                else:
                    return False

            print("Iniciando sesión en LinkedIn...")
            
            # Esperar y encontrar campos de login con reintentos
            campo_usuario = None
            campo_contrasena = None
            
            # Intentar encontrar campos múltiples veces
            for sub_intento in range(3):
                try:
                    campo_usuario = WebDriverWait(driver, TIEMPO_ESPERA_LARGO).until(
                        EC.presence_of_element_located((By.ID, "username"))
                    )
                    campo_contrasena = WebDriverWait(driver, TIEMPO_ESPERA_LARGO).until(
                        EC.presence_of_element_located((By.ID, "password"))
                    )
                    break
                except Exception as e:
                    print(f"Sub-intento {sub_intento + 1}: Error encontrando campos - {e}")
                    if sub_intento < 2:
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                        continue
                    else:
                        raise

            if not campo_usuario or not campo_contrasena:
                print("No se pudieron encontrar los campos de login")
                if intento < max_intentos - 1:
                    time.sleep(TIEMPO_ESPERA_LARGO)
                    continue
                else:
                    return False

            # Limpiar y llenar campos con reintentos
            print("Llenando credenciales...")
            
            # Campo de usuario
            for sub_intento in range(3):
                try:
                    campo_usuario.clear()
                    time.sleep(TIEMPO_ESPERA_CORTO)
                    campo_usuario.send_keys(email)
                    time.sleep(TIEMPO_ESPERA_CORTO)
                    
                    # Verificar que se escribió correctamente
                    if campo_usuario.get_attribute("value") == email:
                        break
                    elif sub_intento < 2:
                        print(f"Reintentando escritura de email (intento {sub_intento + 1})")
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                        continue
                except Exception as e:
                    print(f"Error escribiendo email: {e}")
                    if sub_intento < 2:
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                        continue

            # Campo de contraseña
            for sub_intento in range(3):
                try:
                    campo_contrasena.clear()
                    time.sleep(TIEMPO_ESPERA_CORTO)
                    campo_contrasena.send_keys(password)
                    time.sleep(TIEMPO_ESPERA_CORTO)
                    break
                except Exception as e:
                    print(f"Error escribiendo contraseña: {e}")
                    if sub_intento < 2:
                        time.sleep(TIEMPO_ESPERA_MEDIO)
                        continue

            # Enviar formulario
            print("Enviando formulario de login...")
            campo_contrasena.send_keys(Keys.RETURN)
            
            # Esperar más tiempo para el procesamiento del login
            time.sleep(TIEMPO_ESPERA_LARGO)
            
            # Verificar éxito del login con múltiples checks
            login_exitoso = False
            for check in range(5):  # Verificar hasta 5 veces
                current_url = driver.current_url
                print(f"Check {check + 1}: URL actual = {current_url}")
                
                if any(path in current_url for path in ["feed", "mynetwork", "dashboard", "talent"]):
                    print("✓ Sesión iniciada correctamente.")
                    login_exitoso = True
                    break
                elif "challenge" in current_url or "verify" in current_url:
                    print("⚠️ Se requiere verificación adicional. Revisa tu email o dispositivo.")
                    return False
                elif "login" in current_url and check < 4:
                    print(f"Aún en página de login, esperando más... ({TIEMPO_ESPERA_LARGO}s)")
                    time.sleep(TIEMPO_ESPERA_LARGO)
                    continue
                else:
                    break
            
            if login_exitoso:
                return True
            else:
                print(f"Login no exitoso en intento {intento + 1}. URL final: {driver.current_url}")
                if intento < max_intentos - 1:
                    print(f"Esperando {TIEMPO_ESPERA_LARGO * 2}s antes del siguiente intento...")
                    time.sleep(TIEMPO_ESPERA_LARGO * 2)
                    continue

        except Exception as e:
            print(f"Error durante el login (intento {intento + 1}): {e}")
            if intento < max_intentos - 1:
                print(f"Esperando {TIEMPO_ESPERA_LARGO}s antes del siguiente intento...")
                time.sleep(TIEMPO_ESPERA_LARGO)
                continue
            else:
                print("Todos los intentos de login fallaron.")
                return False

    print("❌ Login fallido después de todos los intentos.")
    return False
