#!/usr/bin/env bash
# Bash companion to scripts/release-bhava.ps1 (subset: status + dry-run).
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:-status}"
CONTENT_TAG="${CONTENT_RELEASE_TAG:-bhava-content-001-009-v1}"
PUBLIC_MAX="${PUBLIC_STORY_MAX:-9}"

case "$MODE" in
  status)
    git fetch --all --prune
    echo "branch=$(git branch --show-current)"
    echo "origin/main=$(git rev-parse origin/main)"
    echo "origin/develop=$(git rev-parse origin/develop)"
    echo "content_default=${CONTENT_TAG} public_max=${PUBLIC_MAX}"
    curl -fsS https://bhava.me/api/v1/version || true
    echo
    ;;
  dry-run)
    test -z "$(git status --porcelain)" || { echo "dirty tree"; exit 1; }
    echo "Would deploy origin/develop=$(git rev-parse origin/develop) with ${CONTENT_TAG}"
    echo "Would require explicit promotion before production"
    ;;
  *)
    echo "Usage: $0 [status|dry-run]" >&2
    exit 2
    ;;
esac
