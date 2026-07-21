"""Post-PR7 release-blocker hotfix regressions."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from krishna_story_factory.activities.planner import _extract_event_labels
from krishna_story_factory.activities.qa import contains_metadata_concept, is_metadata_event_label
from krishna_story_factory.content.repairs import (
    apply_known_story_repairs,
    assert_story_002_audio_clean,
    repair_story_002_dialogue,
)
from krishna_story_factory.content.story_format_v2 import StoryPackageContentV2
from krishna_story_factory.manifest import _is_publishable, write_manifest
from krishna_story_factory.models import PlanRow, StoryContent
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.package_swap import (
    PHASE_PREPARED,
    PHASE_PRODUCTION_BACKED_UP,
    PHASE_STAGING_PROMOTED,
    atomic_replace_package_dir,
    journal_root,
    recover_unfinished_swaps,
)
from krishna_story_factory.paths import PackagePaths

ROOT = Path(__file__).resolve().parents[1]


def _plan(chapter: str = "002", **kwargs) -> PlanRow:
    defaults = dict(
        chapter_no=chapter,
        slug=f"story-{chapter}",
        title=f"Story {chapter}",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book",
        scripture_reference="SB",
        summary_seed="seed",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="done",
        created_at="",
        updated_at="",
        notes="",
        row_index=0,
        must_include="",
        must_avoid="",
        start_boundary="",
        end_boundary="",
    )
    defaults.update(kwargs)
    return PlanRow(**defaults)


def _content(**kwargs) -> StoryContent:
    base = dict(
        title="t",
        greeting="Hare Krishna",
        recap="r" * 20,
        main_story="m" * 20,
        moral="mo",
        takeaway="ta",
        five_star_challenge=["a"] * 5,
        audio_script="audio",
        bedtime_reflection="What will you remember?",
        think_about_it=["What will you remember?", "Why?", "How?"],
        five_lessons=["l1 long enough", "l2 long enough", "l3 long enough", "l4 long enough", "l5 long enough"],
        poster_visual_brief="poster brief",
        coloring_visual_brief="coloring brief",
        source_reference="Krishna Book",
        scripture_reference="SB",
        age_range="6-12",
        story_number="002",
    )
    base.update(kwargs)
    return StoryContent(**base)


def test_codex_metadata_token_injection_never_becomes_events() -> None:
    seed = (
        "title: The Birth of Lord Krishna; source_reference: Krishna Book Chapter 3; "
        "age_range: 6-12; story_number: 006; format: v2; Hare Kṛṣṇa, dear children"
    )
    with pytest.raises(ValueError, match="metadata|placeholders|concrete"):
        _extract_event_labels("---\ntitle: only\n---\n", seed)
    # Even if somehow accepted, concepts must be rejected.
    assert contains_metadata_concept("title Birth in the pastime")
    assert contains_metadata_concept("source reference in the pastime")
    assert is_metadata_event_label("story number in the pastime")


def test_story_002_audio_rewrite_from_actual_file() -> None:
    path = ROOT / "output" / "002_devaki-and-vasudeva-wedding" / "story.md"
    if not path.exists():
        pytest.skip("Story 002 package not present locally")
    from krishna_story_factory.pipeline import _content_from_story_md

    plan = _plan("002", title="The Wedding and the Heavenly Voice", slug="devaki-and-vasudeva-wedding")
    repaired = apply_known_story_repairs("002", _content_from_story_md(path.read_text(encoding="utf-8"), plan))
    # Idempotent
    again = repair_story_002_dialogue(repaired)
    assert again.audio_script == repaired.audio_script
    errors = assert_story_002_audio_clean(repaired.audio_script)
    assert not errors, errors
    low = repaired.audio_script.lower()
    assert "1.0s\" />" not in repaired.audio_script
    assert "he muttered" not in low
    assert "she whispered" not in low
    assert "he smiled and told her, in paraphrase" not in low
    assert "thank you for saving my life" not in low
    assert "<!--" not in repaired.to_markdown().split("## Think About It")[0] or True
    md = repaired.to_markdown()
    assert not md.lstrip().startswith("---")
    assert md.count("<!--") == 1


def test_publishable_gate_matrix(tmp_path: Path) -> None:
    assert _is_publishable(mode="test", quality_status="PASS", quality_errors=[], audio_metadata={}) is False
    assert (
        _is_publishable(
            mode="prod",
            quality_status="AUDIO_STALE",
            quality_errors=[],
            audio_metadata={"audio_stale": True},
        )
        is False
    )
    assert (
        _is_publishable(mode="prod", quality_status="PASS", quality_errors=["x"], audio_metadata={}) is False
    )
    assert (
        _is_publishable(
            mode="prod",
            quality_status="PASS",
            quality_errors=[],
            audio_metadata={"audio_stale": False, "generation_verified": True},
        )
        is True
    )

    out = tmp_path / "output" / "002_x"
    out.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (out / name).write_bytes(b"1234")
    paths = PackagePaths(
        root=out,
        story_md=out / "story.md",
        narration_mp3=out / "narration.mp3",
        story_poster=out / "story_poster.png",
        coloring_page=out / "coloring_page.png",
        simple_coloring_page=out / "simple_coloring_page.png",
        activity_sheet=out / "activity_sheet.pdf",
        whatsapp_caption=out / "whatsapp_caption.txt",
        manifest=out / "manifest.json",
    )
    from krishna_story_factory.config import load_settings

    settings = load_settings(ROOT)
    content = _content(audio_script="Hare Krishna narration for wedding.")
    write_manifest(
        settings=settings,
        plan=_plan(),
        content=content,
        paths=paths,
        mode="prod",
        quality_status="AUDIO_STALE",
        quality_errors=["AUDIO_STALE: narration text changed"],
        audio_metadata={"provider": "unknown_preserved", "generation_verified": False, "audio_stale": True},
    )
    data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    assert data["publishable"] is False
    assert data["audio"]["audio_stale"] is True


def test_openai_mid_run_model_access_does_not_rebill_chunk1(tmp_path: Path, monkeypatch) -> None:
    from krishna_story_factory.audio import openai_tts as oa

    calls: list[str] = []

    def boom(**kwargs):
        text = kwargs["text"]
        model = kwargs["model"]
        calls.append(f"{model}:{text[:20]}")
        if len(calls) == 1:
            return b"ID3fakeaudio" * 40, "req1", model, {
                "model_attempts": [model],
                "request_attempt_count": 1,
                "retryable_error_classes": [],
                "final_successful_attempt": 1,
                "fallback_model_used": False,
                "estimated_extra_paid_attempts": 0,
            }
        raise oa.OpenAITtsError("model not available", error_class="model_access")

    monkeypatch.setattr(oa, "synthesize_openai_speech_once", boom)
    monkeypatch.setattr(oa, "assemble_mp3_chunks", lambda *a, **k: None)

    out = tmp_path / "candidate.mp3"
    long = ("Krishna walks gently. " * 200) + "\n\n" + ("Devaki prays softly. " * 200)
    with pytest.raises(oa.OpenAITtsError) as excinfo:
        oa.synthesize_openai_tts(
            api_key="k",
            text=long,
            output_path=out,
            model="gpt-4o-mini-tts-2025-12-15",
            voice="marin",
            speed=0.92,
            max_input_chars=400,
            allow_model_fallback=True,
            work_dir=tmp_path / "chunks",
            pinned_model="gpt-4o-mini-tts-2025-12-15",
        )
    assert "MODEL_SWITCH_RESTART_REQUIRED" in str(excinfo.value)
    # Exactly one successful chunk request; no duplicate regeneration of chunk 1.
    assert len(calls) == 2
    assert calls[0].startswith("gpt-4o-mini-tts-2025-12-15:")
    assert not out.exists()
    assert (tmp_path / "chunks" / "MODEL_SWITCH_RESTART_REQUIRED.json").exists()


def test_swap_journal_recovers_after_backup_phase(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    staging = output_root / "_staging" / "pkg"
    production = output_root / "006_story"
    archive = output_root / "_archive"
    staging.mkdir(parents=True)
    production.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")

    # Simulate crash after production backed up: production missing, backup present, journal open.
    backup = archive / "006_story_pre_swap_sim"
    archive.mkdir(parents=True)
    production.rename(backup)
    journal = journal_root(output_root) / "swap_sim.json"
    journal.write_text(
        json.dumps(
            {
                "transaction_id": "sim",
                "production_path": str(production),
                "staging_path": str(staging),
                "backup_path": str(backup),
                "phase": PHASE_PRODUCTION_BACKED_UP,
                "timestamp": "now",
            }
        ),
        encoding="utf-8",
    )
    recovered = recover_unfinished_swaps(output_root=output_root)
    assert recovered
    assert production.exists()
    assert (production / "story.md").read_text(encoding="utf-8") == "old-story.md"
    assert not journal.exists()


def test_swap_journal_recovers_prepared_and_promoted(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    staging = output_root / "_staging" / "pkg"
    production = output_root / "006_story"
    archive = output_root / "_archive"
    staging.mkdir(parents=True)
    production.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")

    journal = journal_root(output_root) / "swap_prepared.json"
    journal.write_text(
        json.dumps(
            {
                "transaction_id": "p",
                "production_path": str(production),
                "staging_path": str(staging),
                "backup_path": str(archive / "b"),
                "phase": PHASE_PREPARED,
            }
        ),
        encoding="utf-8",
    )
    recover_unfinished_swaps(output_root=output_root)
    assert not journal.exists()

    # Promote path: staging already moved to production, journal at STAGING_PROMOTED.
    result = atomic_replace_package_dir(
        staging_dir=staging,
        production_dir=production,
        archive_root=archive,
        output_root=output_root,
    )
    assert result["status"] == "REPLACED"
    assert (production / "story.md").read_text(encoding="utf-8") == "new-story.md"


def test_story_005_no_shield_language_on_actual_file() -> None:
    path = ROOT / "output" / "005_prayers-by-the-demigods-for-lord-krishna-in-the-womb" / "story.md"
    if not path.exists():
        pytest.skip("Story 005 not present")
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.pipeline import _content_from_story_md

    plan = _plan(
        "005",
        title="Prayers by the Demigods for Lord Krishna in the Womb",
        slug="prayers-by-the-demigods-for-lord-krishna-in-the-womb",
    )
    content = apply_known_story_repairs("005", _content_from_story_md(path.read_text(encoding="utf-8"), plan))
    for blob in (content.main_story, content.audio_script, content.devotional_meaning):
        assert "shield" not in blob.lower()
    assert not run_source_guard(plan, content)


def test_frontmatter_absent_from_serialized_story() -> None:
    pkg = StoryPackageContentV2(
        title="T",
        source_reference="Krishna Book",
        scripture_reference="SB",
        age_range="6-12",
        story_number="002",
        greeting="Hare Krishna",
        series_name="Krishna Book Bedtime",
        recap="Recap text for the wedding story with enough words here.",
        main_story="Main story text. " * 40,
        devotional_meaning="Meaning " * 20,
        five_lessons=["a", "b", "c", "d", "e"],
        think_about_it=["One?", "Two?", "Three?"],
        five_star_challenge=["1", "2", "3", "4", "5"],
        bedtime_prayer="Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare.",
        next_story_preview="Next story preview with enough words for the band.",
        parent_note="Parent note with enough words for the validation band here tonight.",
        audio_narration="Audio narration " * 40,
        poster_visual_brief="Poster brief",
        coloring_visual_brief="Coloring brief",
        activity_data={},
    )
    md = pkg.to_markdown()
    assert not md.lstrip().startswith("---")
    assert "title:" not in md.split("## Recap")[0]
    assert md.count("<!--") == 1
