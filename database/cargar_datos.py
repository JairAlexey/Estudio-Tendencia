import pandas as pd
from conexion import conn, cursor

ARCHIVO_MERCADO = "files/EnfermeriaNeonatal.xlsx"

HOJAS = ["Carreras", "Codigos", "SemrushBase", "GoogleTrendsBase"]

def cargar_carreras_facultad(path_excel):
    df = pd.read_excel(path_excel, sheet_name="Carreras")
    insertados = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO carreras_facultad (Facultad, Nivel, Carrera)
                VALUES (%s, %s, %s)
            """, (row['Facultad'], row['Nivel'], row['Carrera']))
            insertados += 1
        except Exception:
            pass
    conn.commit()
    print(f"carreras_facultad: {insertados} registros insertados exitosamente.")

def cargar_codigos_carrera(path_excel):
    df = pd.read_excel(path_excel, sheet_name="Codigos")
    insertados = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO codigos_carrera (ID_Carrera, Codigo)
                VALUES (%s, %s)
            """, (int(row['ID Carrera']), str(row['Codigo'])))
            insertados += 1
        except Exception:
            pass
    conn.commit()
    print(f"codigos_carrera: {insertados} registros insertados exitosamente.")

def cargar_semrush_base(path_excel):
    df = pd.read_excel(path_excel, sheet_name="SemrushBase")
    insertados = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO semrush_base (ID_Carrera, Vision_General, Palabras, Volumen)
                VALUES (%s, %s, %s, %s)
            """, (int(row['ID Carrera']), int(row['Visión General']), int(row['Palabras']), int(row['Volumen'])))
            insertados += 1
        except Exception:
            pass
    conn.commit()
    print(f"semrush_base: {insertados} registros insertados exitosamente.")

def cargar_tendencias_carrera(path_excel):
    df = pd.read_excel(path_excel, sheet_name="GoogleTrendsBase")
    insertados = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO tendencias_carrera (ID_Carrera, Palabra, Cantidad)
                VALUES (%s, %s, %s)
            """, (int(row['ID Carrera']), str(row['Palabra']), int(row['Cantidad'])))
            insertados += 1
        except Exception:
            pass
    conn.commit()
    print(f"tendencias_carrera: {insertados} registros insertados exitosamente.")

if __name__ == "__main__":
    cargar_carreras_facultad(ARCHIVO_MERCADO)
    cargar_codigos_carrera(ARCHIVO_MERCADO)
    cargar_semrush_base(ARCHIVO_MERCADO)
    cargar_tendencias_carrera(ARCHIVO_MERCADO)
