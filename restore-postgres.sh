#!/bin/bash
# restore-postgres.sh — restore a pg_dump backup created by backup-postgres.sh
#
# Usage: ./restore-postgres.sh <backup_file.sql.gz>
#
# Runs inside the backup container context (has psql/pg_restore + network
# access to postgres). Intended to be invoked via:
#   docker compose -f docker-compose.dev-arvoo.yaml exec backup \
#     restore-postgres.sh /backups/postgres_backup_TIMESTAMP.sql.gz

set -euo pipefail

BACKUP_FILE="${1:-}"

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "Usage: $0 <backup_file.sql.gz>" >&2
  exit 1
fi

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

: "${POSTGRES_HOST:?POSTGRES_HOST not set}"
: "${POSTGRES_PORT:?POSTGRES_PORT not set}"
: "${POSTGRES_USER:?POSTGRES_USER not set}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}"
: "${POSTGRES_DB:?POSTGRES_DB not set}"

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "[$(date)] Restoring '${BACKUP_FILE}' into database '${POSTGRES_DB}' on ${POSTGRES_HOST}:${POSTGRES_PORT}..."

read -r -p "This will overwrite existing objects in '${POSTGRES_DB}'. Continue? [y/N] " CONFIRM
if [[ ! "${CONFIRM}" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

gunzip -c "${BACKUP_FILE}" | gosu postgres pg_restore \
  -h "${POSTGRES_HOST}" \
  -p "${POSTGRES_PORT}" \
  -U "${POSTGRES_USER}" \
  -d "${POSTGRES_DB}" \
  --clean --if-exists --no-owner

echo "[$(date)] Restore complete."
