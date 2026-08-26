#!/usr/bin/env bash
# Install Vāṇī dictation content under /opt/bhava/content/releases/vani/
# (releases/ stays writable when an intermediate /opt/bhava/content dir is root-owned).
set -euo pipefail

BUNDLE_PATH="${1:?bundle path required}"
RELEASE_NAME="${2:?release name required}"
EXPECTED_SHA="${3:?sha256 required}"

CONTENT_ROOT="${BHAVA_CONTENT_ROOT:-/opt/bhava/content}"
RELEASES="${CONTENT_ROOT}/releases/vani"
CURRENT="${RELEASES}/current"

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

# Optional compatibility path when CONTENT_ROOT itself is writable.
if [[ -w "${CONTENT_ROOT}" ]]; then
  mkdir -p "${CONTENT_ROOT}/vani"
  ln -sfn "$CURRENT" "${CONTENT_ROOT}/vani/current"
fi

echo "Installed Vāṇī content ${RELEASE_NAME} -> ${CURRENT}"

# Replacing the release directory changes the bind-mount inode. Recreate API
# containers that mount releases/vani/current so they see the new files.
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
