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

# Ejemplo de uso:
if __name__ == "__main__":
    codigos = obtener_codigos_ciiu()
    print(codigos)
