import os
import sys
import time
import traceback

# Configurar variables de entorno para evitar conflictos de rutas en Windows
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'profile')

def reset_profile_dir():
    import shutil
    if os.path.exists(PROFILE_DIR):
        try:
            shutil.rmtree(PROFILE_DIR)
        except Exception as e:
            print(f"Error limpiando profile_dir: {e}")
    os.makedirs(PROFILE_DIR, exist_ok=True)

# Llamar a la función al inicio del script
# reset_profile_dir()

from conexion import conn
from scrapers.carpetas_linkedin import scraper_carpetas

SLEEP_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "5"))

def fetch_next_job():
    """Obtiene el siguiente trabajo de la cola"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, tipo_carpeta
            FROM carpetas_queue
            WHERE status = 'queued'
            ORDER BY created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
        row = cur.fetchone()
        if row:
            return {"id": row[0], "tipo_carpeta": row[1]}
    return None

def mark_job_running(job_id):
    """Marca un trabajo como en ejecución"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE carpetas_queue
            SET status = 'running',
                started_at = CURRENT_TIMESTAMP,
                tries = tries + 1
            WHERE id = %s
        """, (job_id,))
        conn.commit()

def mark_job_completed(job_id):
    """Marca un trabajo como completado"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE carpetas_queue
            SET status = 'completed',
                finished_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (job_id,))
        conn.commit()

def mark_job_failed(job_id, error):
    """Marca un trabajo como fallido"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE carpetas_queue
            SET status = 'error',
                finished_at = CURRENT_TIMESTAMP,
                error = %s
            WHERE id = %s
        """, (error, job_id))
        conn.commit()

def process_job(job):
    """Procesa un trabajo de actualización de carpetas"""
    tipo_carpeta = job.get('tipo_carpeta')
    print(f"\n📋 Nuevo trabajo de carpetas detectado:")
    print(f"   Job ID: {job['id']}")
    print(f"   Tipo de carpeta: {tipo_carpeta if tipo_carpeta else 'N/A'}")

    print(f"\n{'='*60}")
    print(f"🚀 INICIANDO PROCESAMIENTO DE CARPETAS PARA JOB {job['id']}")
    print(f"   Tipo de carpeta: {tipo_carpeta if tipo_carpeta else 'N/A'}")
    print(f"{'='*60}")

    try:
        print(f"📂 Paso 1: Ejecutando scraper de carpetas...")
        mark_job_running(job['id'])

        # Ejecutar el scraper de carpetas con el tipo de carpeta específico
        if scraper_carpetas(tipo_carpeta=tipo_carpeta):
            mark_job_completed(job['id'])
            print(f"\n✅ JOB {job['id']} COMPLETADO EXITOSAMENTE")
            print(f"   Job {job['id']} marcado como completado")
            print(f"{'='*60}")
        else:
            mark_job_failed(job['id'], "El scraper retornó False")
            print(f"\n❌ JOB {job['id']} FALLÓ")
            print(f"   Job {job['id']} marcado como error")
            print(f"   Error: El scraper retornó False")
            print(f"{'='*60}")

    except Exception as e:
        error_msg = f"Error procesando job {job['id']}: {str(e)}\n{traceback.format_exc()}"
        print(f"\n❌ JOB {job['id']} FALLÓ")
        print(f"   Job {job['id']} marcado como error")
        print(f"   Error: {str(e)}")
        print(f"{'='*60}")
        mark_job_failed(job['id'], error_msg)

def main():
    print("🔄 Worker Carpetas iniciado")
    print(f"   Tiempo de inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Escuchando cola 'carpetas_queue'...")
    print("   ⚙️ Configurado para procesar carpetas al recibir trabajos")

    last_no_job_print = 0
    NO_JOB_PRINT_INTERVAL = 300  # segundos (5 minutos)
    first_no_job = True

    try:
        while True:
            job = fetch_next_job()
            if not job:
                now = time.time()
                if first_no_job or (now - last_no_job_print > NO_JOB_PRINT_INTERVAL):
                    print("😴 No hay trabajos de carpetas en cola, esperando...")
                    last_no_job_print = now
                    first_no_job = False
                time.sleep(SLEEP_SECONDS)
                continue
            first_no_job = True  # Reset para la próxima vez que no haya trabajos
            process_job(job)
            print(f"\n⏸️ Pausa de 5 segundos antes de revisar la cola nuevamente...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Worker de carpetas detenido por el usuario. Cerrando de forma segura...")

if __name__ == "__main__":
    main()