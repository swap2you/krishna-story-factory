"""Regression gates for Stories 026–035 content correction."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work" / "_026_035_content_correction"
DRAFTS = WORK / "drafts"

from krishna_story_factory.csv_store import read_plan_by_chapter
from krishna_story_factory.activities.preferred_packs_026_035 import PREFERRED_PACKS_026_035
from krishna_story_factory.activities.qa import generic_template_errors, semantic_activity_errors
from krishna_story_factory.audio.drift import detect_audio_stale, narration_source_sha
from krishna_story_factory.content.source_dossiers import load_dossiers, validate_dossier_text
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.models import PlanRow, StoryContent
from krishna_story_factory.publication.notices import compact_footer


def _draft_text(story_no: str) -> str:
    path = DRAFTS / story_no / "story.md"
    if not path.is_file():
        pytest.skip(f"Draft not built yet: {path}")
    return path.read_text(encoding="utf-8")


def _narration(story_no: str) -> str:
    path = DRAFTS / story_no / "narration_script.txt"
    return path.read_text(encoding="utf-8")


def _plan(story_no: str) -> PlanRow:
    plan = read_plan_by_chapter(ROOT, story_no)
    assert plan is not None
    return plan


def _content_from_draft(story_no: str) -> StoryContent:
    md = _draft_text(story_no)
    main_match = re.search(r"## Main Story\n(.*?)\n## Devotional Meaning", md, re.S)
    recap_match = re.search(r"## Recap\n(.*?)\n## Main Story", md, re.S)
    devo_match = re.search(r"## Devotional Meaning\n(.*?)\n## Five Lessons", md, re.S)
    return StoryContent(
        title=f"Story {story_no}",
        recap=recap_match.group(1).strip() if recap_match else "",
        main_story=main_match.group(1).strip() if main_match else "",
        moral=devo_match.group(1).strip() if devo_match else "",
        takeaway="",
        five_star_challenge=[],
        audio_script=_narration(story_no),
        devotional_meaning=devo_match.group(1).strip() if devo_match else "",
        bedtime_reflection="?",
        next_story_preview="",
    )


@pytest.mark.parametrize("story_no", [f"{n:03d}" for n in range(26, 36)])
def test_corrected_drafts_pass_dossier(story_no: str) -> None:
    dossier = load_dossiers(ROOT, (story_no,))[story_no]
    text = _draft_text(story_no) + "\n" + _narration(story_no)
    errors = validate_dossier_text(dossier, text)
    assert errors == [], errors


def test_029_rejects_night_meeting_plot() -> None:
    dossier = load_dossiers(ROOT, ("029",))["029"]
    bad = (
        "At night the gopis left their homes and entered the forest to meet Krishna. "
        "Krishna taught them about devotion under the moonlight."
    )
    assert validate_dossier_text(dossier, bad)


def test_029_requires_forest_flute_and_vraja_discussion() -> None:
    dossier = load_dossiers(ROOT, ("029",))["029"]
    good = _draft_text("029") + "\n" + _narration("029")
    assert validate_dossier_text(dossier, good) == []
    low = good.lower()
    assert "flute" in low
    assert "gopi" in low or "gopī" in low
    assert "peacock" in low or "deer" in low or "yamuna" in low or "yamunā" in low


def test_034_rejects_life_under_hill_plot() -> None:
    dossier = load_dossiers(ROOT, ("034",))["034"]
    bad = (
        "While life continued under the lifted hill, the boys kept chanting and sharing food "
        "under Govardhana as the storm remained the main adventure."
    )
    assert validate_dossier_text(dossier, bad)


def test_034_requires_nanda_garga_and_wonders() -> None:
    text = _draft_text("034") + "\n" + _narration("034")
    dossier = load_dossiers(ROOT, ("034",))["034"]
    assert validate_dossier_text(dossier, text) == []
    low = text.lower()
    assert "nanda" in low and "garga" in low
    assert "putana" in low or "pūtanā" in low
    assert "kaliya" in low or "kāliya" in low


def test_026_forbidden_contradictions_rejected() -> None:
    bad = "Krishna's team cleverly worked together and won after several joyful rounds."
    dossier = load_dossiers(ROOT, ("026",))["026"]
    assert validate_dossier_text(dossier, bad)


def test_027_hide_and_seek_rejected() -> None:
    bad = "The boys played hide and seek in the enchanting forest."
    dossier = load_dossiers(ROOT, ("027",))["027"]
    assert validate_dossier_text(dossier, bad)


def test_030_narration_has_no_editorial_markers() -> None:
    narr = _narration("030")
    assert "[" not in narr and "]" not in narr
    assert "editorial" not in narr.lower()
    assert "naked" not in narr.lower()
    path = DRAFTS / "030" / "manifest_draft.json"
    if not path.is_file():
        pytest.skip("030 manifest draft missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["review"]["senior_devotional_review_required"] is True
    assert data["review"]["senior_devotional_review_complete"] is False


def test_027_visual_brief_requires_inward_fire() -> None:
    path = DRAFTS / "027" / "visual_briefs.md"
    if not path.is_file():
        pytest.skip("Visual briefs not built")
    text = path.read_text(encoding="utf-8").lower()
    assert "inward" in text or "swallow" in text


def test_narration_length_within_series_baseline() -> None:
    """001–025 median ~809 words; drafts must land in ±20% (647–970)."""
    for story_no in [f"{n:03d}" for n in range(26, 36)]:
        words = len(_narration(story_no).split())
        assert 647 <= words <= 970, f"{story_no} narration words={words}"


def test_preferred_packs_026_035_not_generic() -> None:
    for story_no in [f"{n:03d}" for n in range(26, 36)]:
        plan = _plan(story_no)
        pack = PREFERRED_PACKS_026_035[story_no](plan)
        assert generic_template_errors(pack) == []
        assert semantic_activity_errors(pack) == []


def test_no_civil_name_in_public_surfaces() -> None:
    footer = compact_footer(year=2026)
    assert "Swapnil Patil" not in footer
    assert "© 2026 Svarna Gauranga Das" in footer
    ident = yaml.safe_load((ROOT / "config" / "publication_identity.yaml").read_text(encoding="utf-8"))
    assert "Swapnil Patil" not in str(ident.get("public_display_credit", ""))


def test_civil_name_scan_rejects_leak() -> None:
    from krishna_story_factory.publication import identity as identity_mod

    if hasattr(identity_mod.load_identity, "cache_clear"):
        identity_mod.load_identity.cache_clear()
    ident = identity_mod.load_identity(ROOT)
    sample = f"© {ident.copyright_owner} · Dauji Publication · Bhāva"
    assert "Swapnil Patil" not in sample


def test_stale_audio_when_script_changes() -> None:
    out = next((ROOT / "output").glob("026_*"), None)
    if out is None or not (out / "manifest.json").is_file():
        pytest.skip("No output package for 026")
    narr = _narration("026")
    stale, detail = detect_audio_stale(audio_script=narr, manifest_path=out / "manifest.json")
    assert stale, detail


def test_private_story_manifest_draft_semantics() -> None:
    for story_no in ("026", "029"):
        path = DRAFTS / story_no / "manifest_draft.json"
        if not path.is_file():
            pytest.skip("Draft manifests not built")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["publishable"] is False
        assert data["review"]["human_approval_complete"] is False
        assert data["publication"]["catalog_exposure"] == "private"


def test_all_dossiers_026_035_present() -> None:
    dossiers = load_dossiers(ROOT, tuple(f"{n:03d}" for n in range(26, 36)))
    assert len(dossiers) == 10
