#!/usr/bin/env bash
# Wait for HTTPS/TLS readiness before application smoke.
# Distinguishes ACME provisioning from application failure.
set -Eeuo pipefail

BASE_URL="${1:?base URL required (https://host)}"
HOST="$(printf '%s' "${BASE_URL}" | sed -E 's#^https?://([^/:]+).*#\1#')"
MAX_ATTEMPTS="${TLS_READY_ATTEMPTS:-48}"
SLEEP_SECONDS="${TLS_READY_SLEEP_SECONDS:-5}"
AUTH_ARGS=()

if [[ -n "${STAGING_BASIC_AUTH_USER:-}" && -n "${STAGING_BASIC_AUTH_PASSWORD:-}" ]]; then
  AUTH_ARGS=(-u "${STAGING_BASIC_AUTH_USER}:${STAGING_BASIC_AUTH_PASSWORD}")
fi

echo "TLS readiness for ${BASE_URL} (host=${HOST}, max_attempts=${MAX_ATTEMPTS})"

# DNS must resolve before ACME or smoke can succeed.
if command -v getent >/dev/null 2>&1; then
  if ! getent ahostsv4 "${HOST}" >/dev/null 2>&1; then
    echo "DNS resolution failed for ${HOST}." >&2
    exit 2
  fi
  echo "DNS OK: $(getent ahostsv4 "${HOST}" | awk '{print $1}' | head -n1)"
elif command -v dig >/dev/null 2>&1; then
  dig +short A "${HOST}" | head -n1
fi

# TCP 443
if command -v nc >/dev/null 2>&1; then
  if ! nc -z -w 5 "${HOST}" 443; then
    echo "TCP 443 not accepting connections on ${HOST}." >&2
    exit 2
  fi
  echo "TCP 443 OK"
fi

classify_tls_error() {
  local err="$1"
  if grep -Eiq 'tlsv1 alert internal error|ssl routines|certificate|handshake|wrong version number|alert' <<<"${err}"; then
    echo "acme_or_tls_provisioning"
  elif grep -Eiq 'Could not resolve|Name or service not known|Temporary failure in name resolution' <<<"${err}"; then
    echo "dns"
  elif grep -Eiq 'Connection refused|timed out|Failed to connect' <<<"${err}"; then
    echo "network"
  else
    echo "unknown"
  fi
}

attempt=0
while (( attempt < MAX_ATTEMPTS )); do
  attempt=$((attempt + 1))
  body="$(mktemp)"
  err="$(mktemp)"
  code="$(curl -4 --http1.1 -sS -o "${body}" -w '%{http_code}' \
    --connect-timeout 10 --max-time 25 \
    "${AUTH_ARGS[@]}" "${BASE_URL}/" 2>"${err}" || true)"
  curl_err="$(cat "${err}" || true)"
  rm -f "${err}"

  if [[ "${code}" == "200" || "${code}" == "401" ]]; then
    # Certificate hostname verification via openssl when available.
    if command -v openssl >/dev/null 2>&1; then
      cert_host="$(echo | openssl s_client -servername "${HOST}" -connect "${HOST}:443" 2>/dev/null \
        | openssl x509 -noout -subject -ext subjectAltName 2>/dev/null || true)"
      # Fixed-string match only — HOST may contain regex metacharacters (e.g. dots).
      if ! grep -Fq "DNS:${HOST}" <<<"${cert_host}"; then
        echo "Attempt ${attempt}/${MAX_ATTEMPTS}: HTTP ${code} but certificate does not yet name DNS:${HOST}"
        echo "${cert_host}" | head -n 5
        rm -f "${body}"
        sleep "${SLEEP_SECONDS}"
        continue
      fi
      echo "Certificate names DNS:${HOST}"
    fi
    rm -f "${body}"
    echo "TLS ready after ${attempt} attempt(s) (HTTP ${code})."
    exit 0
  fi

  class="$(classify_tls_error "${curl_err}")"
  echo "Attempt ${attempt}/${MAX_ATTEMPTS}: HTTP ${code:-000} class=${class}"
  if [[ -n "${curl_err}" ]]; then
    echo "  curl: ${curl_err}" | head -c 400
    echo
  fi
  rm -f "${body}"
  # Exponential-ish backoff capped at 20s
  sleep_for="${SLEEP_SECONDS}"
  if (( attempt > 12 )); then sleep_for=10; fi
  if (( attempt > 24 )); then sleep_for=15; fi
  if (( attempt > 36 )); then sleep_for=20; fi
  sleep "${sleep_for}"
done

echo "TLS readiness timed out for ${BASE_URL} after ${MAX_ATTEMPTS} attempts." >&2
echo "This indicates ACME/TLS provisioning delay or failure, not necessarily an application regression." >&2
exit 3
