import sys
import os
import psycopg2

# Add the parent directory to sys.path to find the conexion module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conexion import conn, cursor

def fix_sequence():
    try:
        # Obtener el máximo ID actual
        cursor.execute("SELECT MAX(id) FROM proyectos_tendencias")
        max_id = cursor.fetchone()[0]
        
        if max_id is not None:
            # Reiniciar la secuencia al máximo ID + 1
            cursor.execute(f"ALTER SEQUENCE proyectos_tendencias_id_seq RESTART WITH {max_id + 1}")
            conn.commit()
            print(f"Secuencia reiniciada exitosamente al valor {max_id + 1}")
        else:
            print("La tabla está vacía, no es necesario reiniciar la secuencia")
            
    except Exception as e:
        print(f"Error al reiniciar la secuencia: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_sequence()