from scrapers.linkedin_modules.linkedin_database import (
    extraer_datos_tabla,
    obtener_id_carrera,
    obtener_codigos_por_id_carrera,
)
from conexion import conn, cursor

MERCADO = 0.15
HOJAS = ["Total Ingresos", "Ventas 12", "Ventas 0"]

def calc_mercado(proyecto_id):
    print(f"\n=== CÁLCULO DE MERCADO DESDE BASE DE DATOS ===")
    print(f"Proyecto ID: {proyecto_id}")

    try:
        # Obtener datos del proyecto desde la tabla proyectos_tendencias
        cursor.execute("SELECT carrera_referencia, codigo_ciiu, tipo_carpeta FROM proyectos_tendencias WHERE id = %s", (proyecto_id,))
        proyecto_row = cursor.fetchone()
        if not proyecto_row:
            print("ERROR: No se pudo obtener datos del proyecto.")
            return 0
        
        carrera_referencia, codigo_ciiu_consultar, tipo_carpeta = proyecto_row
        
        # Determinar qué tabla usar según el tipo de carpeta
        usar_cr = tipo_carpeta and "pregrado cr" in tipo_carpeta.lower()
        tabla_mercado = "cr_mercado_datos" if usar_cr else "mercado_datos"
        
        print(f"=== DEBUG TIPO DE CARPETA ===")
        print(f"Tipo de carpeta obtenido: '{tipo_carpeta}'")
        print(f"Contiene 'pregrado cr': {usar_cr}")
        print(f"Tabla de mercado seleccionada: {tabla_mercado}")
        print(f"================================")

        print(f"Carrera referencia: {carrera_referencia}")
        print(f"Código CIIU a consultar: {codigo_ciiu_consultar}")

        # Obtener ID de la carrera referencia
        try:
            if usar_cr:
                # Para proyectos CR, buscar específicamente con nivel "Pregrado CR"
                nivel_buscar = "Pregrado CR"
                print(f"DEBUG: Proyecto CR - Buscando carrera '{carrera_referencia}' con nivel '{nivel_buscar}'")
                cursor.execute("SELECT ID FROM carreras_facultad WHERE UPPER(Carrera) = UPPER(%s) AND Nivel = %s", (carrera_referencia, nivel_buscar))
                carrera_row = cursor.fetchone()
                if not carrera_row:
                    print(f"ERROR: No se encontró la carrera '{carrera_referencia}' con nivel '{nivel_buscar}'")
                    return 0
            else:
                # Para proyectos Ecuador, buscar solo por nombre (sin filtrar por nivel) - case insensitive
                print(f"DEBUG: Proyecto Ecuador - Buscando carrera '{carrera_referencia}' (sin filtro de nivel, case-insensitive)")
                cursor.execute("SELECT ID, Carrera, Nivel FROM carreras_facultad WHERE UPPER(Carrera) = UPPER(%s)", (carrera_referencia,))
                carrera_row = cursor.fetchone()
                if not carrera_row:
                    print(f"ERROR: No se encontró la carrera '{carrera_referencia}' en Ecuador")
                    return 0
                print(f"DEBUG: Carrera encontrada - ID: {carrera_row[0]}, Nombre: '{carrera_row[1]}', Nivel: '{carrera_row[2]}'")
            
            id_carrera = carrera_row[0]
            print(f"ID carrera referencia encontrado: {id_carrera}")
        except Exception as e:
            print(f"ERROR: No se pudo obtener el ID de la carrera: {e}")
            return 0

        # Obtener códigos CIIU de la carrera referencia
        try:
            codigos_referencia = obtener_codigos_por_id_carrera(id_carrera)
            codigos_referencia = [c.strip() for c in codigos_referencia]
            print(f"DEBUG: Códigos obtenidos para carrera ID {id_carrera}: {codigos_referencia}")
        except ValueError as e:
            print(f"ERROR: No se pudieron obtener los códigos de la carrera referencia: {e}.")
            return 0

        # Código CIIU de la carrera a consultar (puede ser lista o string)
        codigos_consultar = [codigo_ciiu_consultar.strip()] if codigo_ciiu_consultar else []
        
        # Validar que el código no sea vacío o inválido (pero '0' es válido)
        if not codigos_consultar or codigos_consultar[0] in ['', 'None', 'null']:
            print(f"ERROR: Código CIIU inválido o vacío: {codigo_ciiu_consultar}")
            print("SUGERENCIA: Verificar que el proyecto tenga un código CIIU válido en la base de datos")
            return 0
        
        if codigos_consultar[0] == '0':
            print(f"INFORMACIÓN: Código CIIU '0' detectado - Se usarán valores de 0 para todas las hojas (comportamiento esperado)")
        else:
            print(f"INFORMACIÓN: Código CIIU válido encontrado: {codigos_consultar[0]}")

        resultados_carreraReferencia = {}
        resultados_carreraConsultar = {}

        for hoja in HOJAS:
            print(f"\n--- Procesando hoja: {hoja} ---")
            print(f"DEBUG: Consultando tabla '{tabla_mercado}' para hoja '{hoja}'")
            # Obtener todos los registros de la hoja desde la base de datos usando la tabla correcta
            cursor.execute(
                f"SELECT actividad_economica, valor_2023 FROM {tabla_mercado} WHERE hoja_origen = %s",
                (hoja,)
            )
            rows = cursor.fetchall()
            # Convertir a diccionario para fácil acceso
            datos_hoja = {str(row[0]).strip(): row[1] for row in rows if row[0] is not None}
            print(f"DEBUG: Query ejecutado en tabla '{tabla_mercado}' - Filas obtenidas: {len(rows)}")
            if len(rows) == 0:
                print(f"ADVERTENCIA: No se encontraron datos en tabla '{tabla_mercado}' para hoja '{hoja}'")
            else:
                print(f"DEBUG: Primeros 3 códigos encontrados: {list(datos_hoja.keys())[:3]}")
            print(f"Filas totales en la hoja: {len(rows)}")

            # Mostrar códigos buscados y valores para referencia
            print(f"Códigos referencia buscados: {codigos_referencia}")
            codigos_ref_encontrados = []
            codigos_ref_no_encontrados = []
            valores_ref_codigos = []
            for codigo in codigos_referencia:
                valor = datos_hoja.get(codigo)
                if valor is not None:
                    codigos_ref_encontrados.append(codigo)
                    valores_ref_codigos.append(valor)
                    print(f"  Código referencia {codigo}: valor = {valor}")
                    if valor == 0:
                        print(f"    -> ADVERTENCIA: Valor para código referencia {codigo} es 0")
                else:
                    codigos_ref_no_encontrados.append(codigo)
                    print(f"  Código referencia {codigo}: NO ENCONTRADO")

            # Mostrar códigos buscados y valores para consulta
            print(f"Códigos consulta buscados: {codigos_consultar}")
            codigos_cons_encontrados = []
            codigos_cons_no_encontrados = []
            valores_cons_codigos = []
            for codigo in codigos_consultar:
                valor = datos_hoja.get(codigo)
                if valor is not None:
                    codigos_cons_encontrados.append(codigo)
                    valores_cons_codigos.append(valor)
                    print(f"  Código consulta {codigo}: valor = {valor}")
                    if valor == 0:
                        print(f"    -> ADVERTENCIA: Valor para código consulta {codigo} es 0")
                else:
                    codigos_cons_no_encontrados.append(codigo)
                    print(f"  Código consulta {codigo}: NO ENCONTRADO")

            # Referencia: sumar valores para todos los códigos de la carrera referencia
            total_ref = sum([v for v in valores_ref_codigos if v is not None])
            resultados_carreraReferencia[hoja] = total_ref

            # Consulta: sumar valores para el código CIIU de la carrera a consultar
            total_cons = sum([v for v in valores_cons_codigos if v is not None])
            resultados_carreraConsultar[hoja] = total_cons

            print(f"Referencia - códigos encontrados: {codigos_ref_encontrados}")
            print(f"Referencia - códigos NO encontrados: {codigos_ref_no_encontrados}")
            print(f"Referencia - valores por código: {valores_ref_codigos}")
            print(f"Total referencia para {hoja}: {total_ref}")

            print(f"Consulta - códigos encontrados: {codigos_cons_encontrados}")
            print(f"Consulta - códigos NO encontrados: {codigos_cons_no_encontrados}")
            print(f"Consulta - valores por código: {valores_cons_codigos}")
            print(f"Total consulta para {hoja}: {total_cons}")

        print(f"\n=== RESUMEN DE VALORES ===")
        print(f"Resultados carrera de referencia: {resultados_carreraReferencia}")
        print(f"Resultados carrera a consultar: {resultados_carreraConsultar}")
        print(f"Factor MERCADO: {MERCADO}")

        # Calcular el promedio
        print(f"\n=== PROCESO DE CÁLCULO ===")
        total = 0
        cantidad = 0
        hojas_procesadas = []
        hojas_omitidas = []

        for hoja in HOJAS:
            valor_ref = resultados_carreraReferencia.get(hoja, 0)
            valor_consultar = resultados_carreraConsultar.get(hoja, 0)

            print(f"\n--- Calculando para hoja: {hoja} ---")
            print(f"Valor referencia ({hoja}): {valor_ref} (tipo: {type(valor_ref)})")
            print(f"Valor consultar ({hoja}): {valor_consultar} (tipo: {type(valor_consultar)})")

            if valor_consultar is None or valor_consultar == 0:
                if codigos_consultar[0] == '0':
                    print(f"INFORMACIÓN: Valor consultar es 0 para hoja '{hoja}' (esperado con código CIIU '0') - Esta hoja será omitida del cálculo")
                else:
                    print(f"ADVERTENCIA: Valor consultar es None o 0 para hoja '{hoja}' - Esta hoja será omitida del cálculo")
                hojas_omitidas.append(f"{hoja} (valor_consultar={valor_consultar})")
                continue

            if valor_ref is None or valor_ref == 0:
                print(f"ADVERTENCIA: Valor referencia es None o 0 para hoja '{hoja}' - Esta hoja será omitida del cálculo")
                hojas_omitidas.append(f"{hoja} (valor_ref={valor_ref})")
                continue

            try:
                valor_ref = float(valor_ref)
                valor_consultar = float(valor_consultar)
            except (ValueError, TypeError) as e:
                print(f"ERROR: valor_ref o valor_consultar no es numérico en hoja '{hoja}': valor_ref={valor_ref}, valor_consultar={valor_consultar} - Error: {e}")
                hojas_omitidas.append(f"{hoja} (error conversión)")
                continue

            resultado = (valor_consultar * MERCADO / valor_ref) * 100
            print(f"Cálculo: ({valor_consultar} * {MERCADO} / {valor_ref}) * 100 = {resultado}")
            total += resultado
            cantidad += 1
            hojas_procesadas.append(hoja)
            print(f"Total acumulado: {total}, Cantidad: {cantidad}")

        print(f"\n=== RESULTADO FINAL ===")
        print(f"Hojas procesadas exitosamente: {hojas_procesadas}")
        print(f"Hojas omitidas: {hojas_omitidas}")
        print(f"Total suma de resultados: {total}")
        print(f"Cantidad de hojas procesadas: {cantidad}")

        promedio = round(total / cantidad, 2) if cantidad else 0
        print(f"Promedio calculado: {promedio}")

        if promedio >= 15:
            print(f"Promedio >= 15, limitando a 15")
            promedio = 15

        print(f"Promedio final retornado: {promedio}")

        if len(hojas_omitidas) > 0:
            print(f"\n=== DIAGNÓSTICO ===")
            print(f"Se omitieron {len(hojas_omitidas)} de {len(HOJAS)} hojas:")
            for hoja_omitida in hojas_omitidas:
                print(f"  - {hoja_omitida}")
            print(f"Esto puede indicar:")
            print(f"  - Datos faltantes en la fuente de consulta")
            print(f"  - Problemas de mapeo entre nombres de hojas/columnas")
            print(f"  - Datos no numéricos en las fuentes")

    except Exception as e:
        print(f"ERROR general en calc_mercado: {e}")
        return 0

    return promedio