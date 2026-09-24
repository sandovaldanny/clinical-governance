# Graph Report - aegis-scaffold  (2026-09-09)

## Corpus Check
- 71 files · ~19,862 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 446 nodes · 864 edges · 27 communities (14 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- seed_demo_data.py
- AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico
- CurrentUser
- App.tsx
- ucca/service.py
- AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico
- package.json
- identity/schemas.py
- RuleContext
- 7. Módulos funcionales
- compilerOptions
- scheduler.py
- AEGIS — Arquetipo del sistema
- test_ucca_cycles.py
- 0003_rls_policies.py

## God Nodes (most connected - your core abstractions)
1. `Base` - 31 edges
2. `CurrentUser` - 22 edges
3. `7. Módulos funcionales` - 20 edges
4. `useApiList()` - 19 edges
5. `AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico` - 18 edges
6. `AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico` - 17 edges
7. `get_settings()` - 15 edges
8. `compilerOptions` - 13 edges
9. `_seed_master_data()` - 10 edges
10. `run()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0004_ucca_module.py → backend/app/core/database.py
- `downgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0004_ucca_module.py → backend/app/core/database.py
- `upgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0001_core_master_schema.py → backend/app/core/database.py
- `downgrade()` --uses--> `Base`  [INFERRED]
  backend/alembic/versions/0001_core_master_schema.py → backend/app/core/database.py
- `CorrectiveAction` --inherits--> `Base`  [EXTRACTED]
  backend/app/domains/governance/corrective_actions/models.py → backend/app/core/database.py

## Import Cycles
- None detected.

## Communities (27 total, 1 thin omitted)

### Community 0 - "seed_demo_data.py"
Cohesion: 0.09
Nodes (56): downgrade(), upgrade(), Base, hash_password(), verify_password(), AegisRole, CatalogValue, Facility (+48 more)

### Community 1 - "AEGIS — Requerimiento funcional de la Plataforma de Gobierno Clínico"
Cohesion: 0.06
Nodes (34): 10. Requerimientos no funcionales mínimos, 11. Reglas globales de negocio, 12. Criterios de aceptación de la primera entrega, 13. Fases propuestas, 14. Decisiones pendientes para diseño detallado, 15. Trazabilidad con las fuentes revisadas, 16. Resultado esperado, 1. Propósito del documento (+26 more)

### Community 2 - "CurrentUser"
Cohesion: 0.07
Nodes (47): downgrade(), upgrade(), Punto único de registro de routers. Al agregar un módulo nuevo, se agrega su…, get_settings(), Configuración centralizada. Todo valor de entorno se lee UNA vez aquí, nunca…, Settings, get_db(), Sesión de base de datos + soporte de Row-Level Security multi-centro. Decisión… (+39 more)

### Community 3 - "App.tsx"
Cohesion: 0.08
Nodes (45): ApiError, apiFetch(), apiFetchJson(), AUTH_DISABLED, authorizedFetch(), login(), LoginResponse, App() (+37 more)

### Community 4 - "ucca/service.py"
Cohesion: 0.12
Nodes (27): AuditCycle, Audit ledger inmutable (M10 — sección 7 de la arquitectura técnica).…, record_event(), AuditCriterion, AuditCycle, AuditResult, AuditTemplate, AuditTemplateVersion (+19 more)

### Community 5 - "AEGIS — Arquitectura Técnica de la Plataforma de Gobierno Clínico"
Cohesion: 0.07
Nodes (27): 10. Reportería y Publisher Engine (M09), 11. Integraciones (sección 9.4 del requerimiento), 12. Notificaciones y trabajos programados (sección 9.2), 13. Seguridad y privacidad, 14. Requerimientos no funcionales — enfoque técnico, 15. Hoja de ruta técnica alineada a las fases funcionales, 16. Riesgos técnicos principales, 17. Decisiones técnicas pendientes de confirmar con eHealth/IT (+19 more)

### Community 6 - "package.json"
Cohesion: 0.07
Nodes (26): dependencies, react, react-dom, react-router-dom, devDependencies, @types/react, @types/react-dom, typescript (+18 more)

### Community 7 - "identity/schemas.py"
Cohesion: 0.11
Nodes (30): create_user(), list_catalogs(), list_facilities(), list_professionals(), list_professions(), list_roles(), list_users(), login() (+22 more)

### Community 8 - "RuleContext"
Cohesion: 0.19
Nodes (15): evaluate(), Motor de reglas desacoplado (sección 8 de la arquitectura técnica). UCCA,…, Contexto mínimo común. Cada ruleset puede leer campos adicionales de `extra`., register_ruleset(), RuleContext, Ruleset, RuleVerdict, Omh001Ruleset (+7 more)

### Community 9 - "7. Módulos funcionales"
Cohesion: 0.10
Nodes (20): 7. Módulos funcionales, M01. Gestión de Usuarios, Organización y Accesos, M02. Registro de Profesionales y Datos Maestros, M03. Registro de Gobierno Clínico, M04. Universal Clinical Competency Audit (UCCA), M05. Monitoreo de Medicación Psicotrópica y JAWDA, M06. Gestión de Acciones Correctivas, M07. Auditoría de Cumplimiento de Guías de Práctica Clínica (CPG) (+12 more)

### Community 10 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, resolveJsonModule (+11 more)

### Community 12 - "scheduler.py"
Cohesion: 0.38
Nodes (5): Configuración del scheduler de trabajos programados (sección 12 de la…, start_scheduler(), Esqueleto del job crítico descrito en la sección 9 de la arquitectura técnica:…, Pendiente de implementación real (M05). Debe: 1. Leer la población clasificada…, run_weekly_antipsychotic_report()

### Community 13 - "AEGIS — Arquetipo del sistema"
Cohesion: 0.29
Nodes (6): AEGIS — Arquetipo del sistema, Cómo correr localmente, Cómo se agrega un módulo nuevo, Estructura, Modo local sin autenticación (solo desarrollo), Supuestos de este arquetipo (a validar con el equipo)

### Community 14 - "test_ucca_cycles.py"
Cohesion: 0.40
Nodes (5): client(), fixture, Prueba de regresión: GET /ucca/cycles debe existir y responder con auth…, test_list_cycles_without_token(), TestClient

## Knowledge Gaps
- **123 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+118 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 196 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Base` connect `seed_demo_data.py` to `CurrentUser`, `ucca/service.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `CurrentUser` connect `CurrentUser` to `identity/schemas.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `CurrentUser` to `seed_demo_data.py`, `test_ucca_cycles.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Base` (e.g. with `downgrade()` and `upgrade()`) actually correct?**
  _`Base` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `CurrentUser` (e.g. with `require_facility_access()` and `require_permission()`) actually correct?**
  _`CurrentUser` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _123 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `seed_demo_data.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08514013749338974 - nodes in this community are weakly interconnected._