import os
from pathlib import Path
import pandas as pd

def _resolver_ruta_excel():
    # 1) Variable de entorno explícita
    env_path = os.getenv("MERCADO_XLSX")
    if env_path and Path(env_path).exists():
        return str(Path(env_path).resolve())

    # 2) Ruta relativa al proyecto: <raiz>/db/mercado.xlsx (este archivo vive en la raíz del proyecto)
    proyecto_root = Path(__file__).resolve().parent
    por_defecto = proyecto_root / 'db' / 'mercado.xlsx'
    if por_defecto.exists():
        return str(por_defecto)

    # 3) Fallback: cwd/db/mercado.xlsx
    cwd_path = Path.cwd() / 'db' / 'mercado.xlsx'
    return str(cwd_path)

# Ruta al archivo Excel (resuelta de forma robusta)
EXCEL_PATH = _resolver_ruta_excel()

# Función para obtener los códigos CIIU únicos
def obtener_codigos_ciiu():
    try:
        df = pd.read_excel(EXCEL_PATH)
        codigos = df['ACTIVIDAD ECONÓMICA'].dropna().unique().tolist()
        return codigos
    except Exception as e:
        print(f"ERROR al leer códigos CIIU desde '{EXCEL_PATH}': {e}")
        return []

# Ejemplo de uso:
if __name__ == "__main__":
    codigos = obtener_codigos_ciiu()
    print(codigos)
