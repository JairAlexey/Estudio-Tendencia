import psycopg2
import urllib.parse as urlparse
import os

PG_URL = os.getenv("DATABASE_URL")
if not PG_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está definida. Debe contener la cadena de conexión a PostgreSQL.")

try:
    url = urlparse.urlparse(PG_URL)
    conn = psycopg2.connect(
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    print("✅ Conexión exitosa a PostgreSQL Railway.")
    conn.close()
except Exception as e:
    print("❌ Error conectando a PostgreSQL Railway:")
    print(e)