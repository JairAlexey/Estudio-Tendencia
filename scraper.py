from scrapers.linkedin import linkedin_scraper
from scrapers.semrush import semrush_scraper
import subprocess
import sys
import os

# print("EJECUCION SCRAPERS")

# print("---Linkedin---")
# linkedin_scraper()

# print("---Semrush---")
# import time
# time.sleep(3)
# semrush_scraper()

# Lanzar Streamlit tras completar scrapers
try:
    print("Lanzando Streamlit app...")
    proyecto_id = None
    if len(sys.argv) > 1:
        proyecto_id = sys.argv[1]
    env = os.environ.copy()
    if proyecto_id is not None:
        env["PROJECT_ID"] = str(proyecto_id)
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, env=env)
except Exception as e:
    print(f"No se pudo lanzar Streamlit automáticamente: {e}")
