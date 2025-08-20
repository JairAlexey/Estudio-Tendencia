-- Ejecuta este script en SQL Server Management Studio para revisar la estructura de la tabla

-- Ver estructura de la tabla
EXEC sp_help 'proyectos_tendencias';

-- Ver si hay triggers en la tabla
SELECT name, parent_id FROM sys.triggers WHERE parent_id = OBJECT_ID('proyectos_tendencias');

-- Probar inserción y obtención de ID
INSERT INTO proyectos_tendencias (
    tipo_carpeta, carrera_referencia, carrera_estudio, palabra_semrush, codigo_ciiu, ingresos_2023, ventas12_2023, ventas0_2023
) VALUES ('TEST', 'TEST_CARRERA', 'TEST_ESTUDIO', 'TEST_SEMRUSH', 'TEST_CIIU', 123.45, 67.89, 10.11);
SELECT SCOPE_IDENTITY() AS InsertedID;
