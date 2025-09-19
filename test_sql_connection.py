import psycopg2
import urllib.parse as urlparse

# Configuración de la conexión a PostgreSQL Railway (nueva)
PG_URL = "postgresql://postgres:eSXetjVvVwefXiVucBCnduKLFJFpPnch@switchyard.proxy.rlwy.net:19724/railway"

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