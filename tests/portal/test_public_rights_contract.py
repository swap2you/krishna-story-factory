"""Public rights contract for Stories 001–020 web-assets (D-02 / D-11).

When data/web-assets exists for 001–020, assert:
- web_manifest.rights is non-empty
- required attribution present (Svarna Gauranga Das / Dauji Publication / Bhāva)
- contact_email never present in public rights
- reader.md contains Rights and Credits without contact_email

Skips gracefully when assets are missing (CI without content fixture).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WEB_ASSETS_ROOT = ROOT / "data" / "web-assets"
PUBLIC_STORIES = [f"{n:03d}" for n in range(1, 21)]

sys.path.insert(0, str(ROOT / "apps" / "api"))

REQUIRED_ATTR = (
    "Svarna Gauranga Das",
    "Dauji Publication",
    "Bhāva",
)


def _web_dir(story_no: str) -> Path | None:
    dest = WEB_ASSETS_ROOT / story_no
    return dest if dest.is_dir() else None


def _stories_with_web_assets() -> list[str]:
    return [sn for sn in PUBLIC_STORIES if _web_dir(sn) is not None]


@pytest.fixture(scope="module")
def stories_with_assets() -> list[str]:
    found = _stories_with_web_assets()
    if not found:
        pytest.skip(
            "No Stories 001–020 under data/web-assets; skip public rights contract "
            "(CI without content fixture)."
        )
    return found


def test_sanitize_omits_contact_and_synthesizes_when_empty() -> None:
    from bhava_api.web_assets.public_rights import (
        ensure_reader_rights_section,
        sanitize_public_rights,
    )

    with_email = sanitize_public_rights(
        {
            "title": "Example",
            "version": "2.1.1-copyright",
            "rights": {
                "author": "Svarna Gauranga Das",
                "copyright_owner": "Svarna Gauranga Das",
                "publisher": "Dauji Publication",
                "project": "Bhāva",
                "contact_email": "svarnagaurangdas@gmail.com",
                "copyright_notice": "Copyright © Svarna Gauranga Das\nContact: x@y.com",
                "rights_limitation": "Claim limited to original adaptation.",
            },
        },
        story_no="001",
    )
    assert "contact_email" not in with_email
    assert with_email["publisher"] == "Dauji Publication"
    assert "Svarna Gauranga Das" in with_email["copyright_owner"]

    synthesized = sanitize_public_rights({"title": "Empty Rights Story"}, story_no="015")
    assert synthesized
    assert "contact_email" not in synthesized
    assert synthesized["author"] == "Svarna Gauranga Das"
    assert synthesized["publisher"] == "Dauji Publication"
    assert synthesized["project"] == "Bhāva"
    assert "scriptural" in synthesized["rights_limitation"].lower()
    assert "used with permission" not in json.dumps(synthesized).lower()

    # Operator artifact_notes / font paths must not leak into public rights.
    dirty = sanitize_public_rights(
        {
            "title": "Aghasura",
            "version": "2.0",
            "rights": {
                "artifact_notes": {
                    "images": {
                        "story_poster.png": {
                            "title_font": r"C:\Windows\Fonts\arialbd.ttf",
                        }
                    }
                },
                "author": "Svarna Gauranga Das",
                "publisher": "Dauji Publication",
                "project": "Bhāva",
            },
        },
        story_no="020",
    )
    dirty_blob = json.dumps(dirty)
    assert "artifact_notes" not in dirty
    assert "Windows" not in dirty_blob
    assert "Fonts" not in dirty_blob
    assert dirty["copyright_owner"] == "Svarna Gauranga Das"

    reader = ensure_reader_rights_section(
        "# Title\n\nBody.\n",
        synthesized,
        story_no="015",
    )
    assert "## Rights and Credits" in reader
    assert "contact_email" not in reader.lower()
    assert "@gmail" not in reader.lower()
    assert "Svarna Gauranga Das" in reader
    assert "Dauji Publication" in reader
    assert "Bhāva" in reader


@pytest.mark.content_release
def test_public_web_manifest_rights_contract(stories_with_assets: list[str]) -> None:
    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        manifest_path = dest / "web_manifest.json"
        if not manifest_path.is_file():
            pytest.skip(f"web_manifest.json missing for {story_no}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        rights = manifest.get("rights")
        assert isinstance(rights, dict) and rights, f"{story_no}: rights must be non-empty"
        assert "contact_email" not in rights, f"{story_no}: contact_email must be omitted"
        blob = json.dumps(rights, ensure_ascii=False)
        for token in REQUIRED_ATTR:
            assert token in blob, f"{story_no}: missing attribution {token!r}"
        assert "used with permission" not in blob.lower()
        assert "contact_email" not in blob.lower()
        assert "@gmail" not in blob.lower()
        assert "Windows\\Fonts" not in blob and "/Fonts/" not in blob
        assert "artifact_notes" not in rights


@pytest.mark.content_release
def test_public_reader_rights_section_contract(stories_with_assets: list[str]) -> None:
    for story_no in stories_with_assets:
        dest = _web_dir(story_no)
        assert dest is not None
        reader_path = dest / "reader.md"
        if not reader_path.is_file():
            pytest.skip(f"reader.md missing for {story_no}")
        reader = reader_path.read_text(encoding="utf-8")
        assert "## Rights and Credits" in reader, f"{story_no}: missing Rights and Credits"
        assert "contact_email" not in reader.lower()
        assert "@gmail" not in reader.lower()
        for token in REQUIRED_ATTR:
            assert token in reader, f"{story_no}: reader missing {token!r}"
