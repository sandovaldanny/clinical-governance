# Repo Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `clinical-governance/` into a single, git-tracked monorepo with `apps/backend`, `apps/frontend`, root `docs/`, and no duplicate/obsolete artifacts.

**Architecture:** Pure file/directory reorganization plus two config edits (`docker-compose.yml`, `README.md`). No application code changes. Build artifacts (`.venv`, `node_modules`, `dist`) are excluded from the move and recreated fresh at the new location, since venv activation scripts bake in absolute paths that break when the directory moves.

**Tech Stack:** git, bash, Python 3.12 venv, npm/Vite, docker compose (config validation only, not run).

**Spec:** `docs/superpowers/specs/2026-09-21-repo-reorg-design.md`

## Global Constraints

- Brand stays Alkalma Health — no branding changes in this plan.
- `git` repo already initialized at `clinical-governance/` root with one commit (the spec). Every task below ends with its own commit — never amend that first commit.
- Never `rm -rf` anything not explicitly listed as "delete" in a task below.
- `.venv/`, `node_modules/`, `dist/`, `__pycache__/`, `.pytest_cache/` are never `git mv`'d — they are gitignored and get excluded from every move command.

---

### Task 1: Root scaffolding — .gitignore, apps/ dir

**Files:**
- Create: `clinical-governance/.gitignore`
- Create dir: `clinical-governance/apps/`

**Interfaces:**
- Produces: root `.gitignore` that Task 2–4 rely on being in place before any `git add`.

- [ ] **Step 1: Create `apps/` directory**

```bash
cd <repo>
mkdir -p apps
```

- [ ] **Step 2: Write root `.gitignore`**

Merge of the existing `aegis-scaffold/.gitignore` plus the additions called out in the spec (`.DS_Store`, `*.tsbuildinfo`, `graphify-out/cache/`):

```
__pycache__/
*.pyc
.env
node_modules/
dist/
.venv/
*.egg-info/
.pytest_cache/
.DS_Store
*.tsbuildinfo
graphify-out/cache/
```

- [ ] **Step 3: Verify**

```bash
test -d apps && test -f .gitignore && echo OK
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: add root .gitignore and apps/ scaffolding"
```

---

### Task 2: Move backend into `apps/backend`, recreate venv

**Files:**
- Move: `aegis-scaffold/backend/**` (excl. `.venv/`, `__pycache__/`, `.pytest_cache/`) → `apps/backend/`
- Create: `apps/backend/.venv/` (recreated, not moved)

**Interfaces:**
- Consumes: `apps/` dir from Task 1.
- Produces: `apps/backend/` importable as `app.main` with a working venv, for Task 6's final verification.

- [ ] **Step 1: Move tracked backend content, leaving build artifacts behind**

```bash
cd <repo>
rsync -a --exclude='.venv/' --exclude='__pycache__/' --exclude='.pytest_cache/' \
  aegis-scaffold/backend/ apps/backend/
```

- [ ] **Step 2: Verify no build artifacts were copied**

```bash
test ! -d apps/backend/.venv && test ! -d apps/backend/.pytest_cache && echo OK
```
Expected: `OK`

- [ ] **Step 3: Recreate the venv at the new location**

```bash
cd apps/backend
python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt
```

- [ ] **Step 4: Verify the app imports cleanly from the new path**

```bash
cd <repo>/apps/backend
./.venv/bin/python -c "from app.main import app; print('OK')"
```
Expected: `OK` (no `ModuleNotFoundError`, no import-time exceptions)

- [ ] **Step 5: Stage and commit**

```bash
cd <repo>
git add apps/backend
git commit -m "refactor: move backend into apps/backend"
```

---

### Task 3: Move frontend into `apps/frontend`, recreate node_modules

**Files:**
- Move: `aegis-scaffold/frontend/**` (excl. `node_modules/`, `dist/`) → `apps/frontend/`
- Create: `apps/frontend/node_modules/` (recreated, not moved)

**Interfaces:**
- Consumes: `apps/` dir from Task 1.
- Produces: `apps/frontend/` buildable with `npm run build`, for Task 6's final verification.

- [ ] **Step 1: Move tracked frontend content, leaving build artifacts behind**

```bash
cd <repo>
rsync -a --exclude='node_modules/' --exclude='dist/' \
  aegis-scaffold/frontend/ apps/frontend/
```

- [ ] **Step 2: Verify no build artifacts were copied**

```bash
test ! -d apps/frontend/node_modules && test ! -d apps/frontend/dist && echo OK
```
Expected: `OK`

- [ ] **Step 3: Reinstall dependencies at the new location**

```bash
cd apps/frontend
npm install --silent
```

- [ ] **Step 4: Verify the build succeeds from the new path**

```bash
cd <repo>/apps/frontend
npm run build
```
Expected: exits 0, produces `dist/`

- [ ] **Step 5: Stage and commit**

```bash
cd <repo>
git add apps/frontend
git commit -m "refactor: move frontend into apps/frontend"
```

---

### Task 4: Move root files (docs, README, docker-compose, env) and fix path references

**Files:**
- Move: `aegis-scaffold/docs/` → `docs/` (merge into existing `docs/superpowers/` dir from the spec/plan)
- Move: `aegis-scaffold/README.md` → `README.md`
- Move: `aegis-scaffold/docker-compose.yml` → `docker-compose.yml`
- Move: `aegis-scaffold/.env` → `.env`
- Move: `aegis-scaffold/.env.example` → `.env.example`
- Modify: `docker-compose.yml` (build/volume paths)
- Modify: `README.md` (`## Estructura` diagram)

**Interfaces:**
- Consumes: `apps/backend`, `apps/frontend` from Tasks 2–3 (paths referenced in `docker-compose.yml`).

- [ ] **Step 1: Move docs and root files**

```bash
cd <repo>
mkdir -p docs
rsync -a aegis-scaffold/docs/ docs/
mv aegis-scaffold/README.md ./README.md
mv aegis-scaffold/docker-compose.yml ./docker-compose.yml
mv aegis-scaffold/.env ./.env
mv aegis-scaffold/.env.example ./.env.example
```

- [ ] **Step 2: Verify the two source docs landed alongside the spec/plan dirs**

```bash
ls docs/
```
Expected: `AEGIS_Arquitectura_Tecnica.md  AEGIS_Requerimiento_Funcional_Alkalma.md  superpowers/`

- [ ] **Step 3: Edit `docker-compose.yml` — update backend service**

Change:
```yaml
  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    depends_on:
      - db
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
```
To:
```yaml
  backend:
    build: ./apps/backend
    restart: unless-stopped
    env_file: .env
    depends_on:
      - db
    ports:
      - "8000:8000"
    volumes:
      - ./apps/backend:/app
```

- [ ] **Step 4: Edit `docker-compose.yml` — update frontend service**

Change:
```yaml
  frontend:
    build: ./frontend
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
```
To:
```yaml
  frontend:
    build: ./apps/frontend
    restart: unless-stopped
    depends_on:
      - backend
    ports:
      - "5173:5173"
    volumes:
      - ./apps/frontend:/app
      - /app/node_modules
```

- [ ] **Step 5: Verify docker-compose.yml is valid**

```bash
docker compose config --quiet && echo OK
```
Expected: `OK` (no parse errors; skip this check if Docker Desktop isn't running — note that in the final report instead of blocking)

- [ ] **Step 6: Edit `README.md` — update the `## Estructura` code block**

Replace the existing block that starts with:
```
backend/
  app/
```
and
```
frontend/
  src/
```
so both are nested one level under `apps/`:
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

- [ ] **Step 7: Grep-check for any remaining bare `backend/` or `frontend/` path references in README**

```bash
grep -n '`backend/\|`frontend/\|cd backend\|cd frontend' README.md
```
Expected: any matches use `apps/backend` / `apps/frontend` (fix any that don't — e.g. "Cómo correr localmente" section likely has `cd backend`, `cd frontend` commands to update to `cd apps/backend`, `cd apps/frontend`)

- [ ] **Step 8: Stage and commit**

```bash
cd <repo>
git add docs README.md docker-compose.yml .env.example
git commit -m "refactor: move docs/README/docker-compose to root, fix apps/ paths"
```

Note: `.env` is gitignored by design (secrets) — it will show as untracked, not staged. That's correct.

---

### Task 5: Delete duplicates and obsolete artifacts

**Files:**
- Delete: `documents/` (root-level, byte-identical duplicate of `docs/`)
- Delete: `Claude outputs/` (stale zip export)
- Delete: `.playwright-mcp/` (regenerable test cache)
- Delete: `.DS_Store`
- Delete: `aegis-scaffold/` (now empty except leftover build artifacts)

**Interfaces:**
- Consumes: nothing new — this only runs after Tasks 2–4 have copied everything needed out of `aegis-scaffold/`.

- [ ] **Step 1: Confirm `aegis-scaffold/` has nothing left except gitignored build artifacts**

```bash
cd <repo>
find aegis-scaffold -type f | grep -v -E '\.venv/|node_modules/|__pycache__/|\.pytest_cache/|/dist/'
```
Expected: empty output (if anything else prints, STOP — it means a file wasn't moved in Tasks 2–4, go back and move it before deleting)

- [ ] **Step 2: Delete the confirmed-obsolete directories/files**

```bash
rm -rf documents "Claude outputs" .playwright-mcp aegis-scaffold .DS_Store
```

- [ ] **Step 3: Verify root listing matches the target structure**

```bash
ls -la
```
Expected: only `.git`, `.gitignore`, `.env` (untracked), `.env.example`, `README.md`, `docker-compose.yml`, `apps/`, `docs/`, `graphify-out/`

- [ ] **Step 4: Commit the deletions**

```bash
git add -A
git status
git commit -m "chore: remove duplicate docs/ and obsolete build artifacts"
```

---

### Task 6: Rebuild graphify graph, final verification

**Files:**
- Modify: `graphify-out/graph.json`, `graphify-out/GRAPH_REPORT.md` (regenerated, not hand-edited)

**Interfaces:**
- Consumes: `apps/backend`, `apps/frontend` (final paths) from Tasks 2–4.

- [ ] **Step 1: Re-run graphify from the new root (paths inside the graph changed with the rename)**

```bash
cd <repo>
graphify update . --force
```
Expected: completes, reports updated node/edge counts reflecting `apps/backend`/`apps/frontend` paths

- [ ] **Step 2: Final backend smoke check**

```bash
cd apps/backend
./.venv/bin/python -c "from app.main import app; print('backend import OK')"
```
Expected: `backend import OK`

- [ ] **Step 3: Final frontend smoke check**

```bash
cd <repo>/apps/frontend
test -d dist && echo "frontend build OK"
```
Expected: `frontend build OK` (from Task 3's build; rerun `npm run build` if `dist/` is missing)

- [ ] **Step 4: Commit the refreshed graph**

```bash
cd <repo>
git add graphify-out
git commit -m "chore: rebuild graphify graph after apps/ reorg"
```

- [ ] **Step 5: Show final log for the user**

```bash
git log --oneline
git status
```
Expected: 6 commits total (spec + 5 reorg tasks... actually 6 including this one — count and report), clean working tree except `.env` untracked (expected, gitignored).
