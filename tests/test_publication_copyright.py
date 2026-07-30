"""Publication identity, notices, work-manifest, and sitemap copyright gates."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_central_identity_spelling_and_contact() -> None:
    from krishna_story_factory.publication import get_identity, load_identity

    get_identity.cache_clear()
    ident = load_identity(ROOT)
    assert ident.copyright_owner == "Svarna Gauranga Das"
    assert "Swarna" not in ident.copyright_owner
    assert ident.publisher == "Dauji Publication"
    assert ident.project == "Bhāva"
    assert ident.contact_email == "svarnagaurangdas@gmail.com"
    assert ident.phone is None
    assert ident.location == "Harrisburg, Pennsylvania, USA"
    raw = yaml.safe_load((ROOT / "config" / "publication_identity.yaml").read_text(encoding="utf-8"))
    assert raw.get("phone") is None


def test_no_year_without_reviewed_first_publication() -> None:
    from krishna_story_factory.publication import compact_footer, first_publication_year

    assert first_publication_year({"status": "publicly_available_unreviewed"}) is None
    assert first_publication_year({"status": "published", "first_publication_date": "2026-07-01"}) == 2026
    text = compact_footer(year=None)
    assert "© 20" not in text
    assert "Svarna Gauranga Das" in text
    assert "Dauji Publication" in text


def test_work_manifest_validation_and_sound_recording_gate() -> None:
    from krishna_story_factory.publication import (
        audio_notice_lines,
        build_story_rights_block,
        get_identity,
        validate_work_manifest,
    )

    get_identity.cache_clear()
    ident = get_identity()
    block = build_story_rights_block(
        story_no="001",
        title="Example",
        version="2.1.0-copyright",
        supersedes="2.0",
        source_reference="Krishna Book Chapter 1",
        scripture_reference="test",
        file_sha256={"story.md": "abc"},
        prior_sha256={"story.md": "def"},
        identity=ident,
        ai_assistance={"audio": {"provider": "openai"}},
        human_authorship_claim="human editing",
        sound_recording_claim_status="needs_manual_review",
    )
    assert validate_work_manifest(block) == []
    lines = audio_notice_lines(year=None, sound_recording_claim_status="needs_manual_review")
    assert not any(line.startswith("Sound recording ℗ 20") for line in lines)


def test_sitemap_includes_nine_stories_rights_excludes_010() -> None:
    text = (ROOT / "apps" / "web" / "app" / "sitemap.ts").read_text(encoding="utf-8")
    assert "PUBLIC_STORY_COUNT = 9" in text
    assert '"/rights"' in text
    # The sitemap enumerates an explicit public allow-list, so private surfaces
    # cannot leak by omission from a deny-list.
    for private in ("/studio", "/dev", "/api/studio", "/api/v1/factory"):
        assert private not in text, f"Private route {private} must never be listed in the sitemap"
    assert not re.search(r"/stories/0*(1[0-9]|[1-9]\d\d)", text), "Sitemap must stop at Story 009"


def test_website_footer_and_rights_page_exist() -> None:
    footer = (ROOT / "apps" / "web" / "components" / "site-footer.tsx").read_text(encoding="utf-8")
    assert "© 2026 Svarna Gauranga Das" in footer
    assert "Dauji Publication" in footer
    assert "/rights" in footer
    rights = ROOT / "apps" / "web" / "app" / "rights" / "page.tsx"
    assert rights.is_file()
    body = rights.read_text(encoding="utf-8")
    assert "contact.public_email" in body
    assert "not the same as formal" in body
    assert "Dauji Publication" in body or "contact.publisher" in body


@pytest.mark.content_release
def test_retrofitted_packages_have_rights_and_exact_eight() -> None:
    from krishna_story_factory.package_swap import validate_exact_eight_files

    baseline = json.loads(
        (ROOT / "docs" / "releases" / "BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json").read_text(
            encoding="utf-8"
        )
    )
    for n in range(1, 10):
        folder = next((ROOT / "output").glob(f"{n:03d}_*"))
        assert validate_exact_eight_files(folder) == []
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        # The launch safety baseline is the source of truth for released versions;
        # artifact corrections advance individual stories past 2.1.1-copyright.
        assert manifest.get("version") == baseline["stories"][f"{n:03d}"]["version"]
        rights = manifest.get("rights") or {}
        assert rights.get("copyright_owner") == "Svarna Gauranga Das"
        assert rights.get("publisher") == "Dauji Publication"
        assert rights.get("status") == "publicly_available_unreviewed"
        assert rights.get("sound_recording_claim_status") == "needs_manual_review"
        story = (folder / "story.md").read_text(encoding="utf-8")
        assert "## Rights and Credits" in story
        caption = (folder / "whatsapp_caption.txt").read_text(encoding="utf-8")
        assert "Svarna Gauranga Das" in caption


@pytest.mark.local_archive
def test_retrofit_preserved_superseded_archives() -> None:
    for n in range(1, 10):
        base = ROOT / "output" / "_archive" / "pre-copyright" / f"{n:03d}"
        assert (base / "2.1.0-copyright").is_dir()
        assert (base / "2.0").is_dir()
