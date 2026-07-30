#!/usr/bin/env bash
set -Eeuo pipefail

ENVIRONMENT="${1:?production or staging required}"
TARGET_SHA="${2:-}"

CONFIG_ROOT="/opt/bhava/config"
RUNTIME_ENV="${CONFIG_ROOT}/runtime.env"

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

if [[ -z "${TARGET_SHA}" ]]; then
  TARGET_SHA="$(cat "/opt/bhava/releases/${ENVIRONMENT}/previous")"
fi

docker image inspect "bhava-web:${TARGET_SHA}" >/dev/null
docker image inspect "bhava-api:${TARGET_SHA}" >/dev/null

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
docker compose --env-file "${RUNTIME_ENV}" -f docker-compose.yml up -d --no-build "${SERVICES[@]}"
echo "${TARGET_SHA}" >"/opt/bhava/releases/${ENVIRONMENT}/current"
printf '%s\t%s\t%s\trollback\n' "$(date -u +%FT%TZ)" "${ENVIRONMENT}" "${TARGET_SHA}" \
  >>/opt/bhava/releases/deployments.tsv

echo "Rolled back ${ENVIRONMENT} to ${TARGET_SHA}"
