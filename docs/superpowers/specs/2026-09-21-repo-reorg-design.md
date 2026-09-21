# Reorganización de repo — AEGIS / clinical-governance

## Contexto

`clinical-governance/` no tenía control de versiones. Contenía 3 carpetas sueltas en la raíz:

- `aegis-scaffold/` — la app real (`frontend/`, `backend/`, `docs/`, `docker-compose.yml`, `README.md`, `.env`, `graphify-out/`).
- `documents/` — duplicado byte-a-byte de `aegis-scaffold/docs/` (confirmado con `diff`).
- `Claude outputs/aegis-scaffold.zip` — export del 8-sep-2026, superado por el working tree actual.
- `.playwright-mcp/` — caché de sesiones de prueba con Playwright, regenerable.

No hay referencias de rutas absolutas ni al literal `aegis-scaffold` en ningún archivo de config (`grep -r "aegis-scaffold"` no devolvió resultados fuera de nombres de carpeta), así que mover el contenido es de bajo riesgo salvo por dos archivos que usan rutas relativas al nivel donde viven hoy: `docker-compose.yml` (`build: ./backend`, `./frontend`) y `README.md` (diagrama de estructura).

## Objetivo

Un solo repo git en `clinical-governance/`, con layout de monorepo convencional (`apps/`), marca Alkalma Health sin cambios, sin duplicados ni artefactos obsoletos.

## Estructura final

```
clinical-governance/
├── README.md
├── .gitignore
├── docker-compose.yml
├── .env.example
├── apps/
│   ├── backend/     (ex aegis-scaffold/backend, sin .venv)
│   └── frontend/    (ex aegis-scaffold/frontend, sin node_modules/dist)
├── docs/            (ex aegis-scaffold/docs)
└── graphify-out/    (se reconstruye tras el move — las rutas internas cambian)
```

`documents/`, `Claude outputs/`, `.playwright-mcp/`, `.DS_Store` se eliminan (aprobado por el usuario).

## Cambios de contenido requeridos

1. **`docker-compose.yml`**: `build: ./backend` → `build: ./apps/backend`; `build: ./frontend` → `build: ./apps/frontend`; mismo cambio en los `volumes:` de cada servicio.
2. **`README.md`**: el diagrama de `## Estructura` debe reflejar `apps/backend/` y `apps/frontend/` en vez de `backend/`/`frontend/` al nivel raíz.
3. **`.gitignore` (raíz, fusiona el existente)**: agregar `.DS_Store`, `*.tsbuildinfo`, `graphify-out/cache/`, además de lo ya presente (`__pycache__/`, `*.pyc`, `.env`, `node_modules/`, `dist/`, `.venv/`, `*.egg-info/`, `.pytest_cache/`).
4. **Entornos no portables**: `backend/.venv` y `frontend/node_modules` no se mueven — se recrean después del move (los binarios/activate scripts de un venv tienen rutas absolutas grabadas; moverlo lo rompe). `frontend/dist` tampoco se mueve (build artifact).
5. **`graphify-out/`**: las rutas `source_file` dentro de `graph.json` quedan relativas al viejo root (`backend/...`, `frontend/...`). Tras el move se corre `graphify update .` desde la nueva raíz para reconciliar — se acepta que reporte el corpus como "cambiado" dado el rename de carpeta.

## Flujo de ejecución (alto nivel)

1. `git init` ya hecho en `clinical-governance/` (aprobado).
2. Mover `apps/backend`, `apps/frontend`, `docs/`, `README.md`, `docker-compose.yml`, `.env`, `.env.example` desde `aegis-scaffold/` a la raíz, excluyendo `.venv/`, `node_modules/`, `dist/`, `__pycache__/`, `.pytest_cache/`.
3. Eliminar `documents/`, `Claude outputs/`, `.playwright-mcp/`, `.DS_Store`, la carpeta `aegis-scaffold/` vacía resultante.
4. Editar `docker-compose.yml` y `README.md` según lo descrito arriba; fusionar `.gitignore`.
5. Recrear `apps/backend/.venv` (`python -m venv` + `pip install -r requirements.txt`) y `apps/frontend/node_modules` (`npm install`).
6. `git add` + primer commit.
7. `graphify update .` desde la nueva raíz.
8. Verificación local (arranque de backend + frontend, ver sección de pruebas del README).

## Riesgos / rollback

- Todo el move ocurre dentro de un repo git recién inicializado — si algo queda mal, `git status`/`git diff` antes de cualquier `add` permite revisar, y como es el commit inicial, un `git reset` no destruye historial previo.
- El venv y node_modules se recrean, no se migran — evita el riesgo de binarios rotos por rutas absolutas.

## Fuera de alcance

- Validación de marca Keralty/Alkalma en componentes (tarea separada, no arquitectónica).
- Instrucciones de prueba local detalladas (se entregan después de verificar que el reorg funciona).
