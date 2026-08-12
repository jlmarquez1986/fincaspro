#!/bin/sh
set -eu

if [ "${MIGRATE_ON_STARTUP:-true}" = "true" ]; then
    echo "[FincasPro] Aplicando migraciones Alembic..."
    alembic upgrade head
fi

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${UVICORN_WORKERS:-2}" \
    --proxy-headers
