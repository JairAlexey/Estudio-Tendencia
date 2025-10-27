import os
import sys
import time
import psycopg2

# Configurar variables de entorno para evitar conflictos de rutas
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

from conexion import conn, cursor
from tools.generar_grafico_radar import generar_grafico_radar_desde_bd
from tools.generar_reporte_pptx import generar_reporte, generar_reporte_mercado

def procesar_presentacion_queue():
    print("🔄 Worker Presentación iniciado")
    print(f"   Tiempo de inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Escuchando cola 'presentation_queue'...")
    print("   ⚙️ Configurado para generar presentaciones al recibir trabajos")

    last_no_job_print = 0
    NO_JOB_PRINT_INTERVAL = 300  # segundos (5 minutos)
    first_no_job = True

    try:
        while True:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, proyecto_id, tipo_reporte FROM presentation_queue
                    WHERE status = 'queued'
                    ORDER BY created_at ASC
                """)
                pendientes = cur.fetchall()
            if not pendientes:
                now = time.time()
                if first_no_job or (now - last_no_job_print > NO_JOB_PRINT_INTERVAL):
                    print("😴 No hay presentaciones en cola, esperando...")
                    last_no_job_print = now
                    first_no_job = False
                time.sleep(10)
                continue
            first_no_job = True  # Reset para la próxima vez que no haya trabajos

            for item in pendientes:
                queue_id, proyecto_id, tipo_reporte = item
                tipo_reporte = tipo_reporte or 'viabilidad'  # Valor por defecto si es NULL
                print(f"\n📋 Nuevo trabajo de presentación detectado:")
                print(f"   Queue ID: {queue_id}")
                print(f"   Proyecto ID: {proyecto_id}")
                print(f"   Tipo de reporte: {tipo_reporte}")

                print(f"\n{'='*60}")
                print(f"🚀 INICIANDO PROCESAMIENTO DE PRESENTACIÓN PARA PROYECTO {proyecto_id}")
                print(f"   Queue ID: {queue_id}")
                print(f"{'='*60}")

                try:
                    print(f"📊 Paso 1: Generando presentación tipo '{tipo_reporte}'...")
                    # Marcar como started
                    with conn.cursor() as cur:
                        cur.execute("UPDATE presentation_queue SET status='running', started_at=CURRENT_TIMESTAMP WHERE id=%s", (queue_id,))
                        conn.commit()

                    viabilidad = None
                    output_path = None

                    if tipo_reporte == 'viabilidad':
                        ruta_img = f"files/imagenes/grafico_radar_{proyecto_id}.png"
                        viabilidad = generar_grafico_radar_desde_bd(proyecto_id, ruta_img)
                        output_path = generar_reporte(proyecto_id, viabilidad)
                    elif tipo_reporte == 'mercado':
                        output_path = generar_reporte_mercado(proyecto_id)
                    else:
                        raise ValueError(f"Tipo de reporte desconocido: {tipo_reporte}")

                    # Verificar si se generó la presentación
                    if not output_path or not os.path.exists(output_path):
                        with conn.cursor() as cur:
                            cur.execute("SELECT nombre_programa FROM datos_solicitud WHERE proyecto_id=%s", (proyecto_id,))
                            row = cur.fetchone()
                        if row and row[0]:
                            nombre_archivo = f"{row[0].replace(' ', '_')}_{tipo_reporte}.pptx"
                        else:
                            nombre_archivo = f"Presentacion_{proyecto_id}_{tipo_reporte}.pptx"
                        output_path = os.path.join('files/presentaciones', nombre_archivo)
                        if not os.path.exists(output_path):
                            raise FileNotFoundError(f"No se encontró el archivo PPTX generado: {output_path}")

                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    nombre_archivo = os.path.basename(output_path)

                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE presentation_queue SET status='finished', finished_at=CURRENT_TIMESTAMP, file_name=%s, file_data=%s WHERE id=%s
                        """, (nombre_archivo, psycopg2.Binary(file_data), queue_id))
                        conn.commit()
                    print(f"\n✅ PRESENTACIÓN '{tipo_reporte}' PARA PROYECTO {proyecto_id} GUARDADA EXITOSAMENTE")
                    print(f"   Queue {queue_id} marcada como finalizada")
                    print(f"{'='*60}")
                except Exception as e:
                    print(f"\n❌ PRESENTACIÓN PARA PROYECTO {proyecto_id} FALLÓ")
                    print(f"   Queue {queue_id} marcada como error")
                    print(f"   Error: {e}")
                    print(f"{'='*60}")
                    conn.rollback()
                    with conn.cursor() as cur:
                        cur.execute("UPDATE presentation_queue SET status='error', error=%s WHERE id=%s", (str(e), queue_id))
                        conn.commit()
            print(f"\n⏸️ Pausa de 5 segundos antes de revisar la cola nuevamente...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Worker de presentaciones detenido por el usuario. Cerrando de forma segura...")

if __name__ == "__main__":
    procesar_presentacion_queue()