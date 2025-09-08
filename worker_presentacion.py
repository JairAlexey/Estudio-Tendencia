import os
import sys
import time
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
                    cur.execute("UPDATE presentation_queue SET status='running', started_at=GETDATE() WHERE id=?", (queue_id,))
                    conn.commit()
                # Generar gráfico radar
                ruta_img = f"db/imagenes/grafico_radar_{proyecto_id}.png"
                generar_grafico_radar_desde_bd(proyecto_id, ruta_img)
                # Generar presentación PPTX
                generar_reporte(proyecto_id)
                # Buscar el archivo generado
                # Obtener el nombre del archivo generado dinámicamente
                with conn.cursor() as cur:
                    cur.execute("SELECT nombre_programa FROM datos_solicitud WHERE proyecto_id=?", (proyecto_id,))
                    row = cur.fetchone()
                if row and row[0]:
                    nombre_archivo = f"{row[0].replace(' ', '_')}.pptx"
                else:
                    nombre_archivo = f"Presentacion_{proyecto_id}.pptx"
                output_path = os.path.join('db', nombre_archivo)
                if not os.path.exists(output_path):
                    raise FileNotFoundError(f"No se encontró el archivo PPTX generado: {output_path}")
                # Leer el archivo PPTX como binario
                with open(output_path, 'rb') as f:
                    pptx_data = f.read()
                # Guardar en la base de datos
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE presentation_queue SET status='finished', finished_at=GETDATE(), pptx_file=?, file_name=? WHERE id=?
                    """, (pptx_data, nombre_archivo, queue_id))
                    conn.commit()
                print(f"Presentación para proyecto_id={proyecto_id} guardada correctamente.")
            except Exception as e:
                print(f"Error procesando presentación para proyecto_id={proyecto_id}: {e}")
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='error', error=? WHERE id=?", (str(e), queue_id))
                    conn.commit()
        time.sleep(5)

if __name__ == "__main__":
    procesar_presentacion_queue()
