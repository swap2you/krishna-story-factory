#!/usr/bin/env bash
set -Eeuo pipefail

BUNDLE="${1:?bundle path required}"
RELEASE="${2:?content release name required}"
EXPECTED_SHA="${3:?expected bundle sha256 required}"
CONTENT_ROOT="${BHAVA_CONTENT_ROOT:-/opt/bhava/content}"
# Prefer explicit env from deploy workflow / RELEASE_CONTENT; default matches current pin.
MAX_STORY="${BHAVA_PUBLIC_STORY_MAX:-${4:-20}}"

actual_sha="$(sha256sum "${BUNDLE}" | awk '{print $1}')"
if [[ "${actual_sha}" != "${EXPECTED_SHA}" ]]; then
  echo "Content bundle hash mismatch." >&2
  exit 1
fi

mkdir -p "${CONTENT_ROOT}/releases"
target="${CONTENT_ROOT}/releases/${RELEASE}"
staging="${target}.staging"

rm -rf "${staging}"
mkdir -p "${staging}"
tar -xzf "${BUNDLE}" -C "${staging}"

python3 /opt/bhava/config/scripts/validate_public_content.py \
  --directory "${staging}" \
  --max-story "${MAX_STORY}"

rm -rf "${target}"
mv "${staging}" "${target}"

# Active pointer lives under releases/ so it remains writable when an intermediate
# /opt/bhava/content directory was left root-owned by older bootstrap installs.
ln -sfn "${target}" "${CONTENT_ROOT}/releases/current"
echo "${RELEASE}" >"${CONTENT_ROOT}/releases/CURRENT_RELEASE"

if [[ -w "${CONTENT_ROOT}" ]]; then
  ln -sfn "${CONTENT_ROOT}/releases/current" "${CONTENT_ROOT}/current"
  echo "${RELEASE}" >"${CONTENT_ROOT}/CURRENT_RELEASE"
fi

echo "Installed content release ${RELEASE} (max_story=${MAX_STORY})"

# Replacing the release directory changes the bind-mount inode. Recreate any
# running API containers that mount releases/current so they see the new files.
# Without this, an already-running api-production can observe an empty /app/output
# while the host tree looks complete (P1 catalog outage class).
if [[ "${BHAVA_RECREATE_CONTENT_MOUNTS:-1}" == "1" && -f /opt/bhava/config/docker-compose.yml && -f /opt/bhava/config/runtime.env ]]; then
  (
    cd /opt/bhava/config
    running="$(docker compose --env-file runtime.env ps --status running --services 2>/dev/null || true)"
    for svc in api-production api-staging; do
      if printf '%s\n' "${running}" | grep -qx "${svc}"; then
        echo "Recreating ${svc} to refresh content bind mounts"
        docker compose --env-file runtime.env up -d --force-recreate --no-deps "${svc}"
      fi
    done
  )
fi
