#!/usr/bin/env bash
# Update selected KEY=VALUE pairs in /opt/bhava/config/runtime.env
set -Eeuo pipefail

RUNTIME_ENV="${1:?runtime.env path required}"
shift

mkdir -p "$(dirname "$RUNTIME_ENV")"
touch "$RUNTIME_ENV"

python3 - "$RUNTIME_ENV" "$@" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
updates = {}
for item in sys.argv[2:]:
    if "=" not in item:
        raise SystemExit(f"expected KEY=VALUE, got {item!r}")
    key, value = item.split("=", 1)
    updates[key] = value

rows = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
out = []
seen = set()
for row in rows:
    key = row.split("=", 1)[0] if "=" in row else ""
    if key in updates:
        out.append(f"{key}={updates[key]}")
        seen.add(key)
    else:
        out.append(row)
for key, value in updates.items():
    if key not in seen:
        out.append(f"{key}={value}")
path.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"updated {path} keys={sorted(updates)}")
PY
