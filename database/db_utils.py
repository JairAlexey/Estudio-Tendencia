import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE
from typing import Optional, Tuple, Any
import time
from conexion import get_connection

def insertar_proyecto_con_reintentos(datos: dict, max_intentos: int = 3) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Intenta insertar un nuevo proyecto con reintentos en caso de conflictos.
    
    Args:
        datos: Diccionario con los datos del proyecto
        max_intentos: Número máximo de intentos antes de fallar
    
    Returns:
        Tuple[bool, Optional[int], Optional[str]]: (éxito, id_proyecto, mensaje_error)
    """
    intento = 0
    while intento < max_intentos:
        try:
            conn = get_connection()
            # Usar el nivel de aislamiento más estricto para evitar condiciones de carrera
            conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
            
            with conn.cursor() as cur:
                # Insertar el proyecto
                cur.execute('''
                    INSERT INTO proyectos_tendencias (
                        tipo_carpeta, carrera_referencia, carrera_estudio, 
                        palabra_semrush, codigo_ciiu, carrera_linkedin, 
                        id_ticket, inteligencia_artificial_entrada
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    datos['tipo_carpeta'],
                    datos['carrera_referencia'],
                    datos['carrera_estudio'],
                    datos['palabra_semrush'],
                    datos['codigo_ciiu'],
                    datos['carrera_linkedin'],
                    datos['id_ticket'],
                    datos['inteligencia_artificial_entrada']
                ))
                
                proyecto_id = cur.fetchone()[0]
                
                # Insertar tendencias
                for trend in datos['trends']:
                    cur.execute('''
                        INSERT INTO tendencias (proyecto_id, palabra, promedio)
                        VALUES (%s, %s, %s)
                    ''', (proyecto_id, trend["palabra"], trend["promedio"]))

                # Insertar modalidad de oferta
                if datos.get('modalidad'):
                    cur.execute('''
                        INSERT INTO modalidad_oferta (proyecto_id, presencial, virtual)
                        VALUES (%s, %s, %s)
                    ''', (proyecto_id, datos['modalidad']['presencial'], datos['modalidad']['virtual']))

                # Insertar registro en seguimiento_proyecto
                cur.execute('''
                    INSERT INTO seguimiento_proyecto (proyecto_id)
                    VALUES (%s)
                ''', (proyecto_id,))

                conn.commit()
                return True, proyecto_id, None
                
        except psycopg2.Error as e:
            conn.rollback()
            if "duplicate key" in str(e).lower():
                # Esperar un momento antes de reintentar
                time.sleep(0.5 * (intento + 1))
                intento += 1
                continue
            return False, None, f"Error de base de datos: {str(e)}"
        finally:
            conn.close()
            
    return False, None, "Excedido número máximo de intentos para insertar el proyecto"