#!/usr/bin/env bash
# Install Vāṇī dictation content bundle under /opt/bhava/content/vani/
set -euo pipefail

BUNDLE_PATH="${1:?bundle path required}"
RELEASE_NAME="${2:?release name required}"
EXPECTED_SHA="${3:?sha256 required}"

ROOT="${BHAVA_CONTENT_ROOT:-/opt/bhava/content}"
INCOMING="${ROOT}/incoming"
RELEASES="${ROOT}/vani/releases"
CURRENT="${ROOT}/vani/current"

mkdir -p "$INCOMING" "$RELEASES"
cd "$(dirname "$BUNDLE_PATH")"
echo "${EXPECTED_SHA}  $(basename "$BUNDLE_PATH")" > /tmp/vani-expected.sha256
sha256sum -c /tmp/vani-expected.sha256

DEST="${RELEASES}/${RELEASE_NAME}"
rm -rf "$DEST"
mkdir -p "$DEST"
tar -xzf "$BUNDLE_PATH" -C "$DEST" --strip-components=1
test -f "$DEST/manifests/collection.json"
test -d "$DEST/restored"
ln -sfn "$DEST" "$CURRENT"
echo "Installed Vāṇī content ${RELEASE_NAME} -> ${CURRENT}"
