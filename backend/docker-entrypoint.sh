#!/usr/bin/env bash
set -e

echo "Running database migrations..."
poetry run alembic upgrade head

if [ "${SEED_ON_START:-false}" = "true" ]; then
  echo "Seeding bootstrap data..."
  poetry run app seed || true
fi
