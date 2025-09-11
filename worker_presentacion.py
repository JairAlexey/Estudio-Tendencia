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
                # Generar gráfico radar y calcular viabilidad
                ruta_img = f"db/imagenes/grafico_radar_{proyecto_id}.png"
                viabilidad = generar_grafico_radar_desde_bd(proyecto_id, ruta_img)
                # Generar presentación PPTX pasando viabilidad
                generar_reporte(proyecto_id, viabilidad)
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
                dbx = dropbox.Dropbox('sl.u.AF_9VBroYRGqeFRgKv3nxalBRymI78QVOQyzkou4EqaXbB01HaHwxsQe31n52EYc7245jnTbS2v_vpL_zkN2LBHJrmzNu7chlUWAeAL5BkjR66YZ9JxGXTq9He6TTUMImWMJdQjx8gmT38f-u95l2bqbFopxv8v6tYpBGWV1J0GgdJI3eyIvP3DM2km_cmKbv_rfySgjgPCSHiZCyH5WlHlsZrpYjmanG-c7KlsWzvX6daIh512JwMQOYXp7mI3WOhlhnflXT8X0Sb9TxPZqCBWBbAoHXUFclO2hUMJ5WTYjKqsCAfwhzuMWnovZ98lIWfRzZkjmrA5yUkSfVclrxHBNi0fFPdo_9W-2JIQ4YD_N8gst4NAWTeOHIYlZRH2RsMirX1tyv0DUgMix_UPgVwl9t2gspZGEm5-RCvODCkO2HcxYYF52i1xI2CGbOwYNmxjvdeoLT1r9vFwzJag2AQY8HcopTAeXqZOy_k6gVGENN-E6H1WZeUMQGKJDzkebrA9GvvnUPBi1pe8UDuKWLx97UgScyYhv5YgQG6_S4Nv98g_1Pe5l5Vy3y7uxgwRwOPsGx4qvzT0VsT9sWiZ46Xz_zXeEOEB72uGu70nNj3yOE6R2C4dxtcwOPTuL0mB52ahDg2Ky5aTaEoAmVk5zCNe-C5jQWDo0y6HwHOgHepeGAYuoqTFCwbHGvK39A5Tp2GuShVUnwc98eS4rXrS6mLiSmTanlepae1Z5Bn-umlmUJF4jkInEp1bf8sl-jU1jRlfV6A0POqL0UPD2PUEQoG_FXSMMLqrNAdeHHvGXHLThNSdbIvzDTJOYc1yY892vMSOTBnH_CviXH8dbsd_mGBz-9ewdjhTs05mCHb6JxepCZVF2-gHvoyH7oNqlqEeDQx4lg29OzilwOMFwFvv7Eu90nhSD7Qh69j7AOEdp5Yp1EGGBi58NGIcJQpt5SYPpDRJBJ6BXbwm1vjfFqbx80bWyNe0MWWeQaiDxbhfLa01d-FIr2R48WzWXFGJaJgTCW0cKcvKmcVAN0RwZRUD56-jxh_f_krivd6VianulrI7qg59GbbFM5DnsKHRsyYkhzfT-w1TVercA5xdgJ-zwaas0oDp-TvJY5G8DxjmGZ3j1EcuYZ2nkslrzyU2P8GygE_H71QHJmbHB57nOfoPEpoHbpCeSdkFIXqaUgJUAZVjJD-axd9QypTJ8nug3392e9aHUqymWHuj6eHHyaTB1yIdlXqq_IsEXP7TXzA2jykl51IQTfP3wtc3kVv6b8RXZxyF1VL91y-iVGhj5QutIPhVDIJc1ogqjUa5QJUSJbCWD-JEVL7s2WngkUTGXVXa5TPUOofdcnnXJh7A5cjCYr0d4Fcm6R-5eqq0jxugAHVoB_Ikp_Mpkhv8xtTCtFpEbY_hveZYcZXsgvbvVin0mf4QAnl0yigoIB_C0RQmCQ6Gz4C1RG6eOokpWZW1tLM9oRdanwW35U3UQ3VrANIMj0cEO')
                dropbox_path = f"/presentaciones/{nombre_archivo}"
                with open(output_path, 'rb') as f:
                    dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
                # Obtener enlace compartido, manejar si ya existe
                try:
                    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
                    dropbox_url = shared_link_metadata.url.replace('?dl=0', '?dl=1')
                except dropbox.exceptions.ApiError as e:
                    if (hasattr(e, 'error') and
                        hasattr(e.error, 'is_shared_link_already_exists') and
                        e.error.is_shared_link_already_exists()):
                        # Obtener el enlace existente
                        links = dbx.sharing_list_shared_links(path=dropbox_path).links
                        if links:
                            dropbox_url = links[0].url.replace('?dl=0', '?dl=1')
                        else:
                            raise
                    else:
                        raise
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
