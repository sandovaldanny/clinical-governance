# AEGIS — Clinical Governance Platform by Alkalma Health

Arquetipo técnico (mockup funcional) de **AEGIS**, la plataforma de gobierno clínico de Alkalma Health,
construido a partir de dos documentos fuente que viven en `docs/`:

- `docs/AEGIS_Requerimiento_Funcional_Alkalma.md` — requerimiento funcional (fuente de negocio).
- `docs/AEGIS_Arquitectura_Tecnica.md` — arquitectura técnica (decisiones y justificación).

No implementa los 19 módulos. Implementa el **núcleo transversal** (autenticación, RBAC, multi-centro con
Row-Level Security, audit trail inmutable, motor de reglas) y **un módulo vertical completo (UCCA, M04)**
como patrón de referencia, más un stub de Acciones Correctivas (M06) que muestra cómo un segundo módulo se
conecta al mismo núcleo. El resto (CPG, medicación/JAWDA, OPPE, FPPE, Peer Review, Credentialing,
Incidentes, Quejas, CME, Inteligencia Ejecutiva) se agrega siguiendo el mismo patrón que
`backend/app/domains/governance/ucca`.

## Estructura del repositorio

```
├── backend/                 # FastAPI + SQLAlchemy 2 + Alembic (monolito modular por dominios)
│   ├── app/
│   │   ├── core/            #   config, sesión DB + contexto RLS, JWT/Argon2, RBAC, audit ledger
│   │   ├── domains/
│   │   │   ├── identity/    #   M01 + M02: usuarios, roles, permisos, centros, profesiones, profesionales
│   │   │   └── governance/
│   │   │       ├── ucca/                # M04 — módulo de referencia completo (models, schemas, service, router)
│   │   │       └── corrective_actions/  # M06 — stub que consume hallazgos de UCCA por finding_id
│   │   ├── rules_engine/    #   motor de reglas versionado y desacoplado (sección 8 arquitectura)
│   │   ├── jobs/            #   scheduler + esqueleto del reporte semanal de antipsicóticos (M05)
│   │   ├── scripts/         #   seed del System Administrator inicial y seed de demostración
│   │   ├── api.py           #   registro único de routers
│   │   └── main.py
│   ├── alembic/versions/    #   0001 esquema maestro · 0002 audit ledger · 0003 RLS · 0004 UCCA/M06
│   └── tests/               #   RBAC, motor de reglas, smoke HTTP (sin dependencia de Postgres)
├── frontend/                # React 18 + TypeScript + Vite
│   └── src/
│       ├── theme/           #   brand-tokens.ts — único punto de branding Alkalma
│       ├── auth/            #   login + contexto de sesión (JWT en memoria)
│       ├── api/             #   cliente fetch con proxy /api → backend
│       ├── layout/          #   AppShell, Sidebar, nav-config por módulo
│       ├── components/      #   DataTable, PageHeader
│       ├── hooks/           #   useApiList
│       └── modules/         #   admin (M01/M02), indicators (M04/M05), ucca (M04)
├── infra/                   # infraestructura local: init SQL de Postgres (rol aegis_app restringido)
├── branding/                # identidad Alkalma: guía de tokens, logo placeholder, insumos pendientes
├── docs/                    # requerimiento funcional, arquitectura técnica, specs/planes de proceso
├── graphify-out/            # grafo de conocimiento del código (graphify) — regenerable
├── docker-compose.yml       # db :5432 · backend :8000 · frontend :5173
└── .env.example             # variables para docker compose
```

## Desarrollo local

Requisitos: Docker (recomendado) **o** Python 3.12 + Node 20 + PostgreSQL 16.

### Con Docker

```bash
cp .env.example .env
docker compose up --build
# la primera vez:
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed_demo_data
```

- Backend / OpenAPI: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Postgres: `localhost:5432` (credenciales en `.env.example`)

### Sin Docker

```bash
# Backend
cd backend
cp .env.example .env                   # ajustar DATABASE_URL a su Postgres local
python3.12 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/alembic upgrade head
./.venv/bin/python -m app.scripts.seed_demo_data
./.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
cp .env.example .env
npm install && npm run dev             # proxy /api → http://localhost:8000
```

### Pruebas y build

```bash
cd backend && ./.venv/bin/python -m pytest -q     # no requiere Postgres
cd frontend && npm run build                     # tsc -b && vite build
docker compose config --quiet                    # valida el compose
```

## Datos de demostración

`seed_demo_data` es idempotente. Carga centros (Al Bateen, Al Falah), profesiones, especialidades,
cargos, 9 roles con su matriz de permisos, catálogos JAWDA/OMH001 (10 investigaciones, clases de
medicación), 7 usuarios demo, 3 profesionales, la plantilla UCCA v1 con 21 criterios y un ciclo Q3-2026.

| Usuario | Rol | Alcance |
|---|---|---|
| `admin@alkalma.health` | System Administrator | corporativo (contraseña temporal de `SEED_ADMIN_TEMP_PASSWORD`, cambio forzado) |
| `governance.lead@alkalma.health` | Governance Lead | corporativo |
| `md.bateen@alkalma.health` / `md.falah@alkalma.health` | Medical Director | un centro cada uno |
| `quality@alkalma.health` | Quality Manager | corporativo |
| `auditor@alkalma.health` | Auditor | Al Bateen |
| `clinician@alkalma.health` | Clinician | Al Bateen |

Contraseña de los usuarios demo (excepto admin): la imprime el seed al terminar.

### Modo local sin autenticación (solo desarrollo)

```bash
# backend/.env
AUTH_DISABLED=true
# frontend/.env
VITE_AUTH_DISABLED=true
```

Reinicie ambos procesos (Vite lee `.env` solo al arrancar). El backend actúa como el System Administrator
del seed y la UI muestra una franja de advertencia. **Nunca** habilitar en staging o producción.

## Cómo se agrega un módulo nuevo

1. Crear `backend/app/domains/<grupo>/<modulo>/{models,schemas,service,router}.py` usando `ucca/` como plantilla.
2. Toda tabla operativa **siempre** incluye `facility_id` + política RLS (patrón en
   `alembic/versions/0003_rls_policies.py` y `0004_ucca_module.py`). Es parte del checklist de revisión, no opcional.
3. Toda escritura relevante pasa por `app.core.audit.record_event(...)`; nunca se escribe auditoría "a mano".
4. Cualquier criterio configurable (umbral, aplicabilidad por profesión, versión de guía) se evalúa con
   `app.rules_engine.engine.evaluate(...)`, no con `if` embebidos en el servicio.
5. Todo endpoint declara su permiso con `require_permission("<modulo>.<accion>")` y valida centro con
   `require_facility_access(...)`.
6. Registrar el router en `backend/app/api.py` y la ruta/pantalla en `frontend/src/App.tsx` + `layout/nav-config.ts`.

## Cómo se cumplen las decisiones de la arquitectura técnica

| Decisión (arquitectura técnica) | Dónde vive |
|---|---|
| RBAC centralizado, System Administrator sin bypass de código (§6.2) | `backend/app/core/rbac.py`, permisos otorgados por rol en el seed |
| Segregación multi-centro con RLS nativo (§5.2) | `core/database.py::set_tenant_context` + policies en migraciones 0003/0004 |
| Audit ledger append-only, UPDATE/DELETE revocados (§7) | `core/audit.py`, migración 0002, rol `aegis_app` en `infra/postgres/` |
| Versionado plantilla → versión → criterio (§5.3) | `domains/governance/ucca/models.py` |
| Inmutabilidad de resultados aprobados (§5.4) | `ucca/service.py::approve_result` (409 si ya aprobado) |
| "No aplica" con razón trazable (regla global #5) | `ucca/service.py::record_result` (422 sin razón) |
| Motor de reglas desacoplado y reproducible (§8) | `rules_engine/engine.py` + `rulesets/omh001_example.py` |
| Job semanal que falla ruidosamente (§9) | `jobs/scheduler.py`, `jobs/weekly_antipsychotic_report.py` (esqueleto) |
| Identidad desacoplada del proveedor de auth para SSO futuro (§6.1) | `identity/models.py::User.auth_provider / external_id` |
| Branding por tokens centralizados (§10) | `frontend/src/theme/brand-tokens.ts`, `branding/` (paleta oficial Alkalma, Montserrat) |
| Interfaz bilingüe ES/EN | `frontend/src/i18n/` (react-i18next; toggle en header, persistido en localStorage) |
| Perfil del usuario autenticado en header | `GET /identity/me` → `frontend/src/components/ProfileMenu.tsx` |

## Supuestos de este arquetipo (a validar con el equipo)

- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL 16.
- Autenticación: usuario/contraseña local (fase 1); `Users` ya desacopla `auth_provider`/`external_id`
  para activar SSO con Entra ID sin migrar datos.
- Frontend: React + TypeScript + Vite, sin librería de UI todavía; el branding definitivo se conecta
  reemplazando `brand-tokens.ts` y los assets de `branding/`.
- Scheduler embebido (APScheduler) solo para el arquetipo; en producción, worker dedicado (Celery beat).
- No incluye orquestación en nube (Azure Container Apps/AKS) ni CI/CD — pertenece al diseño de despliegue.
