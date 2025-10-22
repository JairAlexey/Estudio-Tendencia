import psycopg2
import os
import urllib.parse as urlparse
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

PG_URL = os.getenv("DATABASE_URL")
if not PG_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está definida. Debe contener la cadena de conexión a PostgreSQL.")

def get_connection():
    url = urlparse.urlparse(PG_URL)
    return psycopg2.connect(
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
except Exception as e:
    print("Error conectando a PostgreSQL:", e)
    conn = None
    cursor = None

def is_connected():
    return conn is not None and cursor is not None

def ensure_connection():
    global conn, cursor
    # Si el cursor es None o está cerrado, reconectar
    if cursor is None or getattr(cursor, 'closed', False):
        print("Cursor es None o está cerrado. Intentando reconectar a PostgreSQL...")
        try:
            conn = get_connection()
            cursor = conn.cursor()
        except Exception as e:
            print("Error reconectando a PostgreSQL:", e)
        return
    try:
        cursor.execute("SELECT 1")
    except Exception:
        print("Reconectando a PostgreSQL...")
        try:
            conn = get_connection()
            cursor = conn.cursor()
        except Exception as e:
            print("Error reconectando a PostgreSQL:", e)