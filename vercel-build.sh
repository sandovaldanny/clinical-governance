#!/usr/bin/env bash
# Build de Vercel: SPA + migraciones + seed demo (idempotente) contra la base gestionada.
# Las migraciones usan la URL sin pooler (DDL); el runtime usa DATABASE_URL (pooled).
set -euo pipefail

npm --prefix frontend run build

python3 -m pip install -q -r requirements.txt
cd backend
export DATABASE_URL="${DATABASE_URL_UNPOOLED:-${DATABASE_URL:-}}"
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL not set: skipping migrations and seed"
  exit 0
fi
python3 -m alembic upgrade head
python3 -m app.scripts.seed_demo_data
