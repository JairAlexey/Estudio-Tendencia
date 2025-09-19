import pyodbc
import os

# Configuración de la conexión a Azure SQL
server   = "sqlserverestudiotendencia.database.windows.net"
database = "estudio-tendencia"
username = "estudiotendenciaadmin123"
password = "*Admin123*"

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};UID={username};PWD={password};"
        "Encrypt=no;Connection Timeout=30;"
    )
    cursor = conn.cursor()
except pyodbc.Error as e:
    print("Error al conectar a SQL Server:", e)
    raise

def ensure_connection():
    global conn, cursor
    try:
        cursor.execute("SELECT 1")
    except pyodbc.Error:
        print("Reconectando a SQL Server...")
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database};UID={username};PWD={password};"
            "Encrypt=no;Connection Timeout=30;"
        )
        cursor = conn.cursor()
