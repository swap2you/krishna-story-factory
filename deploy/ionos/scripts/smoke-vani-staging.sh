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

payload="$(curl -sS "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/vani/krishna-book")"
python -c 'import json,sys; data=json.loads(sys.stdin.read()); tracks=data.get("tracks") or []; assert len(tracks)==91, len(tracks); available=[t for t in tracks if str(t.get("availability","")).lower()=="available"]; print(f"available={len(available)} streamable={sum(1 for t in tracks if t.get(\"stream_allowed\"))}"); assert len(available)>=70; gaps={"30","58","66"};
for t in tracks:
  tid=str(t.get("canonical_track_id") or t.get("track_id"));
  assert (tid not in gaps) or str(t.get("availability")).lower()=="unavailable", t
print("gap honesty ok")' <<<"$payload"

track_id="$(python -c 'import json,sys; data=json.loads(sys.stdin.read());
for t in data.get("tracks") or []:
  if t.get("stream_allowed") and t.get("audio_url"):
    print(t.get("track_id") or t.get("canonical_track_id")); break' <<<"$payload")"
if [[ -n "${track_id}" ]]; then
  code="$(curl -sS -o /dev/null -w '%{http_code}' -H 'Range: bytes=0-1023' "${AUTH_ARGS[@]}" "${BASE_URL}/api/v1/vani/krishna-book/${track_id}/audio")"
  echo "audio_range_${track_id}=${code}"
  [[ "$code" == "206" || "$code" == "200" ]]
  detail="$(curl -sS -o /dev/null -w '%{http_code}' "${AUTH_ARGS[@]}" "${BASE_URL}/prabhupada-vani/krishna-book/${track_id}")"
  echo "detail=${detail}"
  [[ "$detail" == "200" ]]
fi
echo "Vāṇī staging smoke passed"
