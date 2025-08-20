import pyodbc
from conexion import conn, cursor

def test_insert_scope_identity():
    try:
        cursor.execute('''
            INSERT INTO proyectos_tendencias (
                tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, ingresos_2023, ventas12_2023, ventas0_2023
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
            'TEST',
            'TEST_CARRERA',
            'TEST_ESTUDIO',
            'TEST_SEMRUSH',
            'TEST_CIIU',
            123.45,
            67.89,
            10.11
        )
        # NO commit antes de obtener el ID
        cursor.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
        proyecto_id_row = cursor.fetchone()
        if proyecto_id_row is None or proyecto_id_row[0] is None:
            print("No se pudo obtener el ID del proyecto insertado.")
        else:
            print(f"ID insertado correctamente: {proyecto_id_row[0]}")
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_insert_scope_identity()
