# Graph Report - clinical-governance  (2026-09-24)

## Corpus Check
- 77 files · ~24,427 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: .example 3, (none) 3, .ini 1)

## Summary
- 508 nodes · 1036 edges · 34 communities (23 shown, 11 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 66 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e435297`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- seed_demo_data.py
- AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico
- deps.py
- App.tsx
- ucca/service.py
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
- test_ucca_cycles.py
- env.py
- 9. Capacidades transversales
- branding — identidad Alkalma Health
- 13. Fases propuestas
- 6. Usuarios, autenticación y control de acceso
- 8. Flujos funcionales integrados
- infra/postgres
- 5. Branding y experiencia Alkalma

## God Nodes (most connected - your core abstractions)
1. `Base` - 31 edges
2. `CurrentUser` - 23 edges
3. `useApiList()` - 21 edges
4. `7. Módulos funcionales` - 20 edges
5. `AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico` - 18 edges
6. `get_settings()` - 17 edges
7. `AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico` - 17 edges
8. `User` - 16 edges
9. `compilerOptions` - 13 edges
10. `Facility` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `set_tenant_context()`  [EXTRACTED]
  README.md → backend/app/core/database.py
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `record_result()`  [EXTRACTED]
  README.md → backend/app/domains/governance/ucca/service.py
- `Cómo se cumplen las decisiones de la arquitectura técnica` --references--> `approve_result()`  [EXTRACTED]
  README.md → backend/app/domains/governance/ucca/service.py
- `upgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0004_ucca_module.py → backend/app/core/database.py
- `downgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0004_ucca_module.py → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (34 total, 11 thin omitted)

### Community 0 - "seed_demo_data.py"
Cohesion: 0.09
Nodes (58): downgrade(), upgrade(), Base, hash_password(), verify_password(), AegisRole, CatalogValue, Facility (+50 more)

### Community 1 - "AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico"
Cohesion: 0.17
Nodes (11): 10. Requerimientos no funcionales mínimos, 11. Reglas globales de negocio, 12. Criterios de aceptación de la primera entrega, 14. Decisiones pendientes para diseño detallado, 15. Trazabilidad con las fuentes revisadas, 16. Resultado esperado, 1. Propósito del documento, 2. Visión funcional (+3 more)

### Community 2 - "deps.py"
Cohesion: 0.06
Nodes (65): Punto único de registro de routers. Al agregar un módulo nuevo, se agrega su…, get_settings(), Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca…, Settings, get_db(), Sesión de base de datos + soporte de Row-Level Security multi-centro. Decisión…, Fija el contexto que consumen las políticas RLS definidas en las migraciones., set_tenant_context() (+57 more)

### Community 3 - "App.tsx"
Cohesion: 0.07
Nodes (57): ApiError, apiFetch(), apiFetchJson(), apiPostJson(), AUTH_DISABLED, authorizedFetch(), login(), LoginResponse (+49 more)

### Community 4 - "ucca/service.py"
Cohesion: 0.12
Nodes (29): Audit ledger inmutable (M10 — sección 7 de la arquitectura técnica).…, record_event(), AuditCriterion, AuditCycle, AuditResult, AuditTemplate, AuditTemplateVersion, Finding (+21 more)

### Community 5 - "AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico"
Cohesion: 0.07
Nodes (27): 10. Reportería y Publisher Engine (M09), 11. Integraciones (sección 9.4 del requerimiento), 12. Notificaciones y trabajos programados (sección 9.2), 13. Seguridad y privacidad, 14. Requerimientos no funcionales — enfoque técnico, 15. Hoja de ruta técnica alineada a las fases funcionales, 16. Riesgos técnicos principales, 17. Decisiones técnicas pendientes de confirmar con eHealth/IT (+19 more)

### Community 6 - "package.json"
Cohesion: 0.08
Nodes (24): dependencies, react, react-dom, react-router-dom, devDependencies, @types/react, @types/react-dom, typescript (+16 more)

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
Cohesion: 0.26
Nodes (13): create_user(), login(), post, CatalogValueOut, FacilityOut, LoginRequest, ProfessionalOut, ProfessionOut (+5 more)

### Community 11 - "Global Constraints"
Cohesion: 0.22
Nodes (8): Global Constraints, Repo Reorganization Implementation Plan, Task 1: Root scaffolding — .gitignore, apps/ dir, Task 2: Move backend into `apps/backend`, recreate venv, Task 3: Move frontend into `apps/frontend`, recreate node_modules, Task 4: Move root files (docs, README, docker-compose, env) and fix path references, Task 5: Delete duplicates and obsolete artifacts, Task 6: Rebuild graphify graph, final verification

### Community 12 - "scheduler.py"
Cohesion: 0.24
Nodes (8): apscheduler_schedulers_background, apscheduler_triggers_cron, Configuración del scheduler de trabajos programados (sección 12 de la…, start_scheduler(), Esqueleto del job crítico descrito en la sección 9 de la arquitectura técnica:…, Pendiente de implementación real (M05). Debe: 1. Leer la población clasificada…, run_weekly_antipsychotic_report(), logging

### Community 13 - "AEGIS — Clinical Governance Platform by Alkalma Health"
Cohesion: 0.18
Nodes (10): AEGIS — Clinical Governance Platform by Alkalma Health, Con Docker, Cómo se agrega un módulo nuevo, Datos de demostración, Desarrollo local, Estructura del repositorio, Modo local sin autenticación (solo desarrollo), Pruebas y build (+2 more)

### Community 14 - "Reorganización de repo — AEGIS / clinical-governance"
Cohesion: 0.22
Nodes (8): Cambios de contenido requeridos, Contexto, Estructura final, Flujo de ejecución (alto nivel), Fuera de alcance, Objetivo, Reorganización de repo — AEGIS / clinical-governance, Riesgos / rollback

### Community 15 - "test_ucca_cycles.py"
Cohesion: 0.15
Nodes (10): client(), _fake_db(), _FakeSession, fixture, Prueba de regresión: GET /ucca/cycles debe existir y responder 200 con auth…, Sesión mínima: el bypass de desarrollo consulta el admin (None -> usuario dev)…, test_list_cycles_without_token(), fastapi_testclient (+2 more)

### Community 16 - "env.py"
Cohesion: 0.11
Nodes (9): alembic, _enable_rls(), upgrade(), downgrade(), upgrade(), CorrectiveAction, M06 — stub. Muestra cómo un SEGUNDO módulo consume hallazgos de UCCA sin…, logging_config (+1 more)

### Community 17 - "9. Capacidades transversales"
Cohesion: 0.33
Nodes (6): 9.1 Búsqueda y filtros, 9.2 Notificaciones y tareas, 9.3 Documentos y evidencia, 9.4 Importación, integración y exportación, 9.5 Configuración, 9. Capacidades transversales

### Community 18 - "branding — identidad Alkalma Health"
Cohesion: 0.40
Nodes (4): branding — identidad Alkalma Health, Dónde vive cada cosa, Insumos pendientes (sección 5.2 del funcional), Tokens vigentes (placeholder)

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

## Knowledge Gaps
- **151 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 241 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cómo se cumplen las decisiones de la arquitectura técnica` connect `ucca/service.py` to `deps.py`, `AEGIS — Clinical Governance Platform by Alkalma Health`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `deps.py` to `env.py`, `seed_demo_data.py`, `test_ucca_cycles.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `AEGIS — Clinical Governance Platform by Alkalma Health` connect `AEGIS — Clinical Governance Platform by Alkalma Health` to `ucca/service.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Base` (e.g. with `downgrade()` and `upgrade()`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `CurrentUser` (e.g. with `require_facility_access()` and `require_permission()`) actually correct?**
  _`CurrentUser` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _151 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `seed_demo_data.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08978174603174603 - nodes in this community are weakly interconnected._