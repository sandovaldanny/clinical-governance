# Graph Report - clinical-governance  (2026-10-12)

## Corpus Check
- 133 files · ~72,908 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .example 3, (none) 3, .ini 1)

## Summary
- 1088 nodes · 2840 edges · 61 communities (50 shown, 11 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `183635eb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- identity/service.py
- AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico
- deps.py
- ucca/service.py
- database.py
- AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico
- package.json
- compilerOptions
- engine.py
- 7. Módulos funcionales
- identity/schemas.py
- Global Constraints
- scheduler.py
- AEGIS — Clinical Governance Platform by Alkalma Health
- Reorganización de repo — AEGIS / clinical-governance
- test_identity_me.py
- alembic
- 9. Capacidades transversales
- branding — identidad Alkalma Health
- 13. Fases propuestas
- 6. Usuarios, autenticación y control de acceso
- 8. Flujos funcionales integrados
- infra/postgres
- 5. Branding y experiencia Alkalma
- MasterDataPage.tsx
- UsersPage.tsx
- MasterDataPage
- UccaCyclePage.tsx
- CurrentUser
- test_criteria.py
- make_client
- App.tsx
- FakeSession
- ChartAuditPage.tsx
- AEGIS Phase 1 — Module 1: User, Organization & Access Management
- test_users_update.py
- ucca/schemas.py
- test_roles.py
- cleanup
- types.ts
- test_users_status.py
- identity/router.py
- _fakes.py
- test_ucca_chart_audits.py
- UCCA — Auditoría por expediente (chart audit), score, outcome y dashboard
- Sidebar.tsx
- _FakeSession
- AEGIS — M04 UCCA: Auditoría por expediente (chart audit)
- test_audit.py
- fastapi
- test_ucca_cycles.py

## God Nodes (most connected - your core abstractions)
1. `FakeSession` - 69 edges
2. `make_client()` - 66 edges
3. `CurrentUser` - 46 edges
4. `User` - 39 edges
5. `Base` - 32 edges
6. `brandTokens` - 31 edges
7. `react-i18next` - 29 edges
8. `ChartAudit` - 27 edges
9. `react` - 25 edges
10. `AuditCycle` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Global Constraints` --references--> `domain_errors()`  [INFERRED]
  docs/superpowers/plans/2026-10-12-ucca-chart-audit.md → backend/app/core/master_data.py
- `Task 10: Seed demo, documentación y grafo` --references--> `_seed_sample_cycle()`  [INFERRED]
  docs/superpowers/plans/2026-10-12-ucca-chart-audit.md → backend/app/scripts/seed_demo_data.py
- `Task 3: Schemas, servicio y API de auditorías por expediente` --references--> `record_event()`  [INFERRED]
  docs/superpowers/plans/2026-10-12-ucca-chart-audit.md → backend/app/core/audit.py
- `4. API (`/ucca`)` --references--> `record_event()`  [INFERRED]
  docs/superpowers/specs/2026-10-12-ucca-chart-audit-design.md → backend/app/core/audit.py
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `set_tenant_context()`  [EXTRACTED]
  README.md → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (61 total, 11 thin omitted)

### Community 0 - "identity/service.py"
Cohesion: 0.05
Nodes (113): downgrade(), upgrade(), record_event(), Base, apply_changes(), create_audited(), get_or_404(), UUID (+105 more)

### Community 1 - "AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico"
Cohesion: 0.17
Nodes (11): 10. Requerimientos no funcionales mínimos, 11. Reglas globales de negocio, 12. Criterios de aceptación de la primera entrega, 14. Decisiones pendientes para diseño detallado, 15. Trazabilidad con las fuentes revisadas, 16. Resultado esperado, 1. Propósito del documento, 2. Visión funcional (+3 more)

### Community 2 - "deps.py"
Cohesion: 0.11
Nodes (27): get_settings(), Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca…, Settings, Fija el contexto que consumen las políticas RLS definidas en las migraciones., set_tenant_context(), _dev_bypass_user(), get_current_user(), Dependencias comunes de FastAPI: sesión de base de datos con contexto de tenant… (+19 more)

### Community 3 - "ucca/service.py"
Cohesion: 0.06
Nodes (91): CorrectiveAction, AuditCycle, AuditResult, ChartAudit, Finding, M04 — UCCA, implementado como el módulo de referencia completo. Muestra el…, Respuesta a UN criterio dentro de una auditoría por expediente (celda CCA…CMC…, Hallazgo principal (Key Finding) de una auditoría por expediente, o de un… (+83 more)

### Community 4 - "database.py"
Cohesion: 0.17
Nodes (8): downgrade(), upgrade(), Sesión de base de datos + soporte de Row-Level Security multi-centro. Decisión…, M06 — stub. Muestra cómo un SEGUNDO módulo consume hallazgos de UCCA sin…, collections_abc, logging_config, sqlalchemy, sqlalchemy_orm

### Community 5 - "AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico"
Cohesion: 0.07
Nodes (27): 10. Reportería y Publisher Engine (M09), 11. Integraciones (sección 9.4 del requerimiento), 12. Notificaciones y trabajos programados (sección 9.2), 13. Seguridad y privacidad, 14. Requerimientos no funcionales — enfoque técnico, 15. Hoja de ruta técnica alineada a las fases funcionales, 16. Riesgos técnicos principales, 17. Decisiones técnicas pendientes de confirmar con eHealth/IT (+19 more)

### Community 6 - "package.json"
Cohesion: 0.06
Nodes (33): dependencies, i18next, i18next-browser-languagedetector, react, react-dom, react-i18next, react-router-dom, devDependencies (+25 more)

### Community 7 - "compilerOptions"
Cohesion: 0.13
Nodes (14): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, resolveJsonModule (+6 more)

### Community 8 - "engine.py"
Cohesion: 0.15
Nodes (18): evaluate(), Motor de reglas desacoplado (sección 8 de la arquitectura técnica). UCCA,…, Contexto mínimo común. Cada ruleset puede leer campos adicionales de `extra`., register_ruleset(), RuleContext, Ruleset, RuleVerdict, Omh001Ruleset (+10 more)

### Community 9 - "7. Módulos funcionales"
Cohesion: 0.10
Nodes (20): 7. Módulos funcionales, M01. Gestión de Usuarios, Organización y Accesos, M02. Registro de Profesionales y Datos Maestros, M03. Registro de Gobierno Clínico, M04. Universal Clinical Competency Audit (UCCA), M05. Monitoreo de Medicación Psicotrópica y JAWDA, M06. Gestión de Acciones Correctivas, M07. Auditoría de Cumplimiento de Guías de Práctica Clínica (CPG) (+12 more)

### Community 10 - "identity/schemas.py"
Cohesion: 0.11
Nodes (35): create_catalog_value(), create_position(), create_profession(), create_role(), create_user(), login(), post, CatalogValueCreateRequest (+27 more)

### Community 11 - "Global Constraints"
Cohesion: 0.22
Nodes (8): Global Constraints, Repo Reorganization Implementation Plan, Task 1: Root scaffolding — .gitignore, apps/ dir, Task 2: Move backend into `apps/backend`, recreate venv, Task 3: Move frontend into `apps/frontend`, recreate node_modules, Task 4: Move root files (docs, README, docker-compose, env) and fix path references, Task 5: Delete duplicates and obsolete artifacts, Task 6: Rebuild graphify graph, final verification

### Community 12 - "scheduler.py"
Cohesion: 0.24
Nodes (8): apscheduler_schedulers_background, apscheduler_triggers_cron, Configuración del scheduler de trabajos programados (sección 12 de la…, start_scheduler(), Esqueleto del job crítico descrito en la sección 9 de la arquitectura técnica:…, Pendiente de implementación real (M05). Debe: 1. Leer la población clasificada…, run_weekly_antipsychotic_report(), logging

### Community 13 - "AEGIS — Clinical Governance Platform by Alkalma Health"
Cohesion: 0.14
Nodes (13): AEGIS — Clinical Governance Platform by Alkalma Health, Con Docker, Cómo se agrega un módulo nuevo, Cómo se cumplen las decisiones de la arquitectura técnica, Datos de demostración, Desarrollo local, Estructura del repositorio, Modo local sin autenticación (solo desarrollo) (+5 more)

### Community 14 - "Reorganización de repo — AEGIS / clinical-governance"
Cohesion: 0.20
Nodes (8): Cambios de contenido requeridos, Contexto, Estructura final, Flujo de ejecución (alto nivel), Fuera de alcance, Objetivo, Reorganización de repo — AEGIS / clinical-governance, Riesgos / rollback

### Community 15 - "test_identity_me.py"
Cohesion: 0.15
Nodes (9): client(), _fake_db(), _EmptyScalars, _FakeSession, fixture, TestClient, GET /identity/me devuelve el perfil del usuario autenticado (nombre, correo,…, test_me_returns_profile_shape() (+1 more)

### Community 16 - "alembic"
Cohesion: 0.12
Nodes (4): alembic, _enable_rls(), upgrade(), sqlalchemy_dialects_postgresql

### Community 17 - "9. Capacidades transversales"
Cohesion: 0.33
Nodes (6): 9.1 Búsqueda y filtros, 9.2 Notificaciones y tareas, 9.3 Documentos y evidencia, 9.4 Importación, integración y exportación, 9.5 Configuración, 9. Capacidades transversales

### Community 18 - "branding — identidad Alkalma Health"
Cohesion: 0.33
Nodes (5): branding — identidad Alkalma Health, Dónde vive cada cosa, Insumos pendientes (sección 5.2 del funcional), Paleta oficial (jerarquía 50 / 25 / 12.5 / 6.25), Reglas del brandbook aplicadas

### Community 19 - "13. Fases propuestas"
Cohesion: 0.40
Nodes (5): 13. Fases propuestas, Fase 1 — Fundación y operación inicial, Fase 2 — Gobierno clínico complementario, Fase 3 — Desempeño y credenciales, Fase 4 — Ecosistema e inteligencia

### Community 20 - "6. Usuarios, autenticación y control de acceso"
Cohesion: 0.40
Nodes (5): 6.1 Acceso a la plataforma, 6.2 Usuario administrador inicial, 6.3 Roles funcionales iniciales, 6.4 Matriz de acceso de referencia, 6. Usuarios, autenticación y control de acceso

### Community 21 - "8. Flujos funcionales integrados"
Cohesion: 0.50
Nodes (4): 8.1 Flujo general de auditoría, 8.2 Flujo semanal de medicación y JAWDA, 8.3 Flujo de publicación, 8. Flujos funcionales integrados

### Community 23 - "5. Branding y experiencia Alkalma"
Cohesion: 0.67
Nodes (3): 5.1 Requerimientos de marca, 5.2 Insumos pendientes de marca, 5. Branding y experiencia Alkalma

### Community 34 - "MasterDataPage.tsx"
Cohesion: 0.08
Nodes (33): Task 7: Página del ciclo — KPIs + tabla tipo Excel, apiPostJson(), Column, DataTable(), DataTableProps, Drawer(), ColumnSpec, DynamicOptions() (+25 more)

### Community 35 - "UsersPage.tsx"
Cohesion: 0.08
Nodes (23): CheckboxGroup(), CheckboxGroupProps, FormField(), FormFieldProps, Option, DOT, STATUSES, StatusSelect() (+15 more)

### Community 36 - "MasterDataPage"
Cohesion: 0.16
Nodes (12): apiPatchJson(), MasterDataPage(), changeStatus(), emptyValues(), handleSubmit(), openCreate(), openEdit(), payload() (+4 more)

### Community 37 - "UccaCyclePage.tsx"
Cohesion: 0.10
Nodes (36): Self-review del plan (hecho al escribirlo), Task 6: Frontend base — tipos, scoring en cliente, hook `useApiGet`, i18n, rutas, página de ciclos con "Nuevo ciclo", Task 9: Dashboard UCCA (`/ucca/dashboard`), DrawerProps, StatusBadge(), Tone, toneFor(), TONES (+28 more)

### Community 38 - "CurrentUser"
Cohesion: 0.26
Nodes (25): CurrentUser, domain_errors(), Envuelve la llamada al servicio traduciendo excepciones de dominio a HTTP., Chequeo defensivo a nivel de aplicación; la RLS de base de datos es la barrera…, require_facility_access(), approve_chart_audit(), create_chart_audit(), create_criterion() (+17 more)

### Community 39 - "test_criteria.py"
Cohesion: 0.21
Nodes (13): _audit_events(), _cleanup(), _criterion(), fixture, Criterios de evaluación (UCCA): listar, crear, editar y activar/inactivar desde…, test_create_criterion_duplicate_code_is_409(), test_create_criterion_links_current_version_and_audits(), test_create_criterion_without_template_version_is_422() (+5 more)

### Community 40 - "make_client"
Cohesion: 0.23
Nodes (13): make_client(), TestClient con AUTH_DISABLED y el usuario dev fijo con los permisos dados., _audit_actions(), CRUD de datos maestros M02 (cargos, centros, profesiones, catálogos): crear,…, test_create_catalog_value_and_conflict(), test_create_facility_with_director(), test_create_position(), test_create_position_duplicate_title() (+5 more)

### Community 41 - "App.tsx"
Cohesion: 0.11
Nodes (17): AUTH_DISABLED, login(), LoginPage(), handleSubmit(), LanguageToggle(), AppShell(), CriteriaPage(), Criterion (+9 more)

### Community 42 - "FakeSession"
Cohesion: 0.17
Nodes (8): FakeSession, `scalar_results` se consume en orden (uno por llamada a .scalar()); cuando se…, Ciclos UCCA: creación por centro + año + trimestre, etiqueta derivada,…, test_create_cycle_derives_period_label(), test_create_cycle_invalid_quarter_422(), test_create_cycle_without_template_422(), test_list_cycles_enriched(), _version()

### Community 43 - "ChartAuditPage.tsx"
Cohesion: 0.13
Nodes (24): ApiError, apiFetch(), apiFetchJson(), authorizedFetch(), LoginResponse, App(), AuthContext, AuthContextValue (+16 more)

### Community 44 - "AEGIS Phase 1 — Module 1: User, Organization & Access Management"
Cohesion: 0.14
Nodes (13): 10. Future Expansion, 1. Purpose, 2. Business Process, 3. Database Tables, 4. Field Definitions, 5. Relationships, 6. Business Rules, 7. Workflow (+5 more)

### Community 45 - "test_users_update.py"
Cohesion: 0.21
Nodes (10): Audit ledger inmutable (M10 — sección 7 de la arquitectura técnica).…, _cleanup(), fixture, PATCH /identity/users/{id}: edición parcial con reemplazo de centros/roles y…, test_status_enum(), test_status_invalid_value(), test_update_unknown_user_404(), test_update_user_fields_and_roles() (+2 more)

### Community 46 - "ucca/schemas.py"
Cohesion: 0.11
Nodes (27): AnswerIn, AnswerOut, AuditCriterionCreateRequest, AuditCriterionUpdateRequest, AuditCycleCreateRequest, AuditCycleOut, ChartAuditRowOut, CorrectiveActionIn (+19 more)

### Community 47 - "test_roles.py"
Cohesion: 0.31
Nodes (8): _cleanup(), fixture, Roles + matriz rol→permiso (M01 doc, tablas 5/6/8): editar un rol reemplaza sus…, _role(), test_list_permissions_grouped_by_module(), test_system_administrator_keeps_all_permissions(), test_unknown_permission_id_rejected(), test_update_role_replaces_permissions_and_audits()

### Community 48 - "cleanup"
Cohesion: 0.10
Nodes (24): verify_password(), authenticate(), cleanup(), _cleanup(), fixture, parametrize, Smoke: todos los listados de identity responden 200 con sesión vacía. Protege…, test_list_endpoints_respond() (+16 more)

### Community 49 - "types.ts"
Cohesion: 0.10
Nodes (23): Task 8: Formulario "Auditar expediente" — tarjetas por criterio, barra en vivo, hallazgo y acción correctiva, AnswerSelector(), VALUES, AnswerState, CriterionCard(), EMPTY_FINDING, FindingSection(), FindingState (+15 more)

### Community 50 - "test_users_status.py"
Cohesion: 0.31
Nodes (8): _cleanup(), fixture, UUID, PATCH /identity/users/{id}/status activa / inactiva / suspende una cuenta (M01:…, test_cannot_deactivate_self(), test_deactivate_user(), test_unknown_user_404(), _user()

### Community 51 - "identity/router.py"
Cohesion: 0.16
Nodes (25): create_facility(), list_catalogs(), list_facilities(), list_permissions(), list_positions(), list_professionals(), list_professions(), list_roles() (+17 more)

### Community 52 - "_fakes.py"
Cohesion: 0.17
Nodes (4): Dobles mínimos de sesión SQLAlchemy para probar routers sin Postgres., Las sentencias `text()` (SET LOCAL de RLS, INSERT del audit ledger) no consumen…, Rows, Scalars

### Community 53 - "test_ucca_chart_audits.py"
Cohesion: 0.28
Nodes (23): _answers(), _create_session(), _criteria(), _cycle(), _events(), _existing_audit(), _existing_results(), _payload() (+15 more)

### Community 54 - "UCCA — Auditoría por expediente (chart audit), score, outcome y dashboard"
Cohesion: 0.12
Nodes (15): 1. Objetivo, 3.1 Tablas, 3.2 Cálculo (función pura en `ucca/scoring.py`), 3.3 Permisos, 3. Modelo de datos (migración `0007_ucca_chart_audits`), 5.1 `/ucca` — Ciclos, 5.2 `/ucca/cycles/:cycleId` — Página del ciclo, 5.3 `/ucca/cycles/:cycleId/audits/new` y `/ucca/audits/:auditId` — Auditar expediente (+7 more)

### Community 55 - "Sidebar.tsx"
Cohesion: 0.30
Nodes (9): NAV_GROUPS, NavGroup, NavItem, groupContains(), initialOpen(), itemMatches(), linkStyle(), persist() (+1 more)

### Community 56 - "_FakeSession"
Cohesion: 0.25
Nodes (5): client(), _fake_db(), _FakeSession, fixture, Sesión mínima: el bypass de desarrollo consulta el admin (None -> usuario dev)…

### Community 57 - "AEGIS — M04 UCCA: Auditoría por expediente (chart audit)"
Cohesion: 0.25
Nodes (7): AEGIS — M04 UCCA: Auditoría por expediente (chart audit), API, Estado de implementación, Flujo del director médico, Mapa Excel → AEGIS, Objetivo, Reglas de evaluación (fórmulas)

### Community 58 - "test_audit.py"
Cohesion: 0.38
Nodes (4): _CapturingSession, record_event debe serializar previous/new_values a JSON antes del bind: la…, test_record_event_keeps_null_values(), test_record_event_serializes_json_values()

### Community 59 - "fastapi"
Cohesion: 0.40
Nodes (4): Punto único de registro de routers. Al agregar un módulo nuevo, se agrega su…, health(), get, fastapi

### Community 60 - "test_ucca_cycles.py"
Cohesion: 0.40
Nodes (4): get_db(), TestClient, Prueba de regresión: GET /ucca/cycles debe existir y responder 200 con auth…, test_list_cycles_without_token()

## Knowledge Gaps
- **224 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+219 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 431 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Self-review del plan (hecho al escribirlo)` connect `UccaCyclePage.tsx` to `ucca/service.py`, `FakeSession`, `ChartAuditPage.tsx`, `ucca/schemas.py`, `types.ts`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `FakeSession` connect `FakeSession` to `identity/service.py`, `ucca/service.py`, `UccaCyclePage.tsx`, `test_criteria.py`, `make_client`, `test_users_update.py`, `Reorganización de repo — AEGIS / clinical-governance`, `test_roles.py`, `cleanup`, `ucca/schemas.py`, `test_users_status.py`, `_fakes.py`, `test_ucca_chart_audits.py`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `Estado de implementación en el arquetipo (2026-09-24)` connect `AEGIS Phase 1 — Module 1: User, Organization & Access Management` to `identity/service.py`, `MasterDataPage`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `FakeSession` (e.g. with `test_list_endpoints_respond()` and `Self-review del plan (hecho al escribirlo)`) actually correct?**
  _`FakeSession` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `CurrentUser` (e.g. with `require_facility_access()` and `require_permission()`) actually correct?**
  _`CurrentUser` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `User` (e.g. with `_dev_bypass_user()` and `chart_audit_detail()`) actually correct?**
  _`User` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Base` (e.g. with `downgrade()` and `upgrade()`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._