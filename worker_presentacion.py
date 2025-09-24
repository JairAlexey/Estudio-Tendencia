import os
import sys
import time
import dropbox

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
                dbx = dropbox.Dropbox('sl.u.AF-h8CNdkr6hMQipNzF4_QMYkFYkXqhGGLH0W97K9Yhnrp65Osa-BqbUNGnKxeufVkX8npQQYzYbnGYl2pZQP3RIcccO3zA6r0AHu3K8XgpeTrriVAPFfMsazURyJNAhLTvOI3kW1W5R5fhwqpiy3Um7ZbMTaHkj1u1n42Fl3bnqHRbDXXtInJLn7l-EtzI0CUfr5x-SHNujrHvqbynnjPhXzf1-hCmaJMj9aNE6K8bawW81MUC1uPerrejBlEwuSQm5yrZhIr8eV4oFe0lj98e9eFfMnD36tVUn1mBvRGh8QYuBv1xTIyniuJOnpWsvAf1SrFYH1Ox-PLVdV2-hwdX6DgpMuZgpxChM7S_TzC1DXJeMab7DQLZ5PH_KeJmprzp9Q3hm6MsTzIvbBnJhCqlENkYAeIKxY6OwugMRoR-5rdfUTTwfovEMiXjxVDJCI9QuJ07uBGW5VJ09OxaMEgZ5obtWN2OFfCdbf-lefdYAhln9Hu9aj_SVOtqmooaaFl29i1JoEBiJ5lOFZfRANjA10Gjvped23Oo7OYhOAnZIkeZMk7uYuz_wEpL_gVZSie9u4kg8BYbZDAni7k3ndH4zbwwPDzxALFbqW0-tozBY4vcaNG2Y2nQE0ktPInx-ndyPaRV8febNCWbj_8dC4LjCc-Ax_8aPGy8viH1OP4je4K27a7wTxmBvakm7xPRZOEFjY7GMh_o7cLqATtPzdcBJIL7coOsU2nA8ak0TuHGL6P2lEK3Eejjli-gXY_H3e4gA28meeX_MJxV7nMvve1-Tg5Nr17dEJqtmZI49nNgBoXGVy3BgAY0jD0_br6vMrHFyiwyFZuprWOkqDSug9cTeW_bzhl5Mcph0vkPXezgKl7p1sECBQ-ZovabLvHDQ68BJTjeG5UB8vNz9dAE2X_qvgAS-z-KCakXHdbPGHYOm5mhmWyNgatpr7vYFpxQzzMNt7lzlVSCJ6jNbU581pwUcTWfTj3YElttb2fJdgbs2yCGnam7HHR3LxsYCjo2rTaLpQDZvn0sUiXOXiKSkU2FinJVA5yfSQxEtUvUEGT2Yvc4YSToSo-cG6yqJ-vyF9B7AFWlZyKQl2tYA4T8q1ibjpG3a5ItrVx17VuKGQhUy1ioZxI_3kDkh-CAFTyeNv6yGrYTGuuCjdYQ72sHdrHMGmh2eE-QAkvC5oAabMtNceZHOUdePkqAkNUAqEAHO7jJNMsT9sEWRqxe9yeS4Z0xj-pDFJi41jDVNNvc51w7ihHceQajmEl8qQvyRcjpx1H9AO9eJ-xGtf_9FS7Qu_O2N2VNtUPH9wwacPtZFcWlXBbGwlHY1SmwZ_39gXOYal6e6jdPabYsZ2pVs0j2n31YJ5coKLYCL7dfMevetC5-AqmsUZ5pi7rtgKi9EP5I1_p4L1mzzfOEsOuLvtjG9hTwqesXkDe805ZguaoA7zMFTgnWV_5VwC6HzJe7EQsTuoqtxQfiPdCJwbwo5XRum92FR')
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
