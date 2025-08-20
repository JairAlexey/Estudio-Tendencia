import pyodbc
from conexion import conn, cursor

# Script para crear tablas necesarias en la base de datos

def crear_tablas():
    # Tabla principal de proyectos y tendencias
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proyectos_tendencias')
    BEGIN
        CREATE TABLE proyectos_tendencias (
            id INT IDENTITY(1,1) PRIMARY KEY,
            tipo_carpeta NVARCHAR(100),
            carrera_referencia NVARCHAR(200),
            carrera_estudio NVARCHAR(200),
            palabra_semrush NVARCHAR(200),
            codigo_ciiu NVARCHAR(50),
            ingresos_2023 FLOAT,
            ventas12_2023 FLOAT,
            ventas0_2023 FLOAT
        )
    END
    ''')

    # Tabla de tendencias (palabras y promedios)
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tendencias')
    BEGIN
        CREATE TABLE tendencias (
            id INT IDENTITY(1,1) PRIMARY KEY,
            proyecto_id INT,
            palabra NVARCHAR(200),
            promedio FLOAT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
        )
    END
    ''')

    # Tabla de modalidad de oferta
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'modalidad_oferta')
    BEGIN
        CREATE TABLE modalidad_oferta (
            id INT IDENTITY(1,1) PRIMARY KEY,
            proyecto_id INT,
            presencial NVARCHAR(50),
            virtual NVARCHAR(50),
            FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
        )
    END
    ''')

    conn.commit()
    print("Tablas creadas correctamente.")

if __name__ == "__main__":
    crear_tablas()
