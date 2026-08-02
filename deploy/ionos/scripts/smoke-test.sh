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

version="$(curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/version")"
echo "${version}" | grep -F "${EXPECTED_SHA}" >/dev/null
PUBLIC_MAX="$(printf '%s' "${version}" | python -c 'import json,sys; print(int(json.load(sys.stdin)["public_story_max"]))')"
if [[ "${PUBLIC_MAX}" -lt 1 || "${PUBLIC_MAX}" -gt 999 ]]; then
  echo "Invalid public_story_max from /api/v1/version: ${PUBLIC_MAX}" >&2
  exit 1
fi
LAST_STORY="$(printf '%03d' "${PUBLIC_MAX}")"
PRIVATE_STORY="$(printf '%03d' "$((PUBLIC_MAX + 1))")"
FIRST_STORY="001"

ready_code="$(curl -sS -o /tmp/bhava_readyz.json -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/readyz" || true)"
if [[ "${ready_code}" != "200" ]]; then
  echo "/readyz returned HTTP ${ready_code:-000}; catalog must be complete before smoke passes." >&2
  exit 1
fi

stories_json="$(curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/stories")"
python - "${stories_json}" "${PUBLIC_MAX}" <<'PY'
import json, sys
raw, expected = sys.argv[1], int(sys.argv[2])
try:
    data = json.loads(raw)
except json.JSONDecodeError as exc:
    raise SystemExit(f"/api/v1/stories invalid JSON: {exc}") from exc
if not isinstance(data, list):
    raise SystemExit("/api/v1/stories must return a JSON array")
if len(data) != expected:
    raise SystemExit(f"/api/v1/stories length {len(data)} != public_story_max {expected}")
required = ("story_no", "slug", "title", "poster_url", "narration_url", "reader_url")
for index, item in enumerate(data):
    if not isinstance(item, dict):
        raise SystemExit(f"story[{index}] is not an object")
    for key in required:
        if not item.get(key):
            raise SystemExit(f"story[{index}] missing {key}")
if data[0].get("story_no") != "001":
    raise SystemExit(f"first story_no={data[0].get('story_no')!r}, expected '001'")
last = f"{expected:03d}"
if data[-1].get("story_no") != last:
    raise SystemExit(f"final story_no={data[-1].get('story_no')!r}, expected {last!r}")
print(f"catalog_ok count={len(data)} first=001 last={last}")
PY

library_html="$(curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/library/krishna-book")"
FIRST_TITLE="$(printf '%s' "${stories_json}" | python -c 'import json,sys; print(json.load(sys.stdin)[0]["title"])')"
LAST_TITLE="$(printf '%s' "${stories_json}" | python -c 'import json,sys; print(json.load(sys.stdin)[-1]["title"])')"
printf '%s' "${library_html}" | grep -F "${FIRST_TITLE}" >/dev/null
printf '%s' "${library_html}" | grep -F "${LAST_TITLE}" >/dev/null
if printf '%s' "${library_html}" | grep -Eiq 'library is being prepared|Run the Bhāva API|Run the Bhava API|temporarily unavailable'; then
  echo "Library page shows an empty/unavailable catalog message." >&2
  exit 1
fi
card_count="$(printf '%s' "${library_html}" | grep -oE 'href="/stories/[0-9]{3}"' | sort -u | wc -l | tr -d ' ')"
if [[ "${card_count}" != "${PUBLIC_MAX}" ]]; then
  echo "Library story-card links=${card_count}, expected ${PUBLIC_MAX}." >&2
  exit 1
fi

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/${FIRST_STORY}" >/dev/null
curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/${LAST_STORY}" >/dev/null
if [[ "${PUBLIC_MAX}" -ge 10 ]]; then
  curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/010" >/dev/null
fi

if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/stories/${PRIVATE_STORY}" >/dev/null; then
  echo "Story ${PRIVATE_STORY} is publicly reachable." >&2
  exit 1
fi

for private_path in /studio /dev/audio-lab /api/studio/session /api/v1/factory/status; do
  status="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}${private_path}")"
  if [[ "${status}" != "404" ]]; then
    echo "Private path ${private_path} returned ${status}, expected 404." >&2
    exit 1
  fi
done

headers="$(curl -fsSI "${AUTH_ARGS[@]}" -H 'Range: bytes=0-1023' \
  "${BASE_URL}/api/v1/stories/009/assets/narration.mp3")"
echo "${headers}" | grep -Eiq '^HTTP/[0-9.]+ 206'
echo "${headers}" | grep -Eiq '^content-range: bytes 0-1023/'
echo "${headers}" | grep -Eiq '^accept-ranges: bytes'

curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F "/stories/${LAST_STORY}" >/dev/null
if curl -fsS "${AUTH_ARGS[@]}" "${BASE_URL}/sitemap.xml" | grep -F "/stories/${PRIVATE_STORY}" >/dev/null; then
  echo "Story ${PRIVATE_STORY} appears in sitemap." >&2
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

echo "Smoke test passed for ${BASE_URL} (${ENVIRONMENT}) at ${EXPECTED_SHA} public_max=${PUBLIC_MAX}"
