"""Hermetic pronunciation lexicon coverage for dhotī / Stories 024–025."""
from __future__ import annotations

import unicodedata
from pathlib import Path

from krishna_story_factory.audio.pronunciation import load_pronunciation_aliases, normalize_for_tts
from krishna_story_factory.audio.pronunciation_coverage import evaluate_pronunciation_coverage

ROOT = Path(__file__).resolve().parents[1]

# Synthetic excerpts only — never depend on work/**, output/**, Drive, or local DBs.
STORY_024_SYNTHETIC = (
    "Morning came softly in Vṛndāvana. Kṛṣṇa stood up, His yellow dhotī shining, "
    "and strode to the edge of the Yamunā where Kāliya waited."
)
STORY_025_SYNTHETIC = (
    "In Vṛndāvana, Kṛṣṇa and Balarāma walked with the gopas when a forest fire rose. "
    "Tall tamāla trees stood near Yamunā; Madhumaṅgala cried out after Kālīya was calmed."
)


def test_dhoti_lexicon_entries_present() -> None:
    lexicon = (ROOT / "input" / "audio_pronunciations.yaml").read_text(encoding="utf-8")
    for key in ("dhotī", "dhoti", "Kālīya", "tamāla", "Madhumaṅgala"):
        assert key in lexicon
    aliases = load_pronunciation_aliases(ROOT)
    assert aliases["dhotī"] == "dhoti"
    assert aliases["dhoti"] == "dhoti"
    assert aliases["Kālīya"] == "Kaliya"
    assert aliases["tamāla"] == "tamala"
    assert aliases["Madhumaṅgala"] == "Madhumangala"


def test_dhoti_nfc_nfd_and_ascii_resolve_for_tts() -> None:
    nfc = unicodedata.normalize("NFC", "dhotī")
    nfd = unicodedata.normalize("NFD", "dhotī")
    assert nfc != nfd
    for form in (nfc, nfd, "dhoti", "yellow dhotī cloth", "yellow dhoti cloth"):
        result = normalize_for_tts(form, project_root=ROOT)
        assert "dhoti" in result.audio_text.lower()
        assert "dhotī" not in result.audio_text
        assert "\u0304" not in result.audio_text


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


def _contains_dhoti_term(text: str) -> bool:
    """True if text has dhoti/dhotī in any case; .lower() alone is not enough for DHOTĪ."""
    folded = text.casefold()
    return "dhotī" in folded or "dhoti" in folded


def test_story_024_synthetic_excerpt_passes_pronunciation_preflight() -> None:
    # Hermetic: never read work/** or gitignored output/** for this preflight.
    assert _contains_dhoti_term(STORY_024_SYNTHETIC)
    assert _contains_dhoti_term("His yellow DHOTĪ shining")
    report = evaluate_pronunciation_coverage(STORY_024_SYNTHETIC, project_root=ROOT)
    assert report.status == "PASS", report.notes
    assert not report.missing
    upper = evaluate_pronunciation_coverage(
        "Kṛṣṇa stood up, His yellow DHOTĪ shining by the Yamunā.",
        project_root=ROOT,
    )
    assert upper.status == "PASS", upper.notes


def test_story_025_synthetic_excerpt_passes_pronunciation_preflight() -> None:
    for term in ("tamāla", "Madhumaṅgala", "Kālīya"):
        assert term in STORY_025_SYNTHETIC
    report = evaluate_pronunciation_coverage(STORY_025_SYNTHETIC, project_root=ROOT)
    assert report.status == "PASS", report.notes
    assert not report.missing
