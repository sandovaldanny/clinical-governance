#!/usr/bin/env bash
# Build de Vercel: SPA + migraciones + seed demo (idempotente) contra la base gestionada.
# Las migraciones usan la URL sin pooler (DDL); el runtime usa DATABASE_URL (pooled).
set -euo pipefail

# Nunca heredar el bypass de login de un .env local: en Vercel el valor viene del entorno del proyecto.
export VITE_AUTH_DISABLED="${VITE_AUTH_DISABLED:-false}"
npm --prefix frontend run build

# La imagen de build usa un Python gestionado por uv (PEP 668): instalamos en un venv propio.
VENV="/tmp/aegis-build-venv"
python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r requirements.txt
PY="$VENV/bin/python"
cd backend
export DATABASE_URL="${DATABASE_URL_UNPOOLED:-${DATABASE_URL:-}}"
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL not set: skipping migrations and seed"
  exit 0
fi
"$PY" -m alembic upgrade head
"$PY" -m app.scripts.seed_demo_data
