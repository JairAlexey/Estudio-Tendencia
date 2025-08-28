import os

def mostrar_resumen_final(rutas_excel, extraer_datos_tabla):
    print(f"\n{'='*80}")
    print(f"RESUMEN FINAL DEL PROCESAMIENTO LINKEDIN")
    print(f"{'='*80}")
    
    archivos_exitosos = 0
    archivos_con_errores = 0
    total_proyectos_procesados = 0
    total_proyectos_fallidos = 0
    total_ubicaciones_exitosas = 0
    total_ubicaciones_fallidas = 0

    for i, ruta_excel in enumerate(rutas_excel, 1):
        print(f"\nARCHIVO {i}: {os.path.basename(ruta_excel)}")
        try:
            reportes = extraer_datos_tabla("reporteLinkedin", ruta_excel)
            if not reportes:
                print(f"   Sin reportes configurados")
                archivos_con_errores += 1
                continue
            total_elementos = len(reportes)
            try:
                import pandas as pd
                df = pd.read_excel(ruta_excel, sheet_name="LinkedIn")
                datos_procesados = len(df) if not df.empty else 0
                if datos_procesados > 0:
                    ubicaciones_procesadas = df['Region'].nunique() if 'Region' in df.columns else 0
                    proyectos_estimados = datos_procesados // 2 if datos_procesados >= 2 else 1
                    print(f"   Registros extraídos: {datos_procesados}")
                    print(f"   Ubicaciones únicas: {ubicaciones_procesadas}")
                    print(f"   Proyectos procesados: {proyectos_estimados}/{total_elementos}")
                    if datos_procesados >= total_elementos * 2:
                        archivos_exitosos += 1
                        total_proyectos_procesados += total_elementos
                        total_ubicaciones_exitosas += datos_procesados
                        print(f"   Todos los proyectos procesados exitosamente")
                    else:
                        archivos_con_errores += 1
                        proyectos_parciales = datos_procesados // 2
                        total_proyectos_procesados += proyectos_parciales
                        total_proyectos_fallidos += (total_elementos - proyectos_parciales)
                        total_ubicaciones_exitosas += datos_procesados
                        total_ubicaciones_fallidas += (total_elementos * 2 - datos_procesados)
                        print(f"   Procesamiento parcial: {proyectos_parciales}/{total_elementos} proyectos")
                else:
                    print(f"   Sin datos guardados")
                    archivos_con_errores += 1
                    total_proyectos_fallidos += total_elementos
                    total_ubicaciones_fallidas += total_elementos * 2
            except Exception as e:
                print(f"   Error verificando datos guardados: {e}")
                archivos_con_errores += 1
                total_proyectos_fallidos += total_elementos
                total_ubicaciones_fallidas += total_elementos * 2
        except Exception as e:
            print(f"   Error procesando archivo: {e}")
            archivos_con_errores += 1

    print(f"\nESTADÍSTICAS GLOBALES:")
    print(f"   Archivos procesados: {len(rutas_excel)}")
    print(f"   Archivos exitosos: {archivos_exitosos}")
    print(f"   Archivos con errores: {archivos_con_errores}")
    print(f"   Total proyectos procesados: {total_proyectos_procesados}")
    print(f"   Total proyectos fallidos: {total_proyectos_fallidos}")
    print(f"   Total ubicaciones exitosas: {total_ubicaciones_exitosas}")
    print(f"   Total ubicaciones fallidas: {total_ubicaciones_fallidas}")

    if archivos_con_errores == 0:
        print(f"\n¡PROCESAMIENTO COMPLETAMENTE EXITOSO!")
        print(f"   Todos los archivos, proyectos y ubicaciones fueron procesados correctamente")
    else:
        print(f"\nPROCESAMIENTO COMPLETADO CON ERRORES")
        print(f"   {archivos_con_errores} archivo(s) tuvieron problemas")
        if total_proyectos_fallidos > 0:
            print(f"   {total_proyectos_fallidos} proyecto(s) no pudieron ser procesados")
        if total_ubicaciones_fallidas > 0:
            print(f"   {total_ubicaciones_fallidas} ubicación(es) fallaron")

    print(f"\nProceso LinkedIn finalizado. Se procesaron {len(rutas_excel)} archivo(s).")
