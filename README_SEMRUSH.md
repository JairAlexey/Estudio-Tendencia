# Scraper de Semrush - Versión Corregida

## Descripción

El scraper de Semrush ha sido corregido para funcionar con la base de datos SQL Server, siguiendo la misma estructura que el scraper de LinkedIn. Ahora utiliza `proyecto_id` en lugar de archivos Excel.

## Cambios Realizados

### 1. Estructura del Scraper (`scrapers/semrush.py`)

- ✅ Eliminadas referencias a Excel (`xlwings`)
- ✅ Integrado con la base de datos SQL Server
- ✅ Uso de `proyecto_id` como parámetro principal
- ✅ Importación de funciones de base de datos desde `linkedin_database.py`
- ✅ Guardado de datos en la tabla `semrush`

### 2. Base de Datos

- ✅ Tabla `proyectos_tendencias` con campo `palabra_semrush`
- ✅ Tabla `semrush` con campos: `VisionGeneral`, `Palabras`, `Volumen`
- ✅ Funciones `extraer_datos_tabla()` y `guardar_datos_sql()` actualizadas

## Uso

### 1. Preparación

```bash
# Crear las tablas en la base de datos
python crear_tablas.py

# Insertar datos de prueba (opcional)
python insert_test_data.py

# Ver proyectos existentes
python insert_test_data.py --show
```

### 2. Ejecutar el Scraper

```bash
# Ejecutar con un proyecto_id específico
python scrapers/semrush.py <proyecto_id>

# Ejemplo:
python scrapers/semrush.py 1
```

### 3. Probar la Base de Datos

```bash
# Probar funciones de base de datos
python test_semrush.py <proyecto_id>

# Ejemplo:
python test_semrush.py 1
```

## Estructura de Datos

### Tabla `proyectos_tendencias`
```sql
CREATE TABLE proyectos_tendencias (
    id SERIAL PRIMARY KEY,
    tipo_carpeta VARCHAR(100),
    carrera_referencia VARCHAR(200),
    carrera_estudio VARCHAR(200),
    palabra_semrush VARCHAR(200),  -- Palabra clave para Semrush
    codigo_ciiu VARCHAR(50),
    carrera_linkedin VARCHAR(200),
    mensaje_error TEXT
);
```

### Tabla `semrush`
```sql
CREATE TABLE semrush (
    id int IDENTITY(1,1) NOT NULL,
    proyecto_id int NULL,
    VisionGeneral nvarchar(200),  -- Volumen de búsquedas
    Palabras int NULL,             -- Número de palabras clave
    Volumen int NULL,              -- Volumen total
    CONSTRAINT PK_semrush PRIMARY KEY (id),
    CONSTRAINT FK_semrush_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos_tendencias(id)
)
```

## Variables de Entorno

Crear archivo `.env` con las credenciales de Semrush:

```env
SEMRUSH_USER=tu_email@ejemplo.com
SEMRUSH_PASS=tu_password
```

## Flujo de Trabajo

1. **Configuración**: El scraper lee la configuración del proyecto desde `proyectos_tendencias`
2. **Autenticación**: Inicia sesión en Semrush usando las credenciales del `.env`
3. **Búsqueda**: Busca la palabra clave especificada en `palabra_semrush`
4. **Extracción**: Extrae datos de:
   - Visión General (volumen de búsquedas)
   - Palabras clave relacionadas
   - Volumen total
5. **Guardado**: Almacena los resultados en la tabla `semrush`

## Datos Extraídos

- **VisionGeneral**: Volumen de búsquedas mensuales
- **Palabras**: Número de palabras clave relacionadas
- **Volumen**: Volumen total de búsquedas

## Manejo de Errores

- ✅ Validación de credenciales
- ✅ Verificación de existencia del proyecto
- ✅ Manejo de errores de conexión
- ✅ Logs detallados del proceso
- ✅ Limpieza de recursos (driver)

## Comparación con LinkedIn Scraper

| Característica | LinkedIn | Semrush |
|----------------|----------|---------|
| Parámetro principal | `proyecto_id` | `proyecto_id` |
| Base de datos | SQL Server | SQL Server |
| Tabla de configuración | `proyectos_tendencias` | `proyectos_tendencias` |
| Tabla de resultados | `linkedin` | `semrush` |
| Autenticación | Credenciales .env | Credenciales .env |
| Manejo de errores | ✅ | ✅ |

## Próximos Pasos

1. **Pruebas**: Ejecutar con datos reales
2. **Optimización**: Mejorar tiempos de espera
3. **Monitoreo**: Agregar métricas de rendimiento
4. **Escalabilidad**: Procesamiento en lotes

## Troubleshooting

### Error: "No se encontraron datos para el proyecto"
- Verificar que el `proyecto_id` existe en `proyectos_tendencias`
- Ejecutar `python insert_test_data.py --show` para ver proyectos disponibles

### Error: "Faltan credenciales de Semrush"
- Verificar archivo `.env` con `SEMRUSH_USER` y `SEMRUSH_PASS`

### Error: "No se pudo iniciar sesión"
- Verificar credenciales de Semrush
- Verificar conexión a internet
- Verificar que la cuenta no esté bloqueada

### Error de conexión a base de datos
- Verificar configuración en `conexion.py`
- Verificar que las tablas existan (`python crear_tablas.py`)

