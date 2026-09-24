# infra/postgres

Scripts de inicialización de PostgreSQL 16 montados por `docker-compose.yml` en
`/docker-entrypoint-initdb.d` (se ejecutan solo al crear el volumen por primera vez).

| Archivo | Propósito |
|---|---|
| `init/01-app-role.sql` | Crea el rol `aegis_app` con privilegios acotados y default privileges sobre tablas futuras. |

## Uso del rol restringido

1. Migraciones y seeds corren como dueño del esquema (`aegis`), igual que hoy.
2. Para que el backend respete la inmutabilidad del audit ledger a nivel de base de datos,
   apunte `DATABASE_URL` al rol de aplicación:

   ```
   DATABASE_URL=postgresql+psycopg://aegis_app:aegis_app@db:5432/aegis
   ```

   La migración `0002_audit_ledger` ya revoca `UPDATE`/`DELETE` sobre `audit_events` para `aegis_app`.
3. Las políticas RLS usan `FORCE ROW LEVEL SECURITY`, por lo que aplican tanto al dueño como a `aegis_app`.

Si el volumen ya existía antes de agregar este script, ejecútelo manualmente:

```bash
docker compose exec -T db psql -U aegis -d aegis < infra/postgres/init/01-app-role.sql
```
