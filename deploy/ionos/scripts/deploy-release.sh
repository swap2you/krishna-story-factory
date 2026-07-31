#!/usr/bin/env bash
set -Eeuo pipefail

ENVIRONMENT="${1:?production or staging required}"
RELEASE_SHA="${2:?release SHA required}"
IMAGE_ARCHIVE="${3:?image archive required}"
CONFIG_ARCHIVE="${4:?configuration archive required}"

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
    echo "Invalid environment: ${ENVIRONMENT}" >&2
    exit 1
    ;;
esac

CONFIG_ROOT="/opt/bhava/config"
RUNTIME_ENV="${CONFIG_ROOT}/runtime.env"
PREVIOUS_FILE="/opt/bhava/releases/${ENVIRONMENT}/previous"
CURRENT_FILE="/opt/bhava/releases/${ENVIRONMENT}/current"

mkdir -p "${CONFIG_ROOT}" "/opt/bhava/releases/${ENVIRONMENT}"

if [[ -f "${CURRENT_FILE}" ]]; then
  cp "${CURRENT_FILE}" "${PREVIOUS_FILE}"
fi

docker load -i "${IMAGE_ARCHIVE}"

tmp_config="$(mktemp -d)"
tar -xzf "${CONFIG_ARCHIVE}" -C "${tmp_config}"
rsync -a --delete --exclude runtime.env "${tmp_config}/" "${CONFIG_ROOT}/"
rm -rf "${tmp_config}"

if [[ ! -f "${RUNTIME_ENV}" ]]; then
  cp "${CONFIG_ROOT}/runtime.env.example" "${RUNTIME_ENV}"
fi

python3 - "${RUNTIME_ENV}" "${ENV_KEY}" "${RELEASE_SHA}" <<'PY'
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
docker compose --env-file "${RUNTIME_ENV}" -f docker-compose.yml config >/dev/null

# On a 2 GB VPS, staging is temporary. Stop it before a production cutover
# so production retains predictable memory headroom.
if [[ "${ENVIRONMENT}" == "production" ]]; then
  docker compose --env-file "${RUNTIME_ENV}" -f docker-compose.yml     stop web-staging api-staging >/dev/null 2>&1 || true
fi

docker compose --env-file "${RUNTIME_ENV}" -f docker-compose.yml up -d --no-build "${SERVICES[@]}"

mkdir -p /opt/bhava/backups
echo "${RELEASE_SHA}" >"${CURRENT_FILE}"
printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "${ENVIRONMENT}" "${RELEASE_SHA}" \
  >>/opt/bhava/backups/deployments.tsv

if [[ -f "${PREVIOUS_FILE}" ]]; then
  echo "rollback_pointer_ready=1 previous=$(cat "${PREVIOUS_FILE}")"
else
  echo "rollback_pointer_ready=0 first_release_for_${ENVIRONMENT}"
fi

echo "Deployed ${ENVIRONMENT} ${RELEASE_SHA}"
