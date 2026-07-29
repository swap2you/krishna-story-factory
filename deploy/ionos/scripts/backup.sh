#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_ROOT="/opt/bhava/backups"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="${BACKUP_ROOT}/bhava-${STAMP}.tar.gz"

mkdir -p "${BACKUP_ROOT}"

tar -czf "${TARGET}" \
  /opt/bhava/config \
  /opt/bhava/releases \
  /opt/bhava/content/CURRENT_RELEASE \
  /opt/bhava/content/releases/*/BHAVA_DEPLOYMENT_CONTENT_MANIFEST.json \
  2>/dev/null || true

sha256sum "${TARGET}" >"${TARGET}.sha256"

find "${BACKUP_ROOT}" -type f -name 'bhava-*.tar.gz*' -mtime +14 -delete
echo "Created ${TARGET}"
