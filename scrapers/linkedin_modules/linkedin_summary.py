import os

def mostrar_resumen_final(proyectos_ids, extraer_datos_tabla):
    print(f"\n{'='*80}")
    print(f"RESUMEN FINAL DEL PROCESAMIENTO LINKEDIN")
    print(f"{'='*80}")
    
    proyectos_exitosos = 0
    proyectos_con_errores = 0
    total_ubicaciones_exitosas = 0
    total_ubicaciones_fallidas = 0

    for i, proyecto_id in enumerate(proyectos_ids, 1):
        print(f"\nPROYECTO {i}: ID {proyecto_id}")
        try:
            reportes = extraer_datos_tabla("reporteLinkedin", proyecto_id)
            if not reportes:
                print(f"   Sin reportes configurados")
                proyectos_con_errores += 1
                continue
            
            # Verificar datos de LinkedIn en la base de datos
            linkedin_data = extraer_datos_tabla("linkedin", proyecto_id)
            datos_procesados = len(linkedin_data) if linkedin_data else 0
            
            if datos_procesados > 0:
                # Contar ubicaciones únicas
                import pandas as pd
                df = pd.DataFrame(linkedin_data)
                ubicaciones_procesadas = df['region'].nunique() if 'region' in df.columns else 0
                
                print(f"   Registros extraídos: {datos_procesados}")
                print(f"   Ubicaciones únicas: {ubicaciones_procesadas}")
                
                if datos_procesados >= 4:  # Esperamos al menos 4 registros (2 regiones x 2 tipos)
                    proyectos_exitosos += 1
                    total_ubicaciones_exitosas += datos_procesados
                    print(f"   Proyecto procesado exitosamente")
                else:
                    proyectos_con_errores += 1
                    total_ubicaciones_exitosas += datos_procesados
                    total_ubicaciones_fallidas += (4 - datos_procesados)
                    print(f"   Procesamiento parcial: {datos_procesados}/4 registros esperados")
            else:
                print(f"   Sin datos guardados")
                proyectos_con_errores += 1
                total_ubicaciones_fallidas += 4
        except Exception as e:
            print(f"   Error procesando proyecto: {e}")
            proyectos_con_errores += 1

    print(f"\nESTADÍSTICAS GLOBALES:")
    print(f"   Proyectos procesados: {len(proyectos_ids)}")
    print(f"   Proyectos exitosos: {proyectos_exitosos}")
    print(f"   Proyectos con errores: {proyectos_con_errores}")
    print(f"   Total ubicaciones exitosas: {total_ubicaciones_exitosas}")
    print(f"   Total ubicaciones fallidas: {total_ubicaciones_fallidas}")

    if proyectos_con_errores == 0:
        print(f"\n¡PROCESAMIENTO COMPLETAMENTE EXITOSO!")
        print(f"   Todos los proyectos fueron procesados correctamente")
    else:
        print(f"\nPROCESAMIENTO COMPLETADO CON ERRORES")
        print(f"   {proyectos_con_errores} proyecto(s) tuvieron problemas")

    print(f"\nProceso LinkedIn finalizado. Se procesaron {len(proyectos_ids)} proyecto(s).")
    print(f"   Total ubicaciones exitosas: {total_ubicaciones_exitosas}")
    print(f"   Total ubicaciones fallidas: {total_ubicaciones_fallidas}")
