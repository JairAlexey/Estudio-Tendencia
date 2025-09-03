import os
import sys
import time
import shutil
import os

PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'profile')

def reset_profile_dir():
    if os.path.exists(PROFILE_DIR):
        shutil.rmtree(PROFILE_DIR)
    os.makedirs(PROFILE_DIR)

# Llamar a la función al inicio del script
reset_profile_dir()
import traceback
import subprocess
from scrapers.linkedin_modules.linkedin_database import (
    fetch_next_job,
    mark_job_running,
    mark_job_completed,
    mark_job_failed,
)
from conexion import conn


SLEEP_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "5"))


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
        print(f"[worker] Job {job_id} iniciado (proyecto_id={proyecto_id})")
        rc1, out1, err1 = run_subprocess(os.path.join("scrapers", "linkedin.py"), proyecto_id)
        if rc1 != 0:
            raise RuntimeError(f"linkedin.py fallo rc={rc1}: {err1[:500]}")
        rc2, out2, err2 = run_subprocess(os.path.join("scrapers", "semrush.py"), proyecto_id)
        if rc2 != 0:
            raise RuntimeError(f"semrush.py fallo rc={rc2}: {err2[:500]}")
        mark_job_completed(job_id)
        print(f"[worker] Job {job_id} completado ✔")
    except Exception as e:
        tb = traceback.format_exc()
        mark_job_failed(job_id, f"{e}\n{tb}")
        print(f"[worker] Job {job_id} fallo ✖: {e}")

def main():
    print("Worker iniciado. Escuchando cola 'scraper_queue'...")
    while True:
        job = fetch_next_job()
        if not job:
            time.sleep(SLEEP_SECONDS)
            continue
        print(f"Procesando job {job['id']} (proyecto_id={job['proyecto_id']})")
        process_job(job)


if __name__ == "__main__":
    main()


