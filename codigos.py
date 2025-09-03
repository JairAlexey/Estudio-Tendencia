import pyodbc
from conexion import conn, cursor

# Función para obtener los códigos CIIU únicos desde la base de datos filtrando por hoja_origen
def obtener_codigos_ciiu(hoja_origen="Total Ingresos"):
    try:
        cursor.execute(
            "SELECT DISTINCT actividad_economica FROM mercado_datos WHERE hoja_origen = ? AND actividad_economica IS NOT NULL",
            hoja_origen
        )
        rows = cursor.fetchall()
        codigos = [row[0] for row in rows]
        return codigos
    except Exception as e:
        print(f"ERROR al leer códigos CIIU desde la base de datos: {e}")
        return []

# Ejemplo de uso:
if __name__ == "__main__":
    codigos = obtener_codigos_ciiu()
    print(codigos)
