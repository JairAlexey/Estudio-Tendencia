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
            codigo_ciiu NVARCHAR(50)
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

    # Tabla de linkedin relacionada con proyectos_tendencias
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'linkedin')
    BEGIN
        CREATE TABLE linkedin (
            id INT IDENTITY(1,1) PRIMARY KEY,
            proyecto_id INT,
            Tipo NVARCHAR(50),
            Region NVARCHAR(100),
            Profesionales INT,
            AnunciosEmpleo INT,
            PorcentajeAnunciosProfesionales DECIMAL(10,2),
            DemandaContratacion INT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
        )
    END
    ''')

    # Tabla de semrush relacionada con proyectos_tendencias
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'semrush')
    BEGIN
        CREATE TABLE semrush (
            id INT IDENTITY(1,1) PRIMARY KEY,
            proyecto_id INT,
            VisionGeneral NVARCHAR(200),
            Palabras INT,
            Volumen INT,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
        )
    END
    ''')

    conn.commit()
    print("Tablas creadas correctamente.")

if __name__ == "__main__":
    crear_tablas()
