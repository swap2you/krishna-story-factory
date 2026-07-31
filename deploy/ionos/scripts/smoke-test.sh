#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${1:?base URL required}"
EXPECTED_SHA="${2:?expected SHA required}"
# Optional third arg: staging|production — inferred from URL when omitted.
ENVIRONMENT="${3:-}"
AUTH_ARGS=()

if [[ -z "${ENVIRONMENT}" ]]; then
  case "${BASE_URL}" in
    *staging*) ENVIRONMENT="staging" ;;
    *) ENVIRONMENT="production" ;;
  esac
fi

if [[ -n "${STAGING_BASIC_AUTH_USER:-}" && -n "${STAGING_BASIC_AUTH_PASSWORD:-}" ]]; then
  AUTH_ARGS=(-u "${STAGING_BASIC_AUTH_USER}:${STAGING_BASIC_AUTH_PASSWORD}")
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# TLS/ACME must be ready before application assertions. Failure here is exit 3
# from tls-readiness.sh and must not be treated as an app rollback trigger.
if [[ "${SKIP_TLS_READINESS:-0}" != "1" ]]; then
  bash "${SCRIPT_DIR}/tls-readiness.sh" "${BASE_URL}"
fi

wait_for_ready() {
  local i code
  for i in $(seq 1 36); do
    code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/" || true)"
    if [[ "${code}" == "200" ]]; then
      echo "Endpoint ready after ${i} attempt(s)."
      return 0
    fi
    echo "Waiting for ${BASE_URL}/ (HTTP ${code:-000}) attempt ${i}/36"
    sleep 5
  done
  echo "Timed out waiting for ${BASE_URL}/ to become ready." >&2
  return 1
}

wait_for_ready

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/rights" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/001" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/010" >/dev/null

if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/011" >/dev/null; then
  echo "Story 011 is publicly reachable." >&2
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

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F '/stories/010' >/dev/null
if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F '/stories/011' >/dev/null; then
  echo "Story 011 appears in sitemap." >&2
  exit 1
fi

home_headers="$(curl -fsSI "${AUTH_ARGS[@]}" "${BASE_URL}/")"
echo "${home_headers}" | grep -Eiq '^x-content-type-options:[[:space:]]*nosniff'
echo "${home_headers}" | grep -Eiq '^x-frame-options:[[:space:]]*deny'

# Environment-aware indexing policy:
# - staging must stay noindex
# - production must NOT be globally noindex
if [[ "${ENVIRONMENT}" == "staging" ]]; then
  echo "${home_headers}" | grep -Eiq '^x-robots-tag:[[:space:]]*noindex'
else
  if echo "${home_headers}" | grep -Eiq '^x-robots-tag:[[:space:]]*noindex'; then
    echo "Production unexpectedly sends X-Robots-Tag: noindex." >&2
    exit 1
  fi
fi

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/robots.txt" >/dev/null

for asset in narration.mp3 activity_sheet.pdf story_poster.png; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" \
    "${BASE_URL}/api/v1/stories/009/assets/${asset}")"
  if [[ "${code}" != "200" ]]; then
    echo "Asset ${asset} returned ${code}, expected 200." >&2
    exit 1
  fi
done

for n in 001 002 003 004 005 006 007 008 009; do
  curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/${n}" >/dev/null
done

echo "Smoke test passed for ${BASE_URL} (${ENVIRONMENT}) at ${EXPECTED_SHA}"
