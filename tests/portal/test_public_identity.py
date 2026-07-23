"""Phase 3 — ensure no civil-identity leaks in public-facing config or pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "apps" / "web"

FORBIDDEN = [
    re.compile(r"swapnil", re.IGNORECASE),
    re.compile(r"swapnilpatil", re.IGNORECASE),
    re.compile(r"linkedin\.com/in/swapnil", re.IGNORECASE),
    re.compile(r"github\.com/swap2you", re.IGNORECASE),
    re.compile(r"swap2you", re.IGNORECASE),
]

PUBLIC_PAGES = [
    WEB / "app" / "contact" / "page.tsx",
    WEB / "app" / "about" / "page.tsx",
    WEB / "app" / "privacy" / "page.tsx",
    WEB / "app" / "source-permissions" / "page.tsx",
    WEB / "app" / "layout.tsx",
]

CONTACT_JSON = WEB / "config" / "contact.json"


def _check_forbidden(text: str, label: str) -> list[str]:
    hits: list[str] = []
    for pattern in FORBIDDEN:
        match = pattern.search(text)
        if match:
            hits.append(f"{label}: found forbidden string {match.group()!r}")
    return hits


class TestContactConfig:
    def test_contact_json_exists(self) -> None:
        assert CONTACT_JSON.is_file(), "contact.json missing"

    def test_only_allowed_keys(self) -> None:
        data = json.loads(CONTACT_JSON.read_text(encoding="utf-8"))
        allowed = {"project_name", "domain", "steward_name", "public_email"}
        extra = set(data.keys()) - allowed
        assert not extra, f"Unexpected keys in contact.json: {extra}"

    def test_no_website_linkedin_github(self) -> None:
        data = json.loads(CONTACT_JSON.read_text(encoding="utf-8"))
        for key in ("website", "linkedin_url", "github_url", "contact_url"):
            assert key not in data, f"contact.json must not contain {key}"

    def test_steward_name(self) -> None:
        data = json.loads(CONTACT_JSON.read_text(encoding="utf-8"))
        assert data.get("steward_name") == "Svarna Gauranga Das"

    def test_public_email(self) -> None:
        data = json.loads(CONTACT_JSON.read_text(encoding="utf-8"))
        assert data.get("public_email") == "swarnagaurangadas@gmail.com"

    def test_no_forbidden_strings(self) -> None:
        text = CONTACT_JSON.read_text(encoding="utf-8")
        hits = _check_forbidden(text, "contact.json")
        assert not hits, "\n".join(hits)


class TestPublicPages:
    @pytest.mark.parametrize(
        "page",
        PUBLIC_PAGES,
        ids=[str(p.relative_to(ROOT)) for p in PUBLIC_PAGES],
    )
    def test_no_forbidden_strings_in_page(self, page: Path) -> None:
        if not page.is_file():
            pytest.skip(f"{page.name} not present")
        text = page.read_text(encoding="utf-8")
        hits = _check_forbidden(text, page.name)
        assert not hits, "\n".join(hits)

    def test_layout_no_factory_studio_link(self) -> None:
        layout = WEB / "app" / "layout.tsx"
        if not layout.is_file():
            pytest.skip("layout.tsx not present")
        text = layout.read_text(encoding="utf-8")
        assert "Factory Studio" not in text, "Public footer must not link to Factory Studio"
