import subprocess
import re
import os

def get_chrome_version():
    """Obtiene la versión instalada de Google Chrome en Windows."""
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            return None
        output = subprocess.check_output([chrome_path, "--version"], stderr=subprocess.STDOUT)
        version = output.decode("utf-8")
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", version)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None

def get_chromedriver_version():
    """Obtiene la versión instalada de ChromeDriver en el entorno virtual."""
    try:
        output = subprocess.check_output(["chromedriver", "--version"], stderr=subprocess.STDOUT)
        version = output.decode("utf-8")
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", version)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None

def check_chrome_compatibility():
    """Verifica si la versión de Chrome coincide con la de ChromeDriver (solo el primer número)."""
    chrome_version = get_chrome_version()
    chromedriver_version = get_chromedriver_version()
    if not chrome_version or not chromedriver_version:
        return False, chrome_version, chromedriver_version
    # Solo comparar el primer número (mayor)
    chrome_major = chrome_version.split(".")[0]
    driver_major = chromedriver_version.split(".")[0]
    compatible = chrome_major == driver_major
    return compatible, chrome_version, chromedriver_version
