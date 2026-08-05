"""Caddy security header contract for public PDF embed vs clickjacking DENY."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CADDYFILE = ROOT / "deploy" / "ionos" / "Caddyfile"


def test_caddyfile_allows_same_origin_activity_pdf_embed_only() -> None:
    text = CADDYFILE.read_text(encoding="utf-8")
    assert "@activity_pdf" in text
    assert "activity_sheet\\.pdf" in text or r"activity_sheet\.pdf" in text
    assert 'X-Frame-Options "SAMEORIGIN"' in text
    assert "frame-ancestors 'self'" in text
    assert "@not_activity_pdf" in text
    assert 'X-Frame-Options "DENY"' in text
    # Global DENY must not be applied unconditionally to every response anymore.
    header_block_start = text.index("header {")
    header_block_end = text.index("}", header_block_start)
    common_header = text[header_block_start:header_block_end]
    assert "X-Frame-Options" not in common_header


def test_caddyfile_keeps_private_story_boundary() -> None:
    text = CADDYFILE.read_text(encoding="utf-8")
    assert "private_story" in text
    assert "2[1-9]" in text
    # Split matchers (not a nested `or {` block) so stock caddy:2.10-alpine can start.
    assert "respond @private_paths 404" in text
    assert "respond @private_story 404" in text
    assert "\tor {" not in text and "\n\tor {" not in text
    assert "/stories/011*" not in text


def test_caddyfile_production_blocks_private_reader_api() -> None:
    text = CADDYFILE.read_text(encoding="utf-8")
    prod = text.split("bhava.me {", 1)[1].split("www.bhava.me", 1)[0]
    staging = text.split("staging.bhava.me {", 1)[1]
    assert "@private_reader_api" in prod
    assert "handle @private_reader_api" in prod
    assert "respond 404" in prod
    assert "@private_reader_api" not in staging
