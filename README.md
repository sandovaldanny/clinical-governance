# AEGIS — Arquetipo del sistema

Este repositorio es el **arquetipo técnico** (scaffold) de AEGIS, la plataforma de gobierno clínico de
Alkalma Health, construido a partir de:

- `docs/AEGIS_Requerimiento_Funcional_Alkalma.md` — requerimiento funcional (fuente de negocio).
- `docs/AEGIS_Arquitectura_Tecnica.md` — arquitectura técnica (decisiones y justificación).

No implementa los 19 módulos completos. Implementa el **núcleo transversal** (autenticación, RBAC,
multi-centro con Row-Level Security, audit trail inmutable, motor de reglas) y **un módulo vertical
completo (UCCA)** como patrón de referencia, más un stub de Acciones Correctivas para mostrar cómo un
segundo módulo se conecta al mismo núcleo. El resto de los módulos (CPG, medicación/JAWDA, OPPE, FPPE,
Peer Review, Credentialing, Incidentes, Quejas, CME, Inteligencia Ejecutiva) se agregan siguiendo
exactamente el mismo patrón que `domains/governance/ucca`.

## Estructura

```
apps/
  backend/
    app/
      core/            # config, base de datos, seguridad, RBAC, audit trail — usado por TODOS los módulos
      domains/
        identity/       # M01 + M02: usuarios, roles, permisos, centros, profesiones, profesionales
        governance/
          ucca/          # M04 — módulo de referencia completo (modelo, reglas, API)
          corrective_actions/  # M06 — stub que consume hallazgos de UCCA
      rules_engine/     # motor de reglas desacoplado (sección 8 de la arquitectura técnica)
      jobs/             # trabajos programados (ej. reporte semanal, sección 9 del funcional)
    alembic/            # migraciones versionadas, incluye RLS y audit ledger
    tests/
  frontend/
    src/
      theme/            # tokens de marca Alkalma (branding configurable, sección 5 del funcional)
      auth/              # login + contexto de sesión
      layout/            # shell de navegación por rol
      modules/ucca/       # pantalla de referencia para un módulo
docs/                 # los dos documentos fuente, para que el equipo siempre los tenga a mano
```

## Cómo se agrega un módulo nuevo

1. Crear `apps/backend/app/domains/<grupo>/<modulo>/{models,schemas,service,router}.py` siguiendo `ucca/` como
   plantilla.
2. Las tablas nuevas **siempre** incluyen `facility_id` + política RLS (ver
   `alembic/versions/0003_rls_policies.py`) — es parte del checklist de revisión de código, no opcional.
3. Toda escritura relevante pasa por `app.core.audit.record_event(...)` o por el listener automático de
   SQLAlchemy — nunca se registra auditoría "a mano" dentro de cada servicio.
4. Cualquier criterio configurable (umbral, regla de aplicabilidad, versión de guía) se evalúa a través de
   `app.rules_engine.engine.evaluate(...)`, no con `if` embebidos en el servicio del módulo.
5. Registrar el router del módulo en `apps/backend/app/api.py`.

## Cómo correr localmente

```bash
cp .env.example .env
docker compose up --build
```

- Backend: http://localhost:8000/docs (OpenAPI)
- Frontend: http://localhost:5173
- Postgres: localhost:5432 (usuario/clave en `.env.example`)

La primera vez, aplicar las migraciones:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed_demo_data
```

En local sin Docker:

```bash
cd apps/backend && source .venv/bin/activate
alembic upgrade head
python -m app.scripts.seed_demo_data
```

El seed de demostración carga centros (Al Bateen, Al Falah), profesiones, especialidades,
roles, usuarios demo, catálogos JAWDA/OMH001 y 21 criterios UCCA (incl. investigaciones OMH001).
Es idempotente — puede ejecutarse varias veces.

Esto crea el esquema maestro, el audit ledger, las políticas RLS y el usuario
**System Administrator** inicial (contraseña temporal impresa en consola, forzada a cambiar en el primer
acceso — ver sección 6.3 de la arquitectura técnica).

### Modo local sin autenticación (solo desarrollo)

Para probar la UI sin login, puede activarse el bypass de auth **únicamente en entornos locales**:

```bash
# apps/backend/.env
AUTH_DISABLED=true

# apps/frontend/.env
VITE_AUTH_DISABLED=true
```

Reinicie backend y frontend después de cambiar estas variables (Vite lee `.env` solo al arrancar).
**Nunca** suba `AUTH_DISABLED=true` ni `VITE_AUTH_DISABLED=true` a staging o producción.

## Supuestos de este arquetipo (a validar con el equipo)

- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL 16.
- Autenticación: usuario/contraseña local en esta fase; el modelo de `Users` ya desacopla
  `auth_provider`/`external_id` para no requerir migración cuando se active SSO con Entra ID.
- Frontend: React + TypeScript + Vite, sin librería de UI específica todavía (los tokens de marca están
  aislados en `theme/brand-tokens.ts` para que el branding definitivo de Alkalma se conecte sin tocar
  componentes).
- No incluye orquestación de contenedores en la nube (Azure Container Apps/AKS) ni CI/CD — eso pertenece
  al diseño de despliegue, no al arquetipo de código.
