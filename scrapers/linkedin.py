from scrapers.linkedin_modules.linkedin_excel import (
    extraer_datos_tabla,
    guardar_datos_excel,
    obtener_rutas_excel,
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
    load_dotenv()
    EMAIL = os.getenv("LINKEDIN_USER")
    PASSWORD = os.getenv("LINKEDIN_PASS")

    if not EMAIL or not PASSWORD:
        print("❌ Faltan credenciales de LinkedIn. Verifica las variables de entorno LINKEDIN_USER y LINKEDIN_PASS.")
        return

    # Obtener todas las rutas de Excel configuradas
    try:
        rutas_excel = obtener_rutas_excel()
        print(f"📂 Se procesarán {len(rutas_excel)} archivo(s) Excel:")
        for i, ruta in enumerate(rutas_excel, 1):
            print(f"   {i}. {ruta}")
    except ValueError as e:
        print(e)
        return

    UBICACIONES = ["Ecuador", "América Latina"]

    # CONFIGURACIÓN DEL NAVEGADOR USANDO EL MÓDULO
    user_data_dir = r"C:\Users\User\Documents\TRABAJO - UDLA\Scraping-Tendencias\profile"
    profile_directory = "Default"

    limpiar_singleton_lock(user_data_dir, profile_directory)
    options = crear_opciones_chrome(user_data_dir, profile_directory)
    driver = iniciar_driver(options)

    # INICIAR SESIÓN EN LINKEDIN USANDO EL MÓDULO
    if not login_linkedin(driver, EMAIL, PASSWORD):
        return

    # -------------------------------------------------------------------------
    # ACCEDER A INSIGHTS
    # -------------------------------------------------------------------------
    url = "https://www.linkedin.com/insights/saved?reportType=talent&tab=folders"
    driver.get(url)
    time.sleep(TIEMPO_ESPERA_MEDIO)

    # Procesar cada archivo Excel
    for i, ruta_excel in enumerate(rutas_excel, 1):
        print(f"\n{'='*60}")
        print(f"📊 Procesando archivo {i}/{len(rutas_excel)}: {os.path.basename(ruta_excel)}")
        print(f"{'='*60}")

        # Extraer reportes para este archivo específico
        reportes = extraer_datos_tabla("reporteLinkedin", ruta_excel)
        if not reportes:
            print(f"❌ No se encontraron reportes en el archivo {ruta_excel}")
            continue

        # Lista para almacenar los resultados finales de este archivo
        resultados_finales = []
        elementos_fallidos = []  # Nueva lista para rastrear elementos que fallaron

        # -----------------------------------------------------------------------------
        # PROCESAR CADA ELEMENTO DEL REPORTE (Carpeta + Proyecto) para este archivo
        # -----------------------------------------------------------------------------
        for elemento in reportes:
            # Se esperan las claves "Carpeta" y "Proyecto" en cada elemento
            if isinstance(elemento, dict):
                carpeta_buscar = elemento.get("Carpeta")
                proyecto_buscar = elemento.get("Proyecto")
            else:
                print(f"❌ Formato inesperado en elemento de reportes: {elemento}")
                continue

            print(
                f"\n=== Buscando carpeta '{carpeta_buscar}' y proyecto '{proyecto_buscar}' ==="
            )
            encontrada = paginar_y_buscar_carpeta(driver, carpeta_buscar, buscar_carpeta_en_pagina, url, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO)
            if not encontrada:
                print(f"❌ No se encontró la carpeta '{carpeta_buscar}'")
                elementos_fallidos.append({
                    'elemento': elemento,
                    'carpeta': carpeta_buscar,
                    'proyecto': proyecto_buscar,
                    'razon': f"Carpeta '{carpeta_buscar}' no encontrada"
                })
                driver.get(url)
                time.sleep(TIEMPO_ESPERA_CORTO)
                continue

            proyecto_encontrado = paginar_y_buscar_proyecto(
                driver, proyecto_buscar, UBICACIONES, carpeta_buscar, resultados_finales,
                buscar_proyecto_en_pagina, extraer_datos_reporte, TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_PAGINA
            )
            if not proyecto_encontrado:
                print(
                    f"❌ No se encontró el proyecto '{proyecto_buscar}' dentro de la carpeta '{carpeta_buscar}'."
                )
                elementos_fallidos.append({
                    'elemento': elemento,
                    'carpeta': carpeta_buscar,
                    'proyecto': proyecto_buscar,
                    'razon': f"Proyecto '{proyecto_buscar}' no encontrado en carpeta '{carpeta_buscar}'"
                })
            driver.get(url)
            time.sleep(TIEMPO_ESPERA_PAGINA)

        # -----------------------------------------------------------------------------
        # REINTENTO DE ELEMENTOS FALLIDOS (segunda oportunidad)
        # -----------------------------------------------------------------------------
        reintentar_elementos_fallidos(
            driver, elementos_fallidos, url, UBICACIONES,
            buscar_carpeta_en_pagina, buscar_proyecto_en_pagina, extraer_datos_reporte,
            TIEMPO_ESPERA_CORTO, TIEMPO_ESPERA_MEDIO, TIEMPO_ESPERA_PAGINA
        )

        # -----------------------------------------------------------------------------
        # Exportar resultados a Excel para este archivo
        # -----------------------------------------------------------------------------
        if resultados_finales:
            guardar_datos_excel(resultados_finales, plataforma="LinkedIn", ruta_excel=ruta_excel)
            print(f"✅ Datos guardados correctamente para {os.path.basename(ruta_excel)}")
        else:
            print(f"ℹ️ No se obtuvieron resultados para {os.path.basename(ruta_excel)}.")
        
        # Resumen final del archivo procesado
        total_elementos = len(reportes)
        elementos_exitosos = total_elementos - len(elementos_fallidos)
        if elementos_fallidos:
            print(f"\n📊 RESUMEN para {os.path.basename(ruta_excel)}:")
            print(f"   ✅ Exitosos: {elementos_exitosos}/{total_elementos}")
            print(f"   ❌ Fallidos: {len(elementos_fallidos)}/{total_elementos}")
            print(f"   📋 Elementos que no se pudieron procesar:")
            for fallido in elementos_fallidos:
                print(f"      - {fallido['carpeta']} -> {fallido['proyecto']} ({fallido['razon']})")
        else:
            print(f"\n🎉 Todos los elementos procesados exitosamente para {os.path.basename(ruta_excel)} ({elementos_exitosos}/{total_elementos})")

    # RESUMEN FINAL COMPLETO DE TODO EL PROCESAMIENTO
    mostrar_resumen_final(rutas_excel, extraer_datos_tabla)

if __name__ == "__main__":
    linkedin_scraper()
