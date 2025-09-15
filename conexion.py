import pyodbc
import os

# Configuración de la conexión a Azure SQL
server   = "sqlserverestudiotendencia.database.windows.net"
database = "estudio-tendencia"
username = "estudiotendenciaadmin123"
password = "*Admin123*"

conn = pyodbc.connect(
	"DRIVER={ODBC Driver 17 for SQL Server};"
	f"SERVER=tcp:{server},1433;"
	f"DATABASE={database};UID={username};PWD={password};"
	"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

cursor = conn.cursor()

def ensure_connection():
    global conn, cursor
    try:
        cursor.execute("SELECT 1")
    except pyodbc.Error:
        print("Reconectando a SQL Server...")
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER=tcp:{server},1433;"
            f"DATABASE={database};UID={username};PWD={password};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        )
        cursor = conn.cursor()
