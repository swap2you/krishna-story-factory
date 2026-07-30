#!/usr/bin/env bash
set -Eeuo pipefail

BUNDLE="${1:?bundle path required}"
RELEASE="${2:?content release name required}"
EXPECTED_SHA="${3:?expected bundle sha256 required}"
CONTENT_ROOT="${BHAVA_CONTENT_ROOT:-/opt/bhava/content}"

actual_sha="$(sha256sum "${BUNDLE}" | awk '{print $1}')"
if [[ "${actual_sha}" != "${EXPECTED_SHA}" ]]; then
  echo "Content bundle hash mismatch." >&2
  exit 1
fi

target="${CONTENT_ROOT}/releases/${RELEASE}"
staging="${target}.staging"

rm -rf "${staging}"
mkdir -p "${staging}"
tar -xzf "${BUNDLE}" -C "${staging}"

python3 /opt/bhava/config/scripts/validate_public_content.py \
  --directory "${staging}" \
  --max-story 9

rm -rf "${target}"
mv "${staging}" "${target}"
ln -sfn "${target}" "${CONTENT_ROOT}/current"

echo "${RELEASE}" >"${CONTENT_ROOT}/CURRENT_RELEASE"
echo "Installed content release ${RELEASE}"
