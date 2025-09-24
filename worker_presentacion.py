import os
import sys
import time
import dropbox
import psycopg2

# Configurar variables de entorno para evitar conflictos de rutas
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

from conexion import conn, cursor
from tools.generar_grafico_radar import generar_grafico_radar_desde_bd
from tools.generar_reporte_pptx import generar_reporte

def procesar_presentacion_queue():
    while True:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, proyecto_id FROM presentation_queue
                WHERE status = 'queued'
                ORDER BY created_at ASC
            """)
            pendientes = cur.fetchall()
        if not pendientes:
            print("No hay presentaciones en cola. Esperando...")
            time.sleep(10)
            continue
        for item in pendientes:
            queue_id, proyecto_id = item
            print(f"Procesando presentación para proyecto_id={proyecto_id} (queue_id={queue_id})")
            try:
                # Marcar como started
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='running', started_at=CURRENT_TIMESTAMP WHERE id=%s", (queue_id,))
                    conn.commit()
                # Generar gráfico radar y calcular viabilidad
                ruta_img = f"db/imagenes/grafico_radar_{proyecto_id}.png"
                viabilidad = generar_grafico_radar_desde_bd(proyecto_id, ruta_img)
                # Generar presentación PPTX pasando viabilidad
                generar_reporte(proyecto_id, viabilidad)
                # Buscar el archivo generado
                # Obtener el nombre del archivo generado dinámicamente
                with conn.cursor() as cur:
                    cur.execute("SELECT nombre_programa FROM datos_solicitud WHERE proyecto_id=%s", (proyecto_id,))
                    row = cur.fetchone()
                if row and row[0]:
                    nombre_archivo = f"{row[0].replace(' ', '_')}.pptx"
                else:
                    nombre_archivo = f"Presentacion_{proyecto_id}.pptx"
                output_path = os.path.join('db/presentaciones', nombre_archivo)
                if not os.path.exists(output_path):
                    raise FileNotFoundError(f"No se encontró el archivo PPTX generado: {output_path}")
                # Leer archivo como binario y guardar en la base de datos
                with open(output_path, 'rb') as f:
                    file_data = f.read()
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE presentation_queue SET status='finished', finished_at=CURRENT_TIMESTAMP, file_name=%s, file_data=%s WHERE id=%s
                    """, (nombre_archivo, psycopg2.Binary(file_data), queue_id))
                    conn.commit()
                print(f"Presentación para proyecto_id={proyecto_id} guardada en la base de datos correctamente.")
            except Exception as e:
                print(f"Error procesando presentación para proyecto_id={proyecto_id}: {e}")
                conn.rollback()  # <-- Añade rollback aquí
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='error', error=%s WHERE id=%s", (str(e), queue_id))
                    conn.commit()
        time.sleep(5)

if __name__ == "__main__":
    procesar_presentacion_queue()
