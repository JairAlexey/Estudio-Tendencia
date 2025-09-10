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
                dbx = dropbox.Dropbox('sl.u.AF_bhj8l7Nspj1wp_IEYxBujE1_CFKbmdaCn2-meIk4JIpNYH0lnU4D1OfBSgcI8l3Qh1BHmJDiwwojLxnenmN0dmvsofTd5Rcrohnc_Fofow-WBrlFhUrZdGzHAC4IlKruv7PEhyA5xQrinkNxUJD-LcSOpLltxMvRoV3LvpFXKRE1EO5hb8FanmYDUu04m29wvkptWFlAGlFHayL_6pP3BEnMhSP5k5eBpaCUxyXTXXhjwbVHg0uiT2nzD_UprBQSgV3ocDmgyJJILbD1t5F9Kq6S5lzl4DOhNvsKP53vNxom3wTGG__2Ug_oc8mslj5firHaiKVKHOazSu131vMmXkyw_fvPF86Ksul9ze9F3NVxSUj4uXV5hnWHJSGH-5fAU-wATXb5fM6kjEMcU5wVmEp7lowb3a5npgmrcAEY14_nLinpboS233E8foiUAadz59uQBnLfXT5xEKu8IvjrsyhEH9lPEq7fyfrOuJ7lSR9YvDEuGATyRXm-Kebd9MqJdlBZYMKrGcrEfOYoBL7EtO6Y6oOIWV2lwlB6yn_EV04CTHZbeWhs7d7qPCRSNGyh_oB2cJgSVV3oIjm27yTPwLr8yznJljMVHZ2VBYsKpXi9zNjUGlp0BxapX72_uBDPAAgi24qKLXA1B1fzo5EOi1IyLiCa4TVc1jXMCoch_TmRU6szkWS8gSrWr08oR3DG_V3CCOKYPAUclRY5as2XQajCh06sJTamUYSUjJuhCmGwrpNPvdisCe30F82z9zMmPTndOXRPihiKwGFmHn6cvifCCcDp76L-RXsE7BbbWVHIw7bp_lNmZKwTj0OChDkQRJKyc6goy5BA8dTk-s-zpDAJQlhvSLF_ZFuHVtm_rzIG36PVL2NAPEBttb9UL1w-rZEJZOprta_LSNV-9pvrDJC3tzqHdUD7K4pLyZq0CtguiEIt7thrB6Xn0c34uB6pDKDWpSpINfh44mhOic1UDUeKDu5szCKEh9oswagH6A7ucRW7du2AQDZ0hN4CkJlzbnv02KH4ey2FHjD9iizy5HALCj3iBMmtig5-INL5cPbn4rIINSJZn23XbJeheCxtP00Kx3If_9y5UcKPqH5933O4bbuaCuTGFDAO4TfAEEbS10vmFG7_QVd0R5ncQZ1o9-6XujA3SxqU_uTARHPZwvKkrI8ON5kuHUsllPd5GSNJOnFZFXRPuNLsX4J72EvqMCu4qyrm5ZHjHtq7aqjHcGQE1SdT88udadlhJVKPE-1FQ1Ql95WiUbQT6OEPmh75ruE-UKrh-bkF2XnqeQ-4-tMn8avTL9JMtlQO0pO8_yjcraOxpRR7N9QHCX7qooqqgrdLzpI-QIDy1NI-zA7eu-kyRXanA_sBzKcVEt3QWB472GtyWwJUcPI8CMQ88GMA59FFklw5VoRudFmPN2ptd-OqMKJpIq_oRxV3K5zItyWSPXmky3HjKp4RZlywRzEQ')
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
