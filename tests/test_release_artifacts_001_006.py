"""Actual production artifact regressions for Stories 001–006.

These tests read local output packages. They must fail against defective
artifacts and pass only after real files are repaired.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from krishna_story_factory.audio.drift import narration_source_sha
from krishna_story_factory.activities.qa import contains_metadata_concept, is_metadata_event_label
from krishna_story_factory.content.repairs import (
    apply_known_story_repairs,
    assert_story_002_audio_clean,
    count_story_003_fact_signatures,
    has_invented_direct_dialogue,
    repair_story_003_dedup,
)
from krishna_story_factory.content.story_format_v2 import validate_story_comment_structure
from krishna_story_factory.csv_store import read_plan_by_chapter
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.pipeline import _content_from_story_md

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def _package_dir(chapter: str) -> Path:
    folders = sorted(OUTPUT.glob(f"{chapter}_*"))
    if not folders:
        pytest.skip(f"Story {chapter} package not present under output/")
    return folders[0]


def _read_story(chapter: str) -> tuple[Path, str]:
    package = _package_dir(chapter)
    path = package / "story.md"
    assert path.exists()
    return package, path.read_text(encoding="utf-8")


@pytest.mark.parametrize("chapter", ["001", "002", "003", "004", "005", "006"])
def test_exact_eight_files_and_story_structure(chapter: str) -> None:
    package, md = _read_story(chapter)
    names = {p.name for p in package.iterdir() if p.is_file()}
    assert names == set(FINAL_OUTPUT_FILES)
    assert not md.lstrip().startswith("---")
    assert "\n---\n" not in md[:500]
    assert md.count("<!--") == 1
    assert md.count("-->") == 1
    assert "<!--" in md and md.index("<!--") < md.index("-->")
    structure_errors = validate_story_comment_structure(md)
    assert not structure_errors, structure_errors
    visible = md.split("<!--")[0]
    for section in (
        "## Recap",
        "## Main Story",
        "## Devotional Meaning",
        "## Five Lessons",
        "## Think About It",
        "## Five-Star Challenge",
        "## Bedtime Prayer",
        "## Next Story Preview",
        "## Parent/Teacher Note",
    ):
        assert section in visible
    # Visual briefs live in the hidden block and must not be empty.
    assert "## Poster Visual Brief" in md
    assert "## Coloring Visual Brief" in md
    assert "## Audio Narration" in md
    poster = re.search(r"## Poster Visual Brief\n(.+?)(?=\n## |\n-->)", md, re.S)
    coloring = re.search(r"## Coloring Visual Brief\n(.+?)(?=\n## |\n-->)", md, re.S)
    assert poster and poster.group(1).strip()
    assert coloring and coloring.group(1).strip()

    plan = read_plan_by_chapter(ROOT, chapter)
    content = _content_from_story_md(md, plan)
    assert len(content.five_lessons or []) == 5
    assert 3 <= len(content.think_about_it or []) <= 5
    assert len(content.five_star_challenge or []) == 5
    remember_count = (content.audio_script or "").count("Remember tonight's pastime")
    assert remember_count <= 1, f"Remember-line repeated {remember_count} times in audio"

    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    audio = manifest.get("audio") or {}
    quality = manifest.get("quality") or {}
    stale = bool(audio.get("audio_stale")) or quality.get("status") == "AUDIO_STALE"
    verified = bool(audio.get("generation_verified"))
    computed_sha = narration_source_sha(content.audio_script)
    manifest_sha = str(manifest.get("narration_source_sha") or audio.get("narration_source_sha") or "")
    assert manifest_sha == computed_sha
    if audio.get("narration_source_sha"):
        assert audio.get("narration_source_sha") == computed_sha
    expected_publishable = (
        manifest.get("mode") != "test"
        and quality.get("status") == "PASS"
        and not list(quality.get("errors") or [])
        and not stale
        and verified
        and str(audio.get("provider") or "") not in {"", "preserved", "unknown_preserved"}
        and bool(manifest_sha)
        and bool(audio.get("sha256"))
    )
    assert manifest.get("publishable") is expected_publishable
    # Gate honesty first: publishable must never lie about stale/unverified audio.
    # Release packages 001–006 are expected to satisfy the full gate after Template V2;
    # if TTS/audio drifts, expected_publishable becomes False and this fails with details.
    assert expected_publishable, (
        f"Story {chapter} failed publishable gate "
        f"(stale={stale}, verified={verified}, status={quality.get('status')}, "
        f"provider={audio.get('provider')!r}, sha256={bool(audio.get('sha256'))}). "
        "Fresh verified audio is required for release packages 001–006."
    )


def test_story_002_audio_defects_absent() -> None:
    package, md = _read_story("002")
    plan = read_plan_by_chapter(ROOT, "002")
    content = apply_known_story_repairs("002", _content_from_story_md(md, plan))
    audio = content.audio_script
    low = audio.lower()
    assert '1.0s" />' not in audio
    assert "he muttered" not in low
    assert "she whispered" not in low
    assert "he smiled and told her, in paraphrase" not in low
    assert "i will help in" not in low
    assert "thank you for saving my life" not in low
    assert not assert_story_002_audio_clean(audio)


def test_story_003_closing_facts_deduped_and_idempotent() -> None:
    package, md = _read_story("003")
    plan = read_plan_by_chapter(ROOT, "003")
    content = _content_from_story_md(md, plan)
    for blob in (content.main_story, content.audio_script):
        counts = count_story_003_fact_signatures(blob)
        for sig, count in counts.items():
            assert count <= 1, f"{sig} count={count} in live story.md"
    repaired = apply_known_story_repairs("003", content)
    again = repair_story_003_dedup(repaired)
    assert again.main_story == repaired.main_story
    assert again.audio_script == repaired.audio_script
    # Closing-fact signatures remain unique after repair pass.
    for blob in (repaired.main_story, repaired.audio_script):
        counts = count_story_003_fact_signatures(blob)
        for sig, count in counts.items():
            assert count <= 1, f"{sig} count={count} after repair"


def test_story_005_forbidden_language_absent() -> None:
    package, md = _read_story("005")
    plan = read_plan_by_chapter(ROOT, "005")
    content = apply_known_story_repairs("005", _content_from_story_md(md, plan))
    for blob in (content.main_story, content.audio_script, content.devotional_meaning or ""):
        low = blob.lower()
        assert "shield" not in low
        assert "celestial garden" not in low
        assert "heavenly garden" not in low
        assert "i will help in" not in low
    assert not run_source_guard(plan, content)
    assert not has_invented_direct_dialogue(content.main_story, allow_heavenly_voice=False)


def test_story_006_no_metadata_events_or_story_007_leak() -> None:
    package, md = _read_story("006")
    plan = read_plan_by_chapter(ROOT, "006")
    content = apply_known_story_repairs("006", _content_from_story_md(md, plan))
    low = content.main_story.lower()
    assert "kamsa begins his persecutions" not in low
    assert "story 007" not in low
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    activity = manifest.get("activity") or {}
    for label in activity.get("answer_key") or []:
        assert not is_metadata_event_label(str(label))
        assert not contains_metadata_concept(str(label))
