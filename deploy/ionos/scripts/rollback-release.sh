#!/usr/bin/env bash
set -Eeuo pipefail

ENVIRONMENT="${1:?production or staging required}"
TARGET_SHA="${2:-}"

CONFIG_ROOT="/opt/bhava/config"
RUNTIME_ENV="${CONFIG_ROOT}/runtime.env"
PREVIOUS_FILE="/opt/bhava/releases/${ENVIRONMENT}/previous"
CURRENT_FILE="/opt/bhava/releases/${ENVIRONMENT}/current"

case "${ENVIRONMENT}" in
  production)
    ENV_KEY="BHAVA_PROD_RELEASE_SHA"
    SERVICES=(api-production web-production caddy)
    ;;
  staging)
    ENV_KEY="BHAVA_STAGING_RELEASE_SHA"
    SERVICES=(api-staging web-staging caddy)
    ;;
  *)
    echo "Invalid environment." >&2
    exit 1
    ;;
esac

mkdir -p "/opt/bhava/releases/${ENVIRONMENT}"

if [[ -z "${TARGET_SHA}" ]]; then
  if [[ ! -f "${PREVIOUS_FILE}" ]]; then
    echo "ROLLBACK_UNAVAILABLE_FIRST_RELEASE"
    echo "No previous release pointer at ${PREVIOUS_FILE}." >&2
    if [[ -f "${CURRENT_FILE}" ]]; then
      echo "Original release still recorded as current: $(cat "${CURRENT_FILE}")" >&2
      echo "ORIGINAL_RELEASE_STILL_CURRENT"
    fi
    exit 4
  fi
  TARGET_SHA="$(cat "${PREVIOUS_FILE}")"
  if [[ -z "${TARGET_SHA}" ]]; then
    echo "ROLLBACK_UNAVAILABLE_EMPTY_PREVIOUS" >&2
    exit 4
  fi
fi

if ! docker image inspect "bhava-web:${TARGET_SHA}" >/dev/null 2>&1; then
  echo "ROLLBACK_FAILED: missing image bhava-web:${TARGET_SHA}" >&2
  exit 5
fi
if ! docker image inspect "bhava-api:${TARGET_SHA}" >/dev/null 2>&1; then
  echo "ROLLBACK_FAILED: missing image bhava-api:${TARGET_SHA}" >&2
  exit 5
fi

python3 - "${RUNTIME_ENV}" "${ENV_KEY}" "${TARGET_SHA}" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
key = sys.argv[2]
value = sys.argv[3]
rows = path.read_text(encoding="utf-8").splitlines()
result = []
seen = False
for row in rows:
    if row.startswith(f"{key}="):
        result.append(f"{key}={value}")
        seen = True
    else:
        result.append(row)
if not seen:
    result.append(f"{key}={value}")
path.write_text("\n".join(result) + "\n", encoding="utf-8")
PY

cd "${CONFIG_ROOT}"
chmod +x "${CONFIG_ROOT}/scripts/"*.sh 2>/dev/null || true
docker compose --env-file "${RUNTIME_ENV}" -f docker-compose.yml up -d --no-build "${SERVICES[@]}"
mkdir -p /opt/bhava/backups
echo "${TARGET_SHA}" >"${CURRENT_FILE}"
printf '%s\t%s\t%s\trollback\n' "$(date -u +%FT%TZ)" "${ENVIRONMENT}" "${TARGET_SHA}" \
  >>/opt/bhava/backups/deployments.tsv

echo "ROLLBACK_PERFORMED"
echo "Rolled back ${ENVIRONMENT} to ${TARGET_SHA}"
