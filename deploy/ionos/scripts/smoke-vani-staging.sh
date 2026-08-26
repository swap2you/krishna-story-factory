#!/usr/bin/env bash
# Optional Stage-1 Vāṇī smoke (authenticated).
set -euo pipefail
BASE_URL="${1:-https://staging.bhava.me}"
AUTH_USER="${STAGING_BASIC_AUTH_USER:-}"
AUTH_PASS="${STAGING_BASIC_AUTH_PASSWORD:-}"
AUTH_ARGS=()
if [[ -n "$AUTH_USER" ]]; then
  AUTH_ARGS=(-u "${AUTH_USER}:${AUTH_PASS}")
fi

echo "Vāṇī smoke against ${BASE_URL}"
landing="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/prabhupada-vani")"
catalog="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/prabhupada-vani/krishna-book")"
api="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/vani/krishna-book")"
echo "landing=${landing} catalog=${catalog} api=${api}"
[[ "$landing" == "200" && "$catalog" == "200" && "$api" == "200" ]]

payload_file="$(mktemp)"
version_file="$(mktemp)"
trap 'rm -f "${payload_file}" "${version_file}"' EXIT

curl -sS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/vani/krishna-book" >"${payload_file}"
track_id="$(python3 - "${payload_file}" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)
tracks = data.get("tracks") or []
assert len(tracks) == 91, len(tracks)
available = [t for t in tracks if str(t.get("availability", "")).lower() == "available"]
streamable = sum(1 for t in tracks if t.get("stream_allowed"))
print(f"available={len(available)} streamable={streamable}", file=sys.stderr)
assert len(available) >= 70
gaps = {"30", "58", "66"}
for t in tracks:
    tid = str(t.get("canonical_track_id") or t.get("track_id") or "")
    assert (tid not in gaps) or str(t.get("availability")).lower() == "unavailable", t
print("gap honesty ok", file=sys.stderr)

for t in tracks:
    if t.get("stream_allowed") and t.get("audio_url"):
        print(t.get("track_id") or t.get("canonical_track_id") or "")
        break
PY
)"

if [[ -n "${track_id}" ]]; then
  code="$(curl -sS -o /dev/null -w '%{http_code}' -H 'Range: bytes=0-1023' "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/vani/krishna-book/${track_id}/audio")"
  echo "audio_range_${track_id}=${code}"
  [[ "$code" == "206" || "$code" == "200" ]]
  detail="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/prabhupada-vani/krishna-book/${track_id}")"
  echo "detail=${detail}"
  [[ "$detail" == "200" ]]
fi

if curl -sS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/version" >"${version_file}"; then
  python3 - "${version_file}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
tag = data.get("vani_content_tag") or ""
sha = data.get("vani_content_sha256") or ""
print(f"vani_content_tag={tag}")
print(f"vani_content_sha256={sha[:16]}..." if sha else "vani_content_sha256=")
assert tag.startswith("bhava-vani-"), tag
assert len(sha) == 64, sha
PY
fi

echo "Vāṇī staging smoke passed"
