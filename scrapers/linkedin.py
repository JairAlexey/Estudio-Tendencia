from scrapers.linkedin_modules.linkedin_database import (
    extraer_datos_tabla,
    guardar_datos_sql,
)
from scrapers.linkedin_modules.linkedin_report import extraer_datos_reporte
from scrapers.linkedin_modules.linkedin_project import buscar_proyecto_en_pagina
from scrapers.linkedin_modules.linkedin_pagination import (
    paginar_y_buscar_carpeta,
    paginar_y_buscar_proyecto,
    reintentar_elementos_fallidos,
)
from scrapers.linkedin_modules.driver_config import (
    limpiar_singleton_lock,
    crear_opciones_chrome,
    iniciar_driver,
    login_linkedin,
)
from scrapers.linkedin_modules.linkedin_folder import buscar_carpeta_en_pagina
from scrapers.linkedin_modules.linkedin_summary import mostrar_resumen_final
from scrapers.linkedin_modules.linkedin_banner import esperar_y_refrescar_si_banner
from scrapers.linkedin_modules.linkedin_utils import hay_banner_error, esperar_elemento
from scrapers.linkedin_modules.linkedin_banner import esperar_y_refrescar_si_banner
import os
import time
from dotenv import load_dotenv


ERROR_SELECTORS = [
    "div.artdeco-toast-item[data-test-artdeco-toast-item-type='error']",
    "div[data-test-artdeco-toast-item-type='error']",
    "div.search-filters__notice-v2"
]

# === CONFIGURACIÓN GLOBAL DE TIEMPOS ===
TIEMPO_ESPERA_CORTO = 1   # segundos para esperas cortas  
TIEMPO_ESPERA_MEDIO = 2   # segundos para esperas medias
TIEMPO_ESPERA_LARGO = 4   # segundos para esperas largas
TIEMPO_ESPERA_BANNER = 40 # espera cuando aparece el banner de error (reducido considerablemente)
TIEMPO_ESPERA_PAGINA = 3  # espera larga para recarga de página


def linkedin_scraper():
    # -----------------------------------------------------------------------------
    # CONFIGURACIÓN: Cargar variables de entorno y definir parámetros iniciales
    # -----------------------------------------------------------------------------

    import sys
    load_dotenv()
    EMAIL = os.getenv("LINKEDIN_USER")
    PASSWORD = os.getenv("LINKEDIN_PASS")

    if not EMAIL or not PASSWORD:
        print("❌ Faltan credenciales de LinkedIn. Verifica las variables de entorno LINKEDIN_USER y LINKEDIN_PASS.")
        return

    if len(sys.argv) < 2:
        print("Uso: python linkedin.py <proyecto_id>")
        return
    proyecto_id = int(sys.argv[1])

    UBICACIONES = ["Ecuador", "América Latina"]
    user_data_dir = r"C:\Users\User\Documents\TRABAJO - UDLA\Estudio-Tendencia\profile"
    profile_directory = "Default"
    limpiar_singleton_lock(user_data_dir, profile_directory)
    options = crear_opciones_chrome(user_data_dir, profile_directory)
    driver = iniciar_driver(options)
    try:
        if not login_linkedin(driver, EMAIL, PASSWORD):
            return
        url = "https://www.linkedin.com/insights/saved?reportType=talent&tab=folders"
        driver.get(url)
        time.sleep(TIEMPO_ESPERA_MEDIO)


        # Extraer configuración del proyecto desde la base de datos
        reportes = extraer_datos_tabla("reporteLinkedin", proyecto_id)
        if not reportes:
            print(f"❌ No se encontraron datos para el proyecto {proyecto_id}")
            return


        resultados_finales = []
        elementos_fallidos = []

        def normalizar_resultado(datos, tipo, ubicacion):
            def to_int(val):
                if val is None or str(val).strip() in ["", "--"]:
                    return None
                return int(str(val).replace('.', '').replace(',', '').strip())
            profesionales = to_int(datos.get("profesionales"))
            anuncios = to_int(datos.get("anuncios_empleo") or datos.get("anuncios"))
            porcentaje = round((anuncios / profesionales) * 100, 2) if profesionales and anuncios else None
            return {
                "Tipo": tipo,
                "Region": ubicacion,
                "Profesionales": profesionales,
                "AnunciosEmpleo": anuncios,
                "PorcentajeAnunciosProfesionales": porcentaje,
                "DemandaContratacion": datos.get("demanda_contratacion"),
            }

        
        for elemento in reportes:
            carpeta_buscar = elemento.get("Carpeta")
            for tipo, carrera in [("Referencia", elemento.get("ProyectoReferencia")), ("Estudio", elemento.get("ProyectoEstudio"))]:
                print(f"\n=== Buscando carpeta '{carpeta_buscar}' y proyecto '{carrera}' ({tipo}) ===")
                encontrada = paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO)
                if not encontrada:
                    print(f"❌ No se encontró la carpeta '{carpeta_buscar}'")
                    elementos_fallidos.append({
                        'elemento': elemento,
                        'carpeta': carpeta_buscar,
                        'proyecto': carrera,
                        'razon': f"Carpeta '{carpeta_buscar}' no encontrada"
                    })
                    driver.get(url)
                    time.sleep(TIEMPO_ESPERA_CORTO)
                    continue

                # Usar paginar_y_buscar_proyecto para buscar y extraer datos
                resultados_temp = []
                proyecto_encontrado = paginar_y_buscar_proyecto(
                    driver, carrera, UBICACIONES, carpeta_buscar, resultados_temp,
                    buscar_proyecto_en_pagina,
                    lambda *args, **kwargs: extraer_datos_reporte(
                        *args, **kwargs,
                        esperar_y_refrescar_si_banner=lambda driver, **kw: esperar_y_refrescar_si_banner(
                            driver,
                            hay_banner_error,
                            esperar_elemento,
                            TIEMPO_ESPERA_BANNER,
                            TIEMPO_ESPERA_PAGINA,
                            TIEMPO_ESPERA_MEDIO,
                            TIEMPO_ESPERA_CORTO,
                            **kw
                        )
                    ),
                    TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_PAGINA
                )
                if not proyecto_encontrado:
                    print(f"❌ No se encontró el proyecto '{carrera}' dentro de la carpeta '{carpeta_buscar}'.")
                    elementos_fallidos.append({
                        'elemento': elemento,
                        'carpeta': carpeta_buscar,
                        'proyecto': carrera,
                        'razon': f"Proyecto '{carrera}' no encontrado en carpeta '{carpeta_buscar}'"
                    })
                else:
                    # Normalizar los resultados extraídos antes de guardar
                    for ubicacion, datos in zip(UBICACIONES, resultados_temp):
                        if datos:
                            resultado = normalizar_resultado(datos, tipo, ubicacion)
                            resultados_finales.append(resultado)
                        else:
                            print(f"❌ No se obtuvieron datos para {carrera} - {ubicacion}")
                driver.get(url)
                time.sleep(TIEMPO_ESPERA_PAGINA)

        # Reintento de elementos fallidos
        reintentar_elementos_fallidos(
            driver, elementos_fallidos, url, UBICACIONES,
            buscar_carpeta_en_pagina, buscar_proyecto_en_pagina, extraer_datos_reporte,
            TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO, TIEMPO_ESPERA_PAGINA
        )

        # Guardar resultados en la base de datos
        if resultados_finales:
            # Asignar correctamente el campo Tipo antes de guardar
            for r in resultados_finales:
                if "Tipo" not in r:
                    r["Tipo"] = "Referencia" if r.get("proyecto") == elemento.get("ProyectoReferencia") else "Estudio"
            guardar_datos_sql(resultados_finales, "linkedin", proyecto_id)
            print(f"✅ Datos guardados correctamente para el proyecto {proyecto_id}")
        else:
            print(f"ℹ️ No se obtuvieron resultados para el proyecto {proyecto_id}.")

        # Resumen final
        total_elementos = len(reportes) * 2
        elementos_exitosos = total_elementos - len(elementos_fallidos)
        if elementos_fallidos:
            print(f"\n📊 RESUMEN para proyecto {proyecto_id}:")
            print(f"   ✅ Exitosos: {elementos_exitosos}/{total_elementos}")
            print(f"   ❌ Fallidos: {len(elementos_fallidos)}/{total_elementos}")
            print(f"   📋 Elementos que no se pudieron procesar:")
            for fallido in elementos_fallidos:
                print(f"      - {fallido['carpeta']} -> {fallido['proyecto']} ({fallido['razon']})")
        else:
            print(f"\n🎉 Todos los elementos procesados exitosamente para el proyecto {proyecto_id} ({elementos_exitosos}/{total_elementos})")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    linkedin_scraper()
