import sys
import os
import psycopg2

# Add the parent directory to sys.path to find the conexion module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the parent directory
from conexion import conn, cursor

# Script para crear todas las tablas necesarias en la base de datos
def crear_tablas():

    tablas = [
        '''
        CREATE TABLE IF NOT EXISTS proyectos_tendencias (
            id SERIAL PRIMARY KEY,
            tipo_carpeta VARCHAR(100),
            carrera_referencia VARCHAR(200),
            carrera_estudio VARCHAR(200),
            palabra_semrush VARCHAR(200),
            codigo_ciiu VARCHAR(50),
            carrera_linkedin VARCHAR(200),
            id_ticket VARCHAR(100),
            mensaje_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS codigos_carrera (
            ID_Carrera INTEGER NOT NULL,
            Codigo VARCHAR(50) NOT NULL,
            PRIMARY KEY (ID_Carrera, Codigo)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS carreras_facultad (
            ID SERIAL PRIMARY KEY,
            Facultad VARCHAR(200),
            Nivel VARCHAR(100),
            Carrera VARCHAR(200)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS grafico_radar_datos (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
            valor_busqueda FLOAT,
            valor_competencia_presencialidad FLOAT,
            valor_competencia_virtualidad FLOAT,
            valor_linkedin FLOAT,
            valor_mercado FLOAT,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        # # # linkedin
        '''
        CREATE TABLE IF NOT EXISTS linkedin (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id) ON DELETE CASCADE,
            Tipo VARCHAR(50),
            Region VARCHAR(100),
            Profesionales INTEGER,
            AnunciosEmpleo INTEGER,
            PorcentajeAnunciosProfesionales DECIMAL(10,2),
            DemandaContratacion VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        # # # modalidad_oferta
        '''
        CREATE TABLE IF NOT EXISTS modalidad_oferta (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
            presencial VARCHAR(50),
            virtual VARCHAR(50)
        );
        ''',
        # # # semrush
        '''
        CREATE TABLE IF NOT EXISTS semrush (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id) ON DELETE CASCADE,
            VisionGeneral VARCHAR(200),
            Palabras INTEGER,
            Volumen INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        # # # semrush_base
        '''
        CREATE TABLE IF NOT EXISTS semrush_base (
            ID_Carrera INTEGER PRIMARY KEY,
            Vision_General INTEGER,
            Palabras INTEGER,
            Volumen INTEGER,
            FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
        );
        ''',
        # # # tendencias
        '''
        CREATE TABLE IF NOT EXISTS tendencias (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id),
            palabra VARCHAR(200),
            promedio FLOAT
        );
        ''',
        # # # tendencias_carrera
        '''
        CREATE TABLE IF NOT EXISTS tendencias_carrera (
            ID_Carrera INTEGER,
            Palabra VARCHAR(100),
            Cantidad INTEGER,
            PRIMARY KEY (ID_Carrera, Palabra),
            FOREIGN KEY (ID_Carrera) REFERENCES carreras_facultad(ID)
        );
        ''',
        # # # scraper_queue
        '''
        CREATE TABLE IF NOT EXISTS scraper_queue (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
            status VARCHAR(20) NOT NULL DEFAULT 'queued',
            tries INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP,
            priority INTEGER NOT NULL DEFAULT 2
        );
        ''',
        # # # presentation_queue
        '''
        CREATE TABLE IF NOT EXISTS presentation_queue (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
            status VARCHAR(20) NOT NULL DEFAULT 'queued',
            tries INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP,
            file_name VARCHAR(255),
            file_data BYTEA,
            tipo_reporte VARCHAR(50) DEFAULT 'viabilidad'
        );
        ''',
        # # # mercado_datos
        '''
        CREATE TABLE IF NOT EXISTS mercado_datos (
            id SERIAL PRIMARY KEY,
            hoja_origen VARCHAR(50),
            actividad_economica VARCHAR(200),
            valor_2023 FLOAT
        );
        ''',
        # # # cr_mercado_datos
        '''
        CREATE TABLE IF NOT EXISTS cr_mercado_datos (
            id SERIAL PRIMARY KEY,
            hoja_origen VARCHAR(50),
            actividad_economica VARCHAR(200),
            valor_2023 FLOAT
        );
        ''',
        # # # datos_solicitud
        '''
        CREATE TABLE IF NOT EXISTS datos_solicitud (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id),
            nombre_programa VARCHAR(200),
            facultad_propuesta VARCHAR(200),
            duracion VARCHAR(50),
            modalidad VARCHAR(50),
            nombre_proponente VARCHAR(200),
            facultad_proponente VARCHAR(200),
            cargo_proponente VARCHAR(100)
        );
        ''',
        # # # carpetas
        '''
        CREATE TABLE IF NOT EXISTS carpetas (
            id SERIAL PRIMARY KEY,
            tipo_carpeta VARCHAR(100) NOT NULL,
            nombre_proyecto VARCHAR(255) NOT NULL,
            url_proyecto TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tipo_carpeta, nombre_proyecto)
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS carpetas_queue (
            id SERIAL PRIMARY KEY,
            status VARCHAR(20) NOT NULL DEFAULT 'queued',
            tipo_carpeta VARCHAR(100),
            tries INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS linkedin_aptitudes (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id) ON DELETE CASCADE,
            carrera_estudio VARCHAR(200),
            ubicacion VARCHAR(100),
            nombre VARCHAR(200),
            cantidad FLOAT,
            porcentaje VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS linkedin_ubicaciones (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER REFERENCES proyectos_tendencias(id) ON DELETE CASCADE,
            carrera_estudio VARCHAR(200),
            ubicacion VARCHAR(100),
            nombre VARCHAR(200),
            cantidad FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        '''
        CREATE TABLE IF NOT EXISTS seguimiento_proyecto (
            id SERIAL PRIMARY KEY,
            proyecto_id INTEGER NOT NULL REFERENCES proyectos_tendencias(id) ON DELETE CASCADE,
            brief BOOLEAN NOT NULL DEFAULT TRUE,
            modelo_prioridad BOOLEAN NOT NULL DEFAULT TRUE,
            modelo_tendencia BOOLEAN NOT NULL DEFAULT FALSE,
            enviada_viabilidad BOOLEAN NOT NULL DEFAULT FALSE,
            solicitud_inv_mercados BOOLEAN NOT NULL DEFAULT FALSE,
            enviada_inv_mercados BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );        
        '''
    ]
    
    for sql in tablas:
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(f"Error creando tabla: {e}")
            conn.rollback()
    
    print("Todas las tablas han sido creadas correctamente.")

if __name__ == "__main__":
    crear_tablas()