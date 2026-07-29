#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${1:?base URL required}"
EXPECTED_SHA="${2:?expected SHA required}"
AUTH_ARGS=()

if [[ -n "${STAGING_BASIC_AUTH_USER:-}" && -n "${STAGING_BASIC_AUTH_PASSWORD:-}" ]]; then
  AUTH_ARGS=(-u "${STAGING_BASIC_AUTH_USER}:${STAGING_BASIC_AUTH_PASSWORD}")
fi

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/rights" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/001" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/009" >/dev/null

if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/010" >/dev/null; then
  echo "Story 010 is publicly reachable." >&2
  exit 1
fi

for private_path in /studio /dev/audio-lab /api/studio/session /api/v1/factory/status; do
  status="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}${private_path}")"
  if [[ "${status}" != "404" ]]; then
    echo "Private path ${private_path} returned ${status}, expected 404." >&2
    exit 1
  fi
done

version="$(curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/version")"
echo "${version}" | grep -F "${EXPECTED_SHA}" >/dev/null

headers="$(curl -fsSI "${AUTH_ARGS[@]}" -H 'Range: bytes=0-1023' \
  "${BASE_URL}/api/v1/stories/009/assets/narration.mp3")"
echo "${headers}" | grep -Eiq '^HTTP/[0-9.]+ 206'
echo "${headers}" | grep -Eiq '^content-range: bytes 0-1023/'
echo "${headers}" | grep -Eiq '^accept-ranges: bytes'

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F '/stories/009' >/dev/null
if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F '/stories/010' >/dev/null; then
  echo "Story 010 appears in sitemap." >&2
  exit 1
fi

echo "Smoke test passed for ${BASE_URL} at ${EXPECTED_SHA}"
