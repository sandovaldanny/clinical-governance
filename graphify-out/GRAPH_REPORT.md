# Graph Report - clinical-governance  (2026-10-12)

## Corpus Check
- 107 files · ~42,049 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: .example 3, (none) 3, .ini 1)

## Summary
- 849 nodes · 1955 edges · 51 communities (39 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 138 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `20c52eec`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- identity/service.py
- AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico
- deps.py
- useApiList
- ucca/service.py
- AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico
- package.json
- compilerOptions
- engine.py
- 7. Módulos funcionales
- identity/router.py
- Global Constraints
- scheduler.py
- AEGIS — Clinical Governance Platform by Alkalma Health
- Reorganización de repo — AEGIS / clinical-governance
- test_identity_me.py
- 0003_rls_policies.py
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
- brand-tokens.ts
- ucca/router.py
- test_criteria.py
- make_client
- App.tsx
- FakeSession
- useAuth
- AEGIS Phase 1 — Module 1: User, Organization & Access Management
- cleanup
- UccaEvaluatePage.tsx
- test_roles.py
- test_users_create.py
- test_users_status.py
- _fakes.py

## God Nodes (most connected - your core abstractions)
1. `FakeSession` - 52 edges
2. `make_client()` - 44 edges
3. `CurrentUser` - 41 edges
4. `User` - 33 edges
5. `Base` - 31 edges
6. `brandTokens` - 21 edges
7. `MasterDataPage()` - 20 edges
8. `7. Módulos funcionales` - 20 edges
9. `get_settings()` - 19 edges
10. `AegisRole` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Estado de implementación en el arquetipo (2026-09-24)` --references--> `MasterDataPage()`  [INFERRED]
  docs/AEGIS_M01_User_Organization_Access.md → frontend/src/components/MasterDataPage.tsx
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `set_tenant_context()`  [EXTRACTED]
  README.md → backend/app/core/database.py
- `Estado de implementación en el arquetipo (2026-09-24)` --references--> `_validate_user_rules()`  [EXTRACTED]
  docs/AEGIS_M01_User_Organization_Access.md → backend/app/domains/identity/service.py
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `record_result()`  [EXTRACTED]
  README.md → backend/app/domains/governance/ucca/service.py
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `approve_result()`  [EXTRACTED]
  README.md → backend/app/domains/governance/ucca/service.py

## Import Cycles
- None detected.

## Communities (51 total, 12 thin omitted)

### Community 0 - "identity/service.py"
Cohesion: 0.07
Nodes (89): hash_password(), AegisRole, CatalogValue, Facility, OrganizationalPosition, Permission, Profession, Professional (+81 more)

### Community 1 - "AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico"
Cohesion: 0.17
Nodes (11): 10. Requerimientos no funcionales mínimos, 11. Reglas globales de negocio, 12. Criterios de aceptación de la primera entrega, 14. Decisiones pendientes para diseño detallado, 15. Trazabilidad con las fuentes revisadas, 16. Resultado esperado, 1. Propósito del documento, 2. Visión funcional (+3 more)

### Community 2 - "deps.py"
Cohesion: 0.09
Nodes (31): Punto único de registro de routers. Al agregar un módulo nuevo, se agrega su…, get_settings(), Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca…, Settings, Fija el contexto que consumen las políticas RLS definidas en las migraciones., set_tenant_context(), _dev_bypass_user(), get_current_user() (+23 more)

### Community 3 - "useApiList"
Cohesion: 0.16
Nodes (13): Column, DataTable(), DataTableProps, DynamicOptions(), PageHeader(), PageHeaderProps, useApiList(), Catalog (+5 more)

### Community 4 - "ucca/service.py"
Cohesion: 0.05
Nodes (57): alembic, downgrade(), upgrade(), downgrade(), upgrade(), Audit ledger inmutable (M10 — sección 7 de la arquitectura técnica).…, record_event(), Base (+49 more)

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

### Community 10 - "identity/router.py"
Cohesion: 0.09
Nodes (62): CurrentUser, create_access_token(), create_catalog_value(), create_facility(), create_position(), create_profession(), create_role(), create_user() (+54 more)

### Community 11 - "Global Constraints"
Cohesion: 0.22
Nodes (8): Global Constraints, Repo Reorganization Implementation Plan, Task 1: Root scaffolding — .gitignore, apps/ dir, Task 2: Move backend into `apps/backend`, recreate venv, Task 3: Move frontend into `apps/frontend`, recreate node_modules, Task 4: Move root files (docs, README, docker-compose, env) and fix path references, Task 5: Delete duplicates and obsolete artifacts, Task 6: Rebuild graphify graph, final verification

### Community 12 - "scheduler.py"
Cohesion: 0.24
Nodes (8): apscheduler_schedulers_background, apscheduler_triggers_cron, Configuración del scheduler de trabajos programados (sección 12 de la…, start_scheduler(), Esqueleto del job crítico descrito en la sección 9 de la arquitectura técnica:…, Pendiente de implementación real (M05). Debe: 1. Leer la población clasificada…, run_weekly_antipsychotic_report(), logging

### Community 13 - "AEGIS — Clinical Governance Platform by Alkalma Health"
Cohesion: 0.17
Nodes (11): AEGIS — Clinical Governance Platform by Alkalma Health, Con Docker, Cómo se agrega un módulo nuevo, Datos de demostración, Desarrollo local, Estructura del repositorio, Modo local sin autenticación (solo desarrollo), Módulo administrativo (M01/M02) (+3 more)

### Community 14 - "Reorganización de repo — AEGIS / clinical-governance"
Cohesion: 0.20
Nodes (8): Cambios de contenido requeridos, Contexto, Estructura final, Flujo de ejecución (alto nivel), Fuera de alcance, Objetivo, Reorganización de repo — AEGIS / clinical-governance, Riesgos / rollback

### Community 15 - "test_identity_me.py"
Cohesion: 0.08
Nodes (18): get_db(), client(), _fake_db(), _EmptyScalars, _FakeSession, fixture, TestClient, GET /identity/me devuelve el perfil del usuario autenticado (nombre, correo,… (+10 more)

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
Cohesion: 0.10
Nodes (21): Drawer(), CheckboxGroup(), CheckboxGroupProps, FormField(), FormFieldProps, Option, ColumnSpec, FieldOption (+13 more)

### Community 35 - "UsersPage.tsx"
Cohesion: 0.10
Nodes (18): DOT, STATUSES, StatusSelect(), StatusSelectProps, UserStatus, TempPasswordCallout(), EMPTY_FORM, formFromUser() (+10 more)

### Community 36 - "MasterDataPage"
Cohesion: 0.16
Nodes (12): apiPatchJson(), MasterDataPage(), changeStatus(), emptyValues(), handleSubmit(), openCreate(), openEdit(), payload() (+4 more)

### Community 37 - "brand-tokens.ts"
Cohesion: 0.15
Nodes (16): login(), LoginPage(), handleSubmit(), DrawerProps, LanguageToggle(), StatusBadge(), Tone, toneFor() (+8 more)

### Community 38 - "ucca/router.py"
Cohesion: 0.14
Nodes (29): domain_errors(), Envuelve la llamada al servicio traduciendo excepciones de dominio a HTTP., Chequeo defensivo a nivel de aplicación; la RLS de base de datos es la barrera…, require_facility_access(), approve_result(), create_criterion(), create_cycle(), list_criteria() (+21 more)

### Community 39 - "test_criteria.py"
Cohesion: 0.26
Nodes (11): _audit_events(), _criterion(), Criterios de evaluación (UCCA): listar, crear, editar y activar/inactivar desde…, test_create_criterion_duplicate_code_is_409(), test_create_criterion_links_current_version_and_audits(), test_create_criterion_without_template_version_is_422(), test_list_criteria_exposes_five_fields_and_status(), test_list_criteria_only_active_filter() (+3 more)

### Community 40 - "make_client"
Cohesion: 0.23
Nodes (13): make_client(), TestClient con AUTH_DISABLED y el usuario dev fijo con los permisos dados., _audit_actions(), CRUD de datos maestros M02 (cargos, centros, profesiones, catálogos): crear,…, test_create_catalog_value_and_conflict(), test_create_facility_with_director(), test_create_position(), test_create_position_duplicate_title() (+5 more)

### Community 41 - "App.tsx"
Cohesion: 0.13
Nodes (14): App(), AppShell(), CriteriaPage(), Criterion, FacilitiesPage(), Facility, Position, PositionsPage() (+6 more)

### Community 42 - "FakeSession"
Cohesion: 0.18
Nodes (8): FakeSession, `scalar_results` se consume en orden (uno por llamada a .scalar()); cuando se…, PATCH /identity/users/{id}: edición parcial con reemplazo de centros/roles y…, test_status_enum(), test_status_invalid_value(), test_update_unknown_user_404(), test_update_user_fields_and_roles(), _user()

### Community 43 - "useAuth"
Cohesion: 0.21
Nodes (10): AuthContext, AuthContextValue, AuthProvider(), Session, useAuth(), initialsOf(), ProfileMenu(), useCanManage() (+2 more)

### Community 44 - "AEGIS Phase 1 — Module 1: User, Organization & Access Management"
Cohesion: 0.14
Nodes (13): 10. Future Expansion, 1. Purpose, 2. Business Process, 3. Database Tables, 4. Field Definitions, 5. Relationships, 6. Business Rules, 7. Workflow (+5 more)

### Community 45 - "cleanup"
Cohesion: 0.15
Nodes (13): cleanup(), _cleanup(), fixture, _cleanup(), fixture, Smoke: todos los listados de identity responden 200 con sesión vacía. Protege…, test_list_endpoints_respond(), _cleanup() (+5 more)

### Community 46 - "UccaEvaluatePage.tsx"
Cohesion: 0.15
Nodes (17): ApiError, apiFetch(), apiFetchJson(), apiPostJson(), AUTH_DISABLED, authorizedFetch(), LoginResponse, Criterion (+9 more)

### Community 47 - "test_roles.py"
Cohesion: 0.21
Nodes (11): _cleanup(), fixture, Roles + matriz rol→permiso (M01 doc, tablas 5/6/8): editar un rol reemplaza sus…, _role(), test_create_role_with_permissions(), test_list_permissions_grouped_by_module(), test_system_administrator_keeps_all_permissions(), test_unknown_permission_id_rejected() (+3 more)

### Community 48 - "test_users_create.py"
Cohesion: 0.27
Nodes (10): verify_password(), authenticate(), _cleanup(), _payload(), fixture, POST /identity/users — flujo del documento M01: identidad → cargo → centro →…, test_clinician_requires_profession(), test_create_user_requires_facility_and_role() (+2 more)

### Community 50 - "test_users_status.py"
Cohesion: 0.31
Nodes (8): _cleanup(), fixture, UUID, PATCH /identity/users/{id}/status activa / inactiva / suspende una cuenta (M01:…, test_cannot_deactivate_self(), test_deactivate_user(), test_unknown_user_404(), _user()

### Community 52 - "_fakes.py"
Cohesion: 0.18
Nodes (3): Dobles mínimos de sesión SQLAlchemy para probar routers sin Postgres., Rows, Scalars

## Knowledge Gaps
- **196 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 370 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Estado de implementación en el arquetipo (2026-09-24)` connect `AEGIS Phase 1 — Module 1: User, Organization & Access Management` to `identity/service.py`, `MasterDataPage`?**
  _High betweenness centrality (0.310) - this node is a cross-community bridge._
- **Why does `_validate_user_rules()` connect `identity/service.py` to `AEGIS Phase 1 — Module 1: User, Organization & Access Management`?**
  _High betweenness centrality (0.305) - this node is a cross-community bridge._
- **Why does `MasterDataPage()` connect `MasterDataPage` to `MasterDataPage.tsx`, `useApiList`, `App.tsx`, `useAuth`, `AEGIS Phase 1 — Module 1: User, Organization & Access Management`, `UccaEvaluatePage.tsx`?**
  _High betweenness centrality (0.296) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `CurrentUser` (e.g. with `require_facility_access()` and `require_permission()`) actually correct?**
  _`CurrentUser` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `User` (e.g. with `_dev_bypass_user()` and `authenticate()`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Base` (e.g. with `downgrade()` and `upgrade()`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _196 weakly-connected nodes found - possible documentation gaps or missing edges._