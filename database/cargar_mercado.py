import pandas as pd
from conexion import conn, cursor

ARCHIVO_MERCADO = "files/mercado.xlsx"
HOJAS = ["Total Ingresos", "Ventas 12", "Ventas 0"]

def cargar_mercado():
    try:
        # Limpiar datos existentes
        cursor.execute("DELETE FROM mercado_datos")
        conn.commit()
        
        for hoja in HOJAS:
            print(f"Cargando hoja: {hoja}")
            df = pd.read_excel(ARCHIVO_MERCADO, sheet_name=hoja)
            
            # Verificar que las columnas existan
            if "ACTIVIDAD ECONÓMICA" not in df.columns or "2023" not in df.columns:
                print(f"Advertencia: Columnas esperadas no encontradas en hoja {hoja}")
                continue
                
            # Filtrar solo las columnas requeridas
            df = df[["ACTIVIDAD ECONÓMICA", "2023"]].dropna(subset=["ACTIVIDAD ECONÓMICA"])
            
            registros_insertados = 0
            for _, row in df.iterrows():
                actividad = str(row["ACTIVIDAD ECONÓMICA"]).strip()
                if not actividad or actividad.lower() in ['nan', 'none', '']:
                    continue
                    
                valor_raw = row["2023"]
                # Intentar convertir el valor a float, si no se puede, usar None
                try:
                    if pd.isna(valor_raw) or valor_raw == "":
                        valor = None
                    else:
                        valor = float(str(valor_raw).replace(",", "").replace(" ", ""))
                except Exception:
                    valor = None
                
                try:
                    cursor.execute(
                        "INSERT INTO mercado_datos (hoja_origen, actividad_economica, valor_2023) VALUES (%s, %s, %s)",
                        (hoja, actividad, valor)
                    )
                    registros_insertados += 1
                except Exception as e:
                    print(f"Error insertando registro {actividad}: {e}")
                    continue
            
            print(f"Hoja {hoja}: {registros_insertados} registros insertados")
        
        conn.commit()
        print("Datos cargados correctamente en mercado_datos.")
        
    except Exception as e:
        print(f"Error general cargando datos de mercado: {e}")
        conn.rollback()

if __name__ == "__main__":
    cargar_mercado()
