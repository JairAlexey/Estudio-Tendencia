import pandas as pd
from conexion import conn, cursor

ARCHIVO_MERCADO = "db/mercado.xlsx"
HOJAS = ["Total Ingresos", "Ventas 12", "Ventas 0"]

def cargar_mercado():
    for hoja in HOJAS:
        df = pd.read_excel(ARCHIVO_MERCADO, sheet_name=hoja)
        # Filtrar solo las columnas requeridas
        df = df[["ACTIVIDAD ECONÓMICA", "2023"]]
        for _, row in df.iterrows():
            actividad = str(row["ACTIVIDAD ECONÓMICA"]).strip()
            valor_raw = row["2023"]
            # Intentar convertir el valor a float, si no se puede, usar None
            try:
                if pd.isna(valor_raw) or valor_raw == "":
                    valor = None
                else:
                    valor = float(str(valor_raw).replace(",", "").replace(" ", ""))
            except Exception:
                valor = None
            cursor.execute(
                "INSERT INTO mercado_datos (hoja_origen, actividad_economica, valor_2023) VALUES (?, ?, ?)",
                hoja, actividad, valor
            )
        conn.commit()
    print("Datos cargados correctamente en mercado_datos.")

if __name__ == "__main__":
    cargar_mercado()
