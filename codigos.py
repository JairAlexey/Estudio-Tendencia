import os
import pandas as pd

# Ruta al archivo Excel
EXCEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extract/db/mercado.xlsx'))

# Función para obtener los códigos CIIU únicos
def obtener_codigos_ciiu():
    try:
        df = pd.read_excel(EXCEL_PATH)
        codigos = df['ACTIVIDAD ECONÓMICA'].dropna().unique().tolist()
        return codigos
    except Exception as e:
        print(f"ERROR al leer códigos CIIU: {e}")
        return []

# Función para obtener valores por código y año
# hoja: nombre de la hoja, columna_codigo: nombre de la columna con el código, columna_valor: año (ejemplo: '2023')
def obtener_valor_por_codigo(codigo, hoja, columna_codigo, columna_valor):
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=hoja)
        fila = df[df[columna_codigo] == codigo]
        if not fila.empty:
            return fila.iloc[0][columna_valor]
        return None
    except Exception as e:
        print(f"ERROR al leer valor por código: {e}")
        return None

# Ejemplo de uso:
if __name__ == "__main__":
    codigos = obtener_codigos_ciiu()
    print(codigos)
    valor_ingresos = obtener_valor_por_codigo(codigos[0], hoja='Total Ingresos', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
    print(f"Ingresos 2023 para {codigos[0]}: {valor_ingresos}")
    valor_ventas12 = obtener_valor_por_codigo(codigos[0], hoja='Ventas 12', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
    print(f"Ventas 12 2023 para {codigos[0]}: {valor_ventas12}")
    valor_ventas0 = obtener_valor_por_codigo(codigos[0], hoja='Ventas 0', columna_codigo='ACTIVIDAD ECONÓMICA', columna_valor='2023')
    print(f"Ventas 0 2023 para {codigos[0]}: {valor_ventas0}")
