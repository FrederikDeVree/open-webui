#!/bin/bash
# backup-script.sh — automated pg_dump with rotation

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql.gz"

echo "[$(date)] Starting backup..."

# Perform backup
if PGPASSWORD="${POSTGRES_PASSWORD}" gosu postgres pg_dump -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -Fc "${POSTGRES_DB:-postgres}" | gzip > "${BACKUP_FILE}"; then
  echo "[$(date)] Backup successful: ${BACKUP_FILE}"
else
  echo "[$(date)] Backup FAILED!" >&2
  rm -f "${BACKUP_FILE}"
fi

# Rotate old backups
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "postgres_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

echo "[$(date)] Done."

# Schedule next run
sleep 86400
