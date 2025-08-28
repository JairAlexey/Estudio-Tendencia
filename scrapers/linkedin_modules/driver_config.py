import undetected_chromedriver as uc
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

TIEMPO_ESPERA_CORTO = 1
TIEMPO_ESPERA_MEDIO = 2

def limpiar_singleton_lock(user_data_dir, profile_directory):
    full_profile_path = os.path.join(user_data_dir, profile_directory)
    singleton_lock = os.path.join(full_profile_path, "SingletonLock")
    if os.path.exists(singleton_lock):
        print("Eliminando archivo de bloqueo previo (SingletonLock)...")
        os.remove(singleton_lock)

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

def login_linkedin(driver, email, password):
    print("Abriendo LinkedIn Login...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(TIEMPO_ESPERA_CORTO)

    if "login" in driver.current_url:
        print("Iniciando sesión en LinkedIn...")
        try:
            campo_usuario = driver.find_element(By.ID, "username")
            campo_contrasena = driver.find_element(By.ID, "password")
            campo_usuario.clear()
            campo_usuario.send_keys(email)
            campo_contrasena.clear()
            campo_contrasena.send_keys(password + Keys.RETURN)
            time.sleep(TIEMPO_ESPERA_CORTO)
            if "linkedin.com/feed" in driver.current_url:
                print("Sesión iniciada correctamente.")
                return True
            else:
                print("No se redirigió al feed. Login fallido o requiere verificación.")
                driver.quit()
                return False
        except Exception as e:
            print(f"Error durante el login: {e}")
            driver.quit()
            return False
    else:
        print("Ya estabas logueado. Redirigido automáticamente.")
        return True
