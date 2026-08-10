"""Pronunciation lexicon coverage for dhotī / Story 024–025 preflight."""
from __future__ import annotations

import unicodedata
from pathlib import Path

from krishna_story_factory.audio.pronunciation import load_pronunciation_aliases, normalize_for_tts
from krishna_story_factory.audio.pronunciation_coverage import evaluate_pronunciation_coverage

ROOT = Path(__file__).resolve().parents[1]


def test_dhoti_lexicon_entries_present() -> None:
    lexicon = (ROOT / "input" / "audio_pronunciations.yaml").read_text(encoding="utf-8")
    assert "dhotī" in lexicon
    assert "dhoti" in lexicon
    aliases = load_pronunciation_aliases(ROOT)
    assert aliases["dhotī"] == "dhoti"
    assert aliases["dhoti"] == "dhoti"


def test_dhoti_unicode_and_ascii_resolve_for_tts() -> None:
    nfc = unicodedata.normalize("NFC", "dhotī")
    nfd = unicodedata.normalize("NFD", "dhotī")
    for form in (nfc, "dhoti", "yellow dhotī cloth", "yellow dhoti cloth"):
        result = normalize_for_tts(form, project_root=ROOT)
        assert "dhoti" in result.audio_text.lower()
        assert "dhotī" not in result.audio_text
    # NFD display form still folds via alias or diacritic fold to ASCII audio.
    folded = normalize_for_tts(nfd, project_root=ROOT)
    assert "dhoti" in folded.audio_text.lower()


def test_dhoti_coverage_pass_and_unknown_still_fails() -> None:
    covered = evaluate_pronunciation_coverage(
        "Krishna wore a yellow dhotī beside Kāliya.",
        project_root=ROOT,
    )
    assert covered.status == "PASS"
    assert any(t.lower().startswith("dhot") for t in covered.covered)

    missing = evaluate_pronunciation_coverage(
        "A brand-new missing name Xȳzqŵ appears here.",
        project_root=ROOT,
    )
    assert missing.status == "FAIL"
    assert missing.missing


def test_story_024_and_025_plan_rows_exist_for_preflight() -> None:
    from krishna_story_factory.csv_store import read_plan_by_chapter

    plan_024 = read_plan_by_chapter(ROOT, "024")
    plan_025 = read_plan_by_chapter(ROOT, "025")
    assert plan_024 is not None and plan_024.slug == "subduing-kaliya"
    assert plan_025 is not None and plan_025.slug == "extinguishing-the-forest-fire"


def test_story_024_locked_draft_passes_pronunciation_preflight() -> None:
    """Story 024 text must pass coverage after the dhotī lexicon fix."""
    candidates = sorted((ROOT / "work" / "stories" / "024").glob("*/package/story.md"))
    if not candidates:
        published = ROOT / "output" / "024_subduing-kaliya" / "story.md"
        assert published.is_file(), "expected Story 024 recovery or published story.md for preflight"
        text = published.read_text(encoding="utf-8")
    else:
        text = candidates[-1].read_text(encoding="utf-8")
    report = evaluate_pronunciation_coverage(text, project_root=ROOT)
    assert report.status == "PASS", report.notes
    assert not report.missing
    assert "dhotī" in text or "dhoti" in text.lower()


def test_story_025_pregeneration_guard_expected_chapter_terms() -> None:
    """Chapter 17 forest-fire episode terms must resolve before paid production."""
    sample = (
        "In Vṛndāvana, Kṛṣṇa and Balarāma walked with the gopas when a forest fire rose. "
        "Tall tamāla trees stood near Yamunā; Madhumaṅgala cried out after Kālīya was calmed."
    )
    report = evaluate_pronunciation_coverage(sample, project_root=ROOT)
    assert report.status == "PASS", report.notes
    assert not report.missing


def test_story_025_preflight_draft_passes_when_present() -> None:
    draft = ROOT / "work" / "_evidence" / "preflight_025_20260810" / "story_draft.md"
    if not draft.is_file():
        return
    report = evaluate_pronunciation_coverage(draft.read_text(encoding="utf-8"), project_root=ROOT)
    assert report.status == "PASS", report.notes
    assert not report.missing
