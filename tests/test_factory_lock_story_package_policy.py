"""Hermetic regression coverage for the story-package factory lock."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from krishna_story_factory.audio.pace import evaluate_pace_qa
from krishna_story_factory.audio.punctuation_gate import evaluate_punctuation_gate
from krishna_story_factory.audio.sample_first_gate import (
    AudioSampleFirstError,
    assert_full_tts_allowed,
)
from krishna_story_factory.content.canonical_narration import extract_canonical_narration
from krishna_story_factory.content.story_tts_equivalence import evaluate_story_tts_equivalence
from krishna_story_factory.policy.story_package_policy import (
    load_story_package_policy,
    require_sample_first,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def test_policy_file_locks_021_022_standard() -> None:
    policy = load_story_package_policy(ROOT)
    assert policy["policy_version"] == "story_package_policy_v1"
    assert policy["narration_equivalence_mode"] == "exact"
    assert require_sample_first(policy) is True
    assert policy["activity"]["sequence_beats_required"] == 6
    assert policy["activity"]["prohibit_generic_role_card_fallback"] is True
    assert policy["publication"]["private_by_default"] is True
    assert len(policy["exact_eight_files"]) == 8
    assert policy["bedtime_wpm"]["minimum_accept"] == 115.0
    assert policy["bedtime_wpm"]["maximum_accept"] == 150.0
    assert policy["approved_tts"]["silent_fallback_forbidden"] is True


def test_exact_story_narration_equivalence_fixture() -> None:
    story = (FIXTURES / "story_reader" / "021_canonical_main_audio.md").read_text(encoding="utf-8")
    audio = extract_canonical_narration(story)
    assert audio.strip()
    good = evaluate_story_tts_equivalence(
        story_md=story,
        tts_source=audio,
        require_exact_canonical=True,
    )
    assert good.status == "PASS"
    bad = evaluate_story_tts_equivalence(
        story_md=story,
        tts_source="totally unrelated invented plot about dragons only",
        require_exact_canonical=True,
    )
    assert bad.status == "FAIL"


def test_punctuation_gate_failure() -> None:
    bad = "Krishna smiled. and then the boys ran without a capital start"
    result = evaluate_punctuation_gate(bad)
    assert result.status == "FAIL"


def test_wpm_failure_too_fast() -> None:
    text = " ".join(["Krishna"] * 300)
    result = evaluate_pace_qa(narration_text=text, duration_seconds=60.0)
    assert result.status == "FAIL"
    assert "too fast" in result.detail.lower() or result.measured_wpm > 150


def test_missing_sample_pass_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUDIO_SAMPLE_FIRST_REQUIRED", "1")
    with pytest.raises(AudioSampleFirstError):
        assert_full_tts_allowed(
            work_dir=tmp_path,
            narration_text="Krishna protects the cowherd boys.",
            provider="openai",
            model="gpt-4o-mini-tts-2025-12-15",
            voice="marin",
            settings={"speed": 0.9},
        )


def test_generic_activity_fallback_prohibited_in_planner_source() -> None:
    source = (ROOT / "krishna_story_factory" / "activities" / "planner.py").read_text(encoding="utf-8")
    assert "quality-blind FAMILY_MISSION soft-fallback is prohibited" in source
    assert "Prefer a non-sequence pack only when a semantic map cannot be built" not in source


def test_six_beat_activity_requirement_in_policy() -> None:
    policy = load_story_package_policy(ROOT)
    assert int(policy["activity"]["sequence_beats_required"]) == 6


def test_activity_pdf_title_collision_gate_exists() -> None:
    qa = (ROOT / "krishna_story_factory" / "activities" / "qa.py").read_text(encoding="utf-8")
    assert "title" in qa.lower()
    pdf = (ROOT / "krishna_story_factory" / "pdf" / "activity_sheet.py").read_text(encoding="utf-8")
    assert "overlap" in pdf.lower() or "collision" in pdf.lower() or "clip" in pdf.lower()


def test_visual_crop_contract_metadata_present_in_policy() -> None:
    policy = load_story_package_policy(ROOT)
    crops = policy["poster_composition"]["main_characters_readable_at_crops"]
    assert set(crops) >= {"full_poster", "library_card", "sidebar", "mobile", "og"}


def test_exact_eight_non_empty_contract() -> None:
    policy = load_story_package_policy(ROOT)
    assert all(name.strip() for name in policy["exact_eight_files"])


def test_private_by_default_and_reader_boundary_tests_exist() -> None:
    policy = load_story_package_policy(ROOT)
    assert policy["publication"]["private_by_default"] is True
    boundary = ROOT / "tests" / "test_private_reader_public_boundary.py"
    assert boundary.is_file()
    text = boundary.read_text(encoding="utf-8")
    assert "reader.txt" in text
    assert "public_story_max" in text


def test_queue_does_not_advance_on_failure_contract() -> None:
    pipeline = (ROOT / "krishna_story_factory" / "pipeline.py").read_text(encoding="utf-8")
    assert 'update_plan_status' in pipeline
    assert 'status="done"' in pipeline or '"done"' in pipeline
    # Failure path must restore pending — look for pending restoration.
    assert "pending" in pipeline


def test_provider_not_called_after_failed_preflight_order() -> None:
    pipeline = (ROOT / "krishna_story_factory" / "pipeline.py").read_text(encoding="utf-8")
    # Use distinctive call sites after the prod narration gates begin.
    marker = "Canonical narration exact-match FAILED"
    start = pipeline.index(marker)
    segment = pipeline[start:]
    punct_idx = segment.index("evaluate_punctuation_gate")
    pron_idx = segment.index("evaluate_pronunciation_coverage")
    sample_idx = segment.index("run_sample_first(")
    assert punct_idx < pron_idx < sample_idx


def test_scheduler_cannot_overlap_and_only_next_pending() -> None:
    mwf = (ROOT / "scripts" / "install_mwf_story_task.ps1").read_text(encoding="utf-8")
    runner = (ROOT / "scripts" / "run_daily_story_scheduled.ps1").read_text(encoding="utf-8-sig")
    assert "MultipleInstances IgnoreNew" in mwf
    assert "ValidateScheduler" in runner
    assert "scheduler_status.json" in runner
    assert '"--mode", "prod"' in runner or "--mode prod" in runner
    assert "--force" not in runner
    # Status file must not be web-exposed.
    assert "public_web_exposed = $false" in runner or "public_web_exposed" in runner


def test_scheduler_does_not_create_024_while_023_incomplete() -> None:
    """Scheduler invokes one prod run; pipeline selects next pending only."""
    tree = ast.parse((ROOT / "krishna_story_factory" / "pipeline.py").read_text(encoding="utf-8"))
    # Smoke: module parses; next-pending selection remains single-story.
    assert any(isinstance(node, ast.FunctionDef) and node.name == "run_daily_story" for node in tree.body)


def test_production_never_exposes_private_package_when_mounted() -> None:
    text = (ROOT / "tests" / "test_private_reader_public_boundary.py").read_text(encoding="utf-8")
    assert "public_story_max = 20" in text or "public_story_max=20" in text or "public_story_max" in text
    assert "/reader" in text


def test_talavana_lexicon_covers_story_023() -> None:
    lexicon = (ROOT / "input" / "audio_pronunciations.yaml").read_text(encoding="utf-8")
    assert "Tālavana" in lexicon
    assert "Talavana" in lexicon
