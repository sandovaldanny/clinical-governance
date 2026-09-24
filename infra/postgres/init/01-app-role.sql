-- Rol de aplicación con privilegios acotados (sección 7 y 13 de la arquitectura técnica).
--
-- Las migraciones (alembic) corren como el dueño del esquema (POSTGRES_USER, por defecto
-- "aegis"). El backend en runtime puede conectarse como "aegis_app": la migración
-- 0002_audit_ledger revoca UPDATE/DELETE sobre audit_events a este rol, de modo que la
-- inmutabilidad del audit trail queda impuesta por la base de datos, no solo por código.
--
-- Este script solo se ejecuta la primera vez que se inicializa el volumen de Postgres.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aegis_app') THEN
        CREATE ROLE aegis_app LOGIN PASSWORD 'aegis_app';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE aegis TO aegis_app;
GRANT USAGE ON SCHEMA public TO aegis_app;

-- Tablas que se creen después (vía alembic, como el dueño) quedan accesibles al rol.
ALTER DEFAULT PRIVILEGES FOR ROLE aegis IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO aegis_app;
ALTER DEFAULT PRIVILEGES FOR ROLE aegis IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO aegis_app;
