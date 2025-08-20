
import pyodbc
import os

# Configuración de la conexión a Azure SQL
server   = "tendencias21.database.windows.net"
database = "tendencias"
username = "admin123"
password = "*123Admin*"

conn = pyodbc.connect(
	"DRIVER={ODBC Driver 17 for SQL Server};"
	f"SERVER=tcp:{server},1433;"
	f"DATABASE={database};UID={username};PWD={password};"
	"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

cursor = conn.cursor()
