import pyodbc
from conexion import conn, cursor
# Script para crear tablas necesarias en la base de datos


# Script para crear todas las tablas necesarias en la base de datos
def crear_tablas():
    tablas = [
        # carreras_facultad
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'carreras_facultad')
        BEGIN
            CREATE TABLE carreras_facultad (
                ID int IDENTITY(1,1) NOT NULL,
                Facultad nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                Nivel nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                Carrera nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                CONSTRAINT PK_carreras_facultad PRIMARY KEY (ID)
            )
        END''',
        # codigos_carrera
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'codigos_carrera')
        BEGIN
            CREATE TABLE codigos_carrera (
                ID_Carrera int NOT NULL,
                Codigo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
                CONSTRAINT PK_codigos_carrera PRIMARY KEY (ID_Carrera,Codigo)
            )
        END''',
        # proyectos_tendencias
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'proyectos_tendencias')
        BEGIN
            CREATE TABLE proyectos_tendencias (
                id int IDENTITY(1,1) NOT NULL,
                tipo_carpeta nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                carrera_referencia nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                carrera_estudio nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                palabra_semrush nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                codigo_ciiu nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                CONSTRAINT PK_proyectos_tendencias PRIMARY KEY (id)
            )
        END''',
        # linkedin
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'linkedin')
        BEGIN
            CREATE TABLE linkedin (
                id int IDENTITY(1,1) NOT NULL,
                proyecto_id int NULL,
                Tipo nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                Region nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                Profesionales int NULL,
                AnunciosEmpleo int NULL,
                PorcentajeAnunciosProfesionales decimal(10,2) NULL,
                DemandaContratacion nvarchar(50),
                CONSTRAINT PK_linkedin PRIMARY KEY (id),
                CONSTRAINT FK_linkedin_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
            )
        END''',
        # modalidad_oferta
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'modalidad_oferta')
        BEGIN
            CREATE TABLE modalidad_oferta (
                id int IDENTITY(1,1) NOT NULL,
                proyecto_id int NULL,
                presencial nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                virtual nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                CONSTRAINT PK_modalidad_oferta PRIMARY KEY (id),
                CONSTRAINT FK_modalidad_oferta_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
            )
        END''',
        # semrush
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'semrush')
        BEGIN
            CREATE TABLE semrush (
                id int IDENTITY(1,1) NOT NULL,
                proyecto_id int NULL,
                VisionGeneral nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                Palabras int NULL,
                Volumen int NULL,
                CONSTRAINT PK_semrush PRIMARY KEY (id),
                CONSTRAINT FK_semrush_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
            )
        END''',
        # semrush_base
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'semrush_base')
        BEGIN
            CREATE TABLE semrush_base (
                ID_Carrera int NOT NULL,
                Vision_General int NULL,
                Palabras int NULL,
                Volumen int NULL,
                CONSTRAINT PK_semrush_base PRIMARY KEY (ID_Carrera),
                CONSTRAINT FK_semrush_base_carreras_facultad FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
            )
        END''',
        # tendencias
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tendencias')
        BEGIN
            CREATE TABLE tendencias (
                id int IDENTITY(1,1) NOT NULL,
                proyecto_id int NULL,
                palabra nvarchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
                promedio float NULL,
                CONSTRAINT PK_tendencias PRIMARY KEY (id),
                CONSTRAINT FK_tendencias_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
            )
        END''',
        # tendencias_carrera
        '''IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'tendencias_carrera')
        BEGIN
            CREATE TABLE tendencias_carrera (
                ID_Carrera int NOT NULL,
                Palabra nvarchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
                Cantidad int NULL,
                CONSTRAINT PK_tendencias_carrera PRIMARY KEY (ID_Carrera,Palabra),
                CONSTRAINT FK_tendencias_carrera_carreras_facultad FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
            )
        END'''
    ]
    for sql in tablas:
        cursor.execute(sql)
    conn.commit()
    print("Todas las tablas han sido creadas correctamente.")

if __name__ == "__main__":
    crear_tablas()