import psycopg2
from conexion import conn, cursor

# Script para crear todas las tablas necesarias en la base de datos
def crear_tablas():

    tablas = [
        # '''
        # CREATE TABLE IF NOT EXISTS proyectos_tendencias (
        #     id SERIAL PRIMARY KEY,
        #     tipo_carpeta VARCHAR(100),
        #     carrera_referencia VARCHAR(200),
        #     carrera_estudio VARCHAR(200),
        #     palabra_semrush VARCHAR(200),
        #     codigo_ciiu VARCHAR(50),
        #     carrera_linkedin VARCHAR(200),
        #     mensaje_error VARCHAR(500)
        # );
        # ''',
        '''
        CREATE TABLE IF NOT EXISTS codigos_carrera (
            ID_Carrera INTEGER NOT NULL,
            Codigo VARCHAR(50) NOT NULL,
            PRIMARY KEY (ID_Carrera, Codigo)
        );
        '''
        # '''CREATE TABLE IF NOT EXISTS carreras_facultad (
        #     ID SERIAL PRIMARY KEY,
        #     Facultad VARCHAR(200),
        #     Nivel VARCHAR(100),
        #     Carrera VARCHAR(200)
        # );
        # ''',
        # '''
        # CREATE TABLE IF NOT EXISTS grafico_radar_datos (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
        #     valor_busqueda FLOAT,
        #     valor_competencia_presencialidad FLOAT,
        #     valor_competencia_virtualidad FLOAT,
        #     valor_linkedin FLOAT,
        #     valor_mercado FLOAT,
        #     updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        # );
        # ''',
        # # # linkedin
        # '''
        # CREATE TABLE IF NOT EXISTS linkedin (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
        #     Tipo VARCHAR(50),
        #     Region VARCHAR(100),
        #     Profesionales INTEGER,
        #     AnunciosEmpleo INTEGER,
        #     PorcentajeAnunciosProfesionales DECIMAL(10,2),
        #     DemandaContratacion VARCHAR(50)
        # );
        # ''',
        # # # modalidad_oferta
        # '''
        # CREATE TABLE IF NOT EXISTS modalidad_oferta (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
        #     presencial VARCHAR(50),
        #     virtual VARCHAR(50)
        # );
        # ''',
        # # # semrush
        # '''
        # CREATE TABLE IF NOT EXISTS semrush (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
        #     VisionGeneral VARCHAR(200),
        #     Palabras INTEGER,
        #     Volumen INTEGER
        # );
        # ''',
        # # # semrush_base
        # '''
        # CREATE TABLE IF NOT EXISTS semrush_base (
        #     ID_Carrera INTEGER PRIMARY KEY,
        #     Vision_General INTEGER,
        #     Palabras INTEGER,
        #     Volumen INTEGER,
        #     FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
        # );
        # ''',
        # # # tendencias
        # '''
        # CREATE TABLE IF NOT EXISTS tendencias (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
        #     palabra VARCHAR(200),
        #     promedio FLOAT
        # );
        # ''',
        # # # tendencias_carrera
        # '''
        # CREATE TABLE IF NOT EXISTS tendencias_carrera (
        #     ID_Carrera INTEGER,
        #     Palabra VARCHAR(100),
        #     Cantidad INTEGER,
        #     PRIMARY KEY (ID_Carrera, Palabra),
        #     FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
        # );
        # ''',
        # # # scraper_queue
        # '''
        # CREATE TABLE IF NOT EXISTS scraper_queue (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
        #     status VARCHAR(20) NOT NULL DEFAULT 'queued',
        #     tries INTEGER NOT NULL DEFAULT 0,
        #     error TEXT,
        #     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #     started_at TIMESTAMP,
        #     finished_at TIMESTAMP
        # );
        # ''',
        # # # presentation_queue
        # '''
        # CREATE TABLE IF NOT EXISTS presentation_queue (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
        #     status VARCHAR(20) NOT NULL DEFAULT 'queued',
        #     tries INTEGER NOT NULL DEFAULT 0,
        #     error TEXT,
        #     created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        #     started_at TIMESTAMP,
        #     finished_at TIMESTAMP,
        #     dropbox_url VARCHAR(500),
        #     file_name VARCHAR(255)
        # );
        # ''',
        # # # mercado_datos
        # '''
        # CREATE TABLE IF NOT EXISTS mercado_datos (
        #     id SERIAL PRIMARY KEY,
        #     hoja_origen VARCHAR(50),
        #     actividad_economica VARCHAR(200),
        #     valor_2023 FLOAT
        # );
        # ''',
        # # # datos_solicitud
        # '''
        # CREATE TABLE IF NOT EXISTS datos_solicitud (
        #     id SERIAL PRIMARY KEY,
        #     proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
        #     nombre_programa VARCHAR(200),
        #     facultad_propuesta VARCHAR(200),
        #     duracion VARCHAR(50),
        #     modalidad VARCHAR(50),
        #     nombre_proponente VARCHAR(200),
        #     facultad_proponente VARCHAR(200),
        #     cargo_proponente VARCHAR(100)
        # );
        # '''
    ]
    for sql in tablas:
        cursor.execute(sql)
    conn.commit()
    print("Todas las tablas han sido creadas correctamente.")

if __name__ == "__main__":
    crear_tablas()