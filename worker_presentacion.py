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
    while True:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, proyecto_id, tipo_reporte FROM presentation_queue
                WHERE status = 'queued'
                ORDER BY created_at ASC
            """)
            pendientes = cur.fetchall()
        if not pendientes:
            print("No hay presentaciones en cola. Esperando...")
            time.sleep(10)
            continue
        for item in pendientes:
            queue_id, proyecto_id, tipo_reporte = item
            tipo_reporte = tipo_reporte or 'viabilidad'  # Valor por defecto si es NULL
            print(f"Procesando presentación tipo '{tipo_reporte}' para proyecto_id={proyecto_id} (queue_id={queue_id})")
            try:
                # Marcar como started
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='running', started_at=CURRENT_TIMESTAMP WHERE id=%s", (queue_id,))
                    conn.commit()
                
                # Generar gráfico radar y calcular viabilidad (solo para reportes de viabilidad)
                viabilidad = None
                output_path = None
                
                if tipo_reporte == 'viabilidad':
                    ruta_img = f"files/imagenes/grafico_radar_{proyecto_id}.png"
                    viabilidad = generar_grafico_radar_desde_bd(proyecto_id, ruta_img)
                    # Generar presentación PPTX según el tipo y recibir la ruta donde se guardó
                    output_path = generar_reporte(proyecto_id, viabilidad)
                elif tipo_reporte == 'mercado':
                    # Generar presentación de mercado y recibir la ruta
                    output_path = generar_reporte_mercado(proyecto_id)
                else:
                    raise ValueError(f"Tipo de reporte desconocido: {tipo_reporte}")
                
                # Verificar si se generó la presentación
                if not output_path or not os.path.exists(output_path):
                    # Obtener el nombre del archivo esperado dinámicamente
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
                
                # Leer archivo como binario y guardar en la base de datos
                with open(output_path, 'rb') as f:
                    file_data = f.read()
                
                # Extraer solo el nombre del archivo sin la ruta
                nombre_archivo = os.path.basename(output_path)
                
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE presentation_queue SET status='finished', finished_at=CURRENT_TIMESTAMP, file_name=%s, file_data=%s WHERE id=%s
                    """, (nombre_archivo, psycopg2.Binary(file_data), queue_id))
                    conn.commit()
                print(f"Presentación '{tipo_reporte}' para proyecto_id={proyecto_id} guardada en la base de datos correctamente.")
            except Exception as e:
                print(f"Error procesando presentación para proyecto_id={proyecto_id}: {e}")
                conn.rollback()
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='error', error=%s WHERE id=%s", (str(e), queue_id))
                    conn.commit()
        time.sleep(5)

if __name__ == "__main__":
    procesar_presentacion_queue()
