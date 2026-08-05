#!/usr/bin/env python3
"""Patch host Caddyfile with production-only private reader handle denies."""
from __future__ import annotations

import re
from pathlib import Path

MARKER = "INCIDENT_PRIVATE_READER_DENY_V2"
BLOCK = f"""
\t# {MARKER} temporary production-only containment
\thandle /api/v1/stories/021/reader {{
\t\trespond 404
\t}}
\thandle /api/v1/stories/021/reader.txt {{
\t\trespond 404
\t}}
\thandle /api/v1/stories/022/reader {{
\t\trespond 404
\t}}
\thandle /api/v1/stories/022/reader.txt {{
\t\trespond 404
\t}}
"""


def main() -> None:
    path = Path("/opt/bhava/config/Caddyfile")
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\n\t# INCIDENT_PRIVATE_READER_DENY_V[12].*?(?=\n\thandle |\n\t@|\n})",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    needle = "\thandle /api/* {\n\t\treverse_proxy api-production:8000\n\t}"
    parts = text.split("bhava.me {", 1)
    if len(parts) != 2:
        raise SystemExit("bhava.me site block missing")
    head, rest = parts
    site, tail = rest.split("\n}", 1)
    if needle not in site:
        raise SystemExit("production api handle block missing")
    if MARKER not in site:
        site = site.replace(needle, BLOCK + "\n" + needle, 1)
    path.write_text(head + "bhava.me {" + site + "\n}" + tail, encoding="utf-8")
    print("caddy_incident_handle_deny_applied")


if __name__ == "__main__":
    main()
