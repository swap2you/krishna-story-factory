#!/usr/bin/env bash
# Install Vāṇī under /opt/bhava/releases/vani (deploy-user writable; avoid
# creating new children under root-owned /opt/bhava or content/).
set -euo pipefail

BUNDLE_PATH="${1:?bundle path required}"
RELEASE_NAME="${2:?release name required}"
EXPECTED_SHA="${3:?sha256 required}"

VANI_ROOT="${BHAVA_VANI_HOST_ROOT:-/opt/bhava/releases/vani}"
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
test -d "$DEST/restored"
# Docker may have created CURRENT as an empty directory on first mount; replace it.
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
