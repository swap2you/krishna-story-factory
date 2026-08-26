#!/usr/bin/env bash
# Install Vāṇī under content/releases/vani-kb-dictations (deploy-user writable).
# Do not use a bare "vani" leaf name — earlier Docker mounts may have left
# root-owned empty dirs at sibling paths.
set -euo pipefail

BUNDLE_PATH="${1:?bundle path required}"
RELEASE_NAME="${2:?release name required}"
EXPECTED_SHA="${3:?sha256 required}"

VANI_ROOT="${BHAVA_VANI_HOST_ROOT:-/opt/bhava/content/releases/vani-kb-dictations}"
RELEASES="${VANI_ROOT}/releases"
CURRENT="${VANI_ROOT}/current"

mkdir -p "$RELEASES"
cd "$(dirname "$BUNDLE_PATH")"
echo "${EXPECTED_SHA}  $(basename "$BUNDLE_PATH")" > /tmp/vani-expected.sha256
sha256sum -c /tmp/vani-expected.sha256

DEST="${RELEASES}/${RELEASE_NAME}"
rm -rf "$DEST"
mkdir -p "$DEST"
tar -xzf "$BUNDLE_PATH" -C "$DEST" --strip-components=1
test -f "$DEST/manifests/collection.json"
# Stage-1 serve bundle ships originals (restoration_bypassed); restored/ is optional.
if [[ ! -d "$DEST/original" && ! -d "$DEST/restored" ]]; then
  echo "Vāṇī bundle missing original/ and restored/" >&2
  exit 1
fi
rm -rf "$CURRENT"
ln -sfn "$DEST" "$CURRENT"

echo "Installed Vāṇī content ${RELEASE_NAME} -> ${CURRENT}"

if [[ "${BHAVA_RECREATE_CONTENT_MOUNTS:-1}" == "1" && -f /opt/bhava/config/docker-compose.yml && -f /opt/bhava/config/runtime.env ]]; then
  (
    cd /opt/bhava/config
    running="$(docker compose --env-file runtime.env ps --status running --services 2>/dev/null || true)"
    for svc in api-production api-staging; do
      if printf '%s\n' "${running}" | grep -qx "${svc}"; then
        echo "Recreating ${svc} to refresh Vāṇī content bind mounts"
        docker compose --env-file runtime.env up -d --force-recreate --no-deps "${svc}"
      fi
    done
  )
fi
