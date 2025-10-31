import os
import sys
import time
import shutil

# Configurar variables de entorno para evitar conflictos de rutas en Windows
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'profile')

def reset_profile_dir():
    if os.path.exists(PROFILE_DIR):
        shutil.rmtree(PROFILE_DIR)
    os.makedirs(PROFILE_DIR)

# NO llamar a la función al inicio del script - ahora se hará por proyecto
# reset_profile_dir()
import traceback
import subprocess
from scrapers.linkedin_modules.linkedin_database import (
    fetch_next_job,
    mark_job_running,
    mark_job_completed,
    mark_job_failed,
)
from scrapers.linkedin_modules.driver_config import limpiar_perfil_completo
from conexion import conn


SLEEP_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "5"))


def limpiar_perfil_proyecto(proyecto_id):
    """
    Limpia el perfil de Chrome al inicio de cada proyecto.
    Incluye esperas para no interferir con otros procesos.
    """
    print(f"🧹 Iniciando limpieza de perfil para proyecto {proyecto_id}...")
    
    try:
        # Usar la función optimizada del driver_config
        user_data_dir = PROFILE_DIR
        profile_directory = "Default"
        
        # limpieza_exitosa = limpiar_perfil_completo(
        #     user_data_dir, 
        #     profile_directory, 
        #     espera_inicial=3,  # Espera inicial antes de limpiar
        #     espera_recreacion=2  # Espera después de recrear
        # )
        # if limpieza_exitosa:
        #     print(f"✅ Perfil limpiado exitosamente para proyecto {proyecto_id}")
        # else:
        #     print(f"⚠️ Limpieza de perfil falló para proyecto {proyecto_id}, usando limpieza básica...")
        #     reset_profile_dir()
        # return limpieza_exitosa

        # Solo mostrar mensaje de omisión
        print(f"⚠️ Limpieza de perfil omitida por configuración (comentada en el código)")
        return True
        
    except Exception as e:
        print(f"❌ Error en limpieza de perfil para proyecto {proyecto_id}: {e}")
        # Fallback a limpieza básica
        # try:
        #     reset_profile_dir()
        #     print(f"✅ Limpieza básica aplicada como fallback")
        #     return True
        # except Exception as e2:
        #     print(f"❌ Error crítico en limpieza de perfil: {e2}")
        #     return False
        return True

def run_subprocess(module_path: str, proyecto_id: int) -> tuple[int, str, str]:
    project_root = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, module_path, str(proyecto_id)]
    print(f"[worker] Ejecutando: {' '.join(cmd)} (cwd={project_root})")
    env = os.environ.copy()
    # Asegurar PYTHONPATH para que el paquete 'scrapers' sea importable
    env["PYTHONPATH"] = project_root + (os.pathsep + env.get("PYTHONPATH", ""))
    # Forzar UTF-8 para evitar UnicodeEncodeError por emojis en stdout/stderr
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=project_root,
        env=env,
    )
    out, err = proc.communicate()
    if out:
        print(f"[stdout] {out}")
    if err:
        print(f"[stderr] {err}")
    return proc.returncode, out, err


def process_job(job):
    job_id = job["id"]
    proyecto_id = job["proyecto_id"]
    mark_job_running(job_id)
    try:
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO PROCESAMIENTO DEL PROYECTO {proyecto_id}")
        print(f"   Job ID: {job_id}")
        print(f"{'='*60}")
        
        # LIMPIAR PERFIL AL INICIO DE CADA PROYECTO
        print(f"📂 Paso 1: Limpieza de perfil de Chrome...")
        perfil_limpio = limpiar_perfil_proyecto(proyecto_id)
        
        if not perfil_limpio:
            print(f"⚠️ Advertencia: Limpieza de perfil no completamente exitosa, pero continuando...")
        
        # Espera adicional para estabilizar después de la limpieza
        print(f"⏸️ Esperando 5 segundos para estabilizar...")
        time.sleep(5)
        
        print(f"📡 Paso 2: Ejecutando LinkedIn scraper...")
        rc1, out1, err1 = run_subprocess(os.path.join("scrapers", "linkedin.py"), proyecto_id)
        if rc1 != 0:
            raise RuntimeError(f"linkedin.py fallo rc={rc1}: {err1[:500]}")
        
        # print(f"🔍 Paso 3: Ejecutando SEMrush scraper...")
        # rc2, out2, err2 = run_subprocess(os.path.join("scrapers", "semrush.py"), proyecto_id)
        # if rc2 != 0:
        #     raise RuntimeError(f"semrush.py fallo rc={rc2}: {err2[:500]}")
        
        mark_job_completed(job_id)
        print(f"\n✅ PROYECTO {proyecto_id} COMPLETADO EXITOSAMENTE")
        print(f"   Job {job_id} marcado como completado")
        print(f"{'='*60}")
        
    except Exception as e:
        tb = traceback.format_exc()
        mark_job_failed(job_id, f"{e}\n{tb}")
        print(f"\n❌ PROYECTO {proyecto_id} FALLÓ")
        print(f"   Job {job_id} marcado como fallido")
        print(f"   Error: {e}")
        print(f"{'='*60}")

# ...existing code...

def main():
    print("🔄 Worker Scraper iniciado")
    print(f"   Tiempo de inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Escuchando cola 'scraper_queue'...")
    print("   ⚙️ Configurado para limpiar perfil al inicio de cada proyecto")
    
    last_no_job_print = 0
    NO_JOB_PRINT_INTERVAL = 300  # segundos (5 minutos)
    first_no_job = True

    try:
        while True:
            job = fetch_next_job()
            if not job:
                now = time.time()
                if first_no_job or (now - last_no_job_print > NO_JOB_PRINT_INTERVAL):
                    print("😴 No hay trabajos en cola, esperando...")
                    last_no_job_print = now
                    first_no_job = False
                time.sleep(SLEEP_SECONDS)
                continue

            first_no_job = True  # Reset para la próxima vez que no haya trabajos

            print(f"\n📋 Nuevo trabajo detectado:")
            print(f"   Job ID: {job['id']}")
            print(f"   Proyecto ID: {job['proyecto_id']}")
            
            process_job(job)
            
            # Pausa entre proyectos para estabilidad
            print(f"\n⏸️ Pausa de 10 segundos antes del siguiente proyecto...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Worker detenido por el usuario. Cerrando de forma segura...")

if __name__ == "__main__":
    main()
