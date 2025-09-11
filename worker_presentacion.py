import os
import sys
import time
import dropbox
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
                output_path = os.path.join('db/presentaciones', nombre_archivo)
                if not os.path.exists(output_path):
                    raise FileNotFoundError(f"No se encontró el archivo PPTX generado: {output_path}")
                # Subir el archivo a Dropbox
                dbx = dropbox.Dropbox('sl.u.AF8sij9Ig5isRKhhXFMmhKRNrskPP8wEosO7-c8Y23X7qA6KuiQGJXbx7XCPdSrFmUF9rvqclz4c9hC1GqrtVGi8N9lXYrNtGg2CcIeF8aAb8QYGMlw8AqmEtvPqR94DQ1U2PlyzFyM0cio7W_Oi0ZI9_KfvnAgXoz6Dy3ZVGGJ5im3IK8kYbFev8_r1Knz1yoKwV52n5XOPiRR4muNXhgyeXUuXTxP21Y_21PLSfNZ2Wr2eCnx4JTHFbnAqSCKnCkWZKVCmWgh7su6UW4u2ZOwcTs9KdnDon5jGhKciE0Fw7dVpqXiXC6iHyYEq0tPdEKdQuI4oUKkz8wq4F1Y90XoLI8Re2VrcK15ooBjoCie5TMV7FskNRzaSIHSxze1pWeS1vE9ww3eF0LupTZ0n6WbESpB2tj41dKPjbjX6pFZHikf9TubeYI-s545LG3wUAAnyKPEf4axFvhTxA2GSUjulzaXj9GybNmYWPS2bpXrZhaRwBHdb0HMn6d25zsoZLl7YXKR1bOKf21a-Vq4rvH-nn5iHAU65RIjSRTKo4oEw79Nljig22x-52gd6qUKGEApkyuIGlEWgKDOYl_KDYZ5VGH62eTQMwY5_Cs1HmwdVMw3m1W8q9QINUVR066Uisjn-AqWD8TC14kxK85uPJYFW2zgjIfaQPlCes7SfOL3F1qOb1QWPeAgJbHmY2pWLUCRjCUTgbFyOBgflegVHiWPkLJp40L6irqAErrLhLlujrgsOmPPgq-kq1wG2rZfY3r_cTtlyfPcyDW6i8NqD8T9CyvWENvscSQoy83yvc6oHP0EPOLH7yQYD2UA5rZ9Te7Ge0jrQnXPlHb1yqFuQ7lAq-EnMF6M1SHzsW4RcLA5OvM4XhgjWwFwZ8WAfw1CnQdnfVTRjSBL8w_N0aqWe5ty81TeeH3q3C6djmwZC6EUn_pd2f5pWZ_OmTGcMDJFaSHbCOKYgizB-6CNMYgmD7XTyAFKZROrUagLsn0Lp_-cZOLQulu1TgkIw0wkBVGGGb1HVIrqtfiqSPgLa3ImkcsOsARqPzWlrM7tyDCXI_Pdj1cu0UhVYuJzryNAggVMmNP_83tkkMC5F0RQkQUN3qStu-rHlMdSdJJQkFa2FEcVwq7o1CCzGAHRUE92COZrJfLtsERB_-FbOkq8tQsu03gHH5k9PW2aODl92azSG_7NkCbivI3FqDPdnXi2Ry8romWLqPZFP-yk6KbaLAbOIhvH_fkZtbxYRytUGDzpAp_ZDNOOsIiB1_lpKZBCl9GiNVhXyNSYYpfltN8kEAvNwswkXewYBXC05HHpajONTAN_03tKZHO6CXO5bWrWr9qr-QQsFCsnPaz08a1AiSORV75_nhKgi-rmI2AUbzp5dSOD3HOW3E2hb2Pw5T3avzamN5JD6X-NWEMMfA_oq9fA8pYAB_fGTgypmBKjQNnm8CDiBAU3036O__Qjw9rIh4r4Ir8s')
                dropbox_path = f"/presentaciones/{nombre_archivo}"
                with open(output_path, 'rb') as f:
                    dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                # Obtener enlace compartido
                shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                dropbox_url = shared_link_metadata.url.replace('?dl=0', '?dl=1')
                # Guardar el enlace en la base de datos
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE presentation_queue SET status='finished', finished_at=GETDATE(), dropbox_url=?, file_name=? WHERE id=?
                    """, (dropbox_url, nombre_archivo, queue_id))
                    conn.commit()
                print(f"Presentación para proyecto_id={proyecto_id} guardada en Dropbox correctamente.")
            except Exception as e:
                print(f"Error procesando presentación para proyecto_id={proyecto_id}: {e}")
                with conn.cursor() as cur:
                    cur.execute("UPDATE presentation_queue SET status='error', error=? WHERE id=?", (str(e), queue_id))
                    conn.commit()
        time.sleep(5)

if __name__ == "__main__":
    procesar_presentacion_queue()
