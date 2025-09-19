import psycopg2
import os
import urllib.parse as urlparse

# Permite usar una sola variable de entorno o el string directo
PG_URL = os.getenv("DATABASE_URL", "postgresql://postgres:GzBNabTYXBdUpYswLIYZkvFuIOvdwDXr@gondola.proxy.rlwy.net:11456/railway")

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
    if cursor is None:
        print("Cursor es None. Intentando reconectar a PostgreSQL...")
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