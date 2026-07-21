"""Post-PR7 release-blocker hotfix regressions."""
from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import MagicMock

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
    STATUS_INVALID_SWAP_JOURNAL,
    InvalidSwapJournalError,
    atomic_replace_package_dir,
    journal_root,
    parse_and_validate_journal,
    quarantine_root,
    recover_unfinished_swaps,
)
from krishna_story_factory.paths import PackagePaths
import krishna_story_factory.package_swap as package_swap_mod

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
    md = repaired.to_markdown()
    _assert_distributed_story_md_has_no_yaml_frontmatter(md)


def test_publishable_gate_matrix(tmp_path: Path) -> None:
    assert _is_publishable(mode="test", quality_status="PASS", quality_errors=[], audio_metadata={}) is False
    assert (
        _is_publishable(
            mode="prod",
            quality_status="AUDIO_STALE",
            quality_errors=[],
            audio_metadata={"audio_stale": True, "generation_verified": True, "provider": "openai", "sha256": "ABC"},
            narration_source_sha="DEAD",
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
            audio_metadata={"audio_stale": False, "generation_verified": False, "provider": "openai", "sha256": "ABC"},
            narration_source_sha="DEAD",
        )
        is False
    )
    assert (
        _is_publishable(
            mode="prod",
            quality_status="PASS",
            quality_errors=[],
            audio_metadata={"audio_stale": False, "provider": "openai", "sha256": "ABC"},
            narration_source_sha="DEAD",
        )
        is False
    ), "missing generation_verified must be false"
    assert (
        _is_publishable(
            mode="prod",
            quality_status="PASS",
            quality_errors=[],
            audio_metadata={
                "audio_stale": False,
                "generation_verified": True,
                "provider": "unknown_preserved",
                "sha256": "ABC",
            },
            narration_source_sha="DEAD",
        )
        is False
    )
    out = tmp_path / "output" / "002_x"
    out.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (out / name).write_bytes(b"1234")
    assert (
        _is_publishable(
            mode="prod",
            quality_status="PASS",
            quality_errors=[],
            audio_metadata={
                "audio_stale": False,
                "generation_verified": True,
                "provider": "openai",
                "sha256": "ABC123",
            },
            narration_source_sha="DEADBEEF",
            package_dir=out,
        )
        is True
    )

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


def test_actual_manifests_001_006_not_publishable_while_stale() -> None:
    for chapter in ("001", "002", "003", "004", "005", "006"):
        folders = list((ROOT / "output").glob(f"{chapter}_*"))
        if not folders:
            pytest.skip(f"Story {chapter} package missing locally")
        data = json.loads((folders[0] / "manifest.json").read_text(encoding="utf-8"))
        audio = data.get("audio") or {}
        assert data.get("publishable") is False
        assert audio.get("audio_stale") is True or data.get("quality", {}).get("status") == "AUDIO_STALE"
        assert not audio.get("generation_verified")


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


def _assert_distributed_story_md_has_no_yaml_frontmatter(md: str) -> None:
    """Distributed story.md must not expose YAML metadata; keep parent sections visible."""
    stripped = md.lstrip()
    assert not stripped.startswith("---"), "distributed story.md must not start with YAML ---"
    assert "\n---\n" not in md[:400], "distributed story.md must not contain a leading YAML fence"

    visible, sep, hidden = md.partition("<!--")
    assert sep == "<!--", "exactly one hidden production comment block is required"
    assert "-->" in hidden
    assert hidden.count("<!--") == 0
    assert md.count("<!--") == 1
    assert md.count("-->") == 1

    # No visible YAML-style metadata keys before the hidden block.
    for key in (
        "title:",
        "source_reference:",
        "scripture_reference:",
        "age_range:",
        "story_number:",
        "format:",
    ):
        assert key not in visible, f"visible metadata key leaked: {key}"

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
        assert section in visible, f"parent-facing section missing: {section}"


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
    _assert_distributed_story_md_has_no_yaml_frontmatter(md)


def _valid_journal_paths(output_root: Path) -> dict[str, Path]:
    production = output_root / "006_story"
    staging = output_root / "_staging" / "pkg"
    backup = output_root / "_archive" / "006_story_pre_swap_sim"
    return {"production": production, "staging": staging, "backup": backup}


def _write_journal(output_root: Path, payload: dict, name: str = "swap_bad.json") -> Path:
    path = journal_root(output_root) / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _base_payload(paths: dict[str, Path], **overrides) -> dict:
    payload = {
        "transaction_id": "sim",
        "production_path": str(paths["production"]),
        "staging_path": str(paths["staging"]),
        "backup_path": str(paths["backup"]),
        "phase": PHASE_PRODUCTION_BACKED_UP,
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "mutator,match",
    [
        (lambda p: p.pop("production_path"), "missing"),
        (lambda p: p.__setitem__("production_path", ""), "empty"),
        (lambda p: p.__setitem__("production_path", None), "null"),
        (lambda p: p.__setitem__("production_path", str(Path(""))), "unsafe empty/cwd|current working"),
        (lambda p: p.__setitem__("production_path", "."), "unsafe empty/cwd|current working"),
    ],
)
def test_journal_rejects_missing_empty_null_cwd_paths(tmp_path: Path, mutator, match: str) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    payload = _base_payload(paths)
    mutator(payload)
    with pytest.raises(InvalidSwapJournalError, match=match):
        parse_and_validate_journal(payload, output_root=output_root, project_root=tmp_path)


def test_journal_rejects_output_root_repo_root_traversal_and_outside(tmp_path: Path) -> None:
    output_root = (tmp_path / "output").resolve()
    paths = _valid_journal_paths(output_root)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    with pytest.raises(InvalidSwapJournalError, match="output_root"):
        parse_and_validate_journal(
            _base_payload(paths, production_path=str(output_root)),
            output_root=output_root,
            project_root=tmp_path,
        )
    with pytest.raises(InvalidSwapJournalError, match="repository root"):
        parse_and_validate_journal(
            _base_payload(paths),
            output_root=output_root,
            project_root=paths["production"],
        )
    with pytest.raises(InvalidSwapJournalError, match="parent traversal"):
        parse_and_validate_journal(
            _base_payload(paths, production_path=str(output_root / ".." / "outside_pkg")),
            output_root=output_root,
            project_root=tmp_path,
        )
    outside = (tmp_path / "elsewhere" / "pkg").resolve()
    outside.mkdir(parents=True)
    with pytest.raises(InvalidSwapJournalError, match="escapes approved root"):
        parse_and_validate_journal(
            _base_payload(paths, production_path=str(outside)),
            output_root=output_root,
            project_root=tmp_path,
        )


def test_journal_rejects_identical_operational_paths(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    with pytest.raises(InvalidSwapJournalError, match="distinct"):
        parse_and_validate_journal(
            _base_payload(paths, backup_path=str(paths["production"])),
            output_root=output_root,
            project_root=tmp_path,
        )
    with pytest.raises(InvalidSwapJournalError, match="distinct"):
        parse_and_validate_journal(
            _base_payload(paths, staging_path=str(paths["production"])),
            output_root=output_root,
            project_root=tmp_path,
        )


def test_invalid_journals_quarantined_without_package_mutation(tmp_path: Path, monkeypatch) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    production = paths["production"]
    staging = paths["staging"]
    backup = paths["backup"]
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    (production / "marker.txt").write_text("prod", encoding="utf-8")
    (staging / "marker.txt").write_text("stage", encoding="utf-8")
    (backup / "marker.txt").write_text("back", encoding="utf-8")

    rename_spy = MagicMock(side_effect=AssertionError("package rename must not run for invalid journals"))
    monkeypatch.setattr(package_swap_mod, "_retry_rename", rename_spy)

    # Missing production_path
    _write_journal(
        output_root,
        {
            "transaction_id": "a",
            "staging_path": str(staging),
            "backup_path": str(backup),
            "phase": PHASE_PRODUCTION_BACKED_UP,
        },
        "swap_missing.json",
    )
    # Empty production_path
    _write_journal(output_root, _base_payload(paths, production_path=""), "swap_empty.json")
    # Path("") / "."
    _write_journal(output_root, _base_payload(paths, production_path=str(Path(""))), "swap_dot.json")
    # Malformed JSON
    bad = journal_root(output_root) / "swap_malformed.json"
    bad.write_text("{not-json", encoding="utf-8")
    # Partially written JSON
    partial = journal_root(output_root) / "swap_partial.json"
    partial.write_text('{"transaction_id": "x", "production_path":', encoding="utf-8")
    # Absolute path outside output_root
    outside = (tmp_path / "outside_pkg").resolve()
    outside.mkdir()
    _write_journal(output_root, _base_payload(paths, production_path=str(outside)), "swap_outside.json")
    # production == backup
    _write_journal(
        output_root,
        _base_payload(paths, backup_path=str(production)),
        "swap_same_backup.json",
    )

    recovered = recover_unfinished_swaps(output_root=output_root, project_root=tmp_path)
    assert rename_spy.call_count == 0
    assert any(item.get("status") == STATUS_INVALID_SWAP_JOURNAL for item in recovered)
    assert (production / "marker.txt").read_text(encoding="utf-8") == "prod"
    assert (staging / "marker.txt").read_text(encoding="utf-8") == "stage"
    assert (backup / "marker.txt").read_text(encoding="utf-8") == "back"
    assert production.exists() and staging.exists() and backup.exists()
    # Evidence preserved in quarantine, not silently discarded.
    quarantined = list(quarantine_root(output_root).glob("swap_*.json"))
    assert len(quarantined) >= 6
    assert not list(journal_root(output_root).glob("swap_*.json"))

    with pytest.raises(RuntimeError, match=STATUS_INVALID_SWAP_JOURNAL):
        # Quarantine already cleared active journals; seed another invalid one to block swap.
        _write_journal(output_root, _base_payload(paths, production_path=""), "swap_block.json")
        atomic_replace_package_dir(
            staging_dir=staging,
            production_dir=production,
            archive_root=output_root / "_archive",
            output_root=output_root,
            project_root=tmp_path,
        )


def test_valid_journal_recovery_still_works(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    staging = paths["staging"]
    production = paths["production"]
    archive = output_root / "_archive"
    staging.mkdir(parents=True)
    production.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")

    backup = paths["backup"]
    archive.mkdir(parents=True)
    production.rename(backup)
    journal = _write_journal(output_root, _base_payload(paths), "swap_sim.json")
    recovered = recover_unfinished_swaps(output_root=output_root, project_root=tmp_path)
    assert recovered
    assert all(item.get("status") != STATUS_INVALID_SWAP_JOURNAL for item in recovered)
    assert production.exists()
    assert (production / "story.md").read_text(encoding="utf-8") == "old-story.md"
    assert not journal.exists()


def test_relative_journal_paths_rejected_before_mutation(tmp_path: Path, monkeypatch) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    rename_spy = MagicMock(side_effect=AssertionError("no rename on relative journal"))
    monkeypatch.setattr(package_swap_mod, "_retry_rename", rename_spy)
    _write_journal(
        output_root,
        _base_payload(paths, production_path="006_story"),
        "swap_relative.json",
    )
    with pytest.raises(InvalidSwapJournalError, match="absolute"):
        parse_and_validate_journal(
            _base_payload(paths, production_path="006_story"),
            output_root=output_root,
            project_root=tmp_path,
        )
    recovered = recover_unfinished_swaps(output_root=output_root, project_root=tmp_path)
    assert rename_spy.call_count == 0
    assert any(item.get("status") == STATUS_INVALID_SWAP_JOURNAL for item in recovered)


def test_atomic_replace_rejects_repo_root_journal_paths(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    paths = _valid_journal_paths(output_root)
    staging = paths["staging"]
    production = paths["production"]
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")
    # Seed an open journal whose production path equals project_root (repo-root collision).
    _write_journal(
        output_root,
        _base_payload(paths, production_path=str(production.resolve())),
        "swap_repo.json",
    )
    with pytest.raises(RuntimeError, match=STATUS_INVALID_SWAP_JOURNAL):
        atomic_replace_package_dir(
            staging_dir=staging,
            production_dir=production,
            archive_root=output_root / "_archive",
            output_root=output_root,
            project_root=production.resolve(),
        )


def test_camelcase_metadata_concepts_rejected() -> None:
    from krishna_story_factory.activities.planner import _extract_event_labels
    from krishna_story_factory.activities.qa import contains_metadata_concept

    samples = [
        "sourceReference",
        "scriptureReference",
        "scriptureRange",
        "ageRange",
        "storyNumber",
        "sourceREFERENCE",
        "SourceReference",
        "source-reference",
        "source_reference",
        "source reference",
    ]
    for sample in samples:
        assert contains_metadata_concept(sample), sample

    with pytest.raises(ValueError, match="metadata|concrete"):
        _extract_event_labels(
            "sourceReference: Krishna Book; ageRange: 6-12; storyNumber: 006",
            "sourceReference ageRange storyNumber",
        )


def test_story_003_semantic_dedup_on_actual_file() -> None:
    from krishna_story_factory.content.repairs import (
        count_story_003_fact_signatures,
        repair_story_003_dedup,
    )
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.pipeline import _content_from_story_md

    path = ROOT / "output" / "003_vasudeva-keeps-his-word" / "story.md"
    if not path.exists():
        pytest.skip("Story 003 package not present locally")
    plan = read_plan_by_chapter(ROOT, "003")
    original = _content_from_story_md(path.read_text(encoding="utf-8"), plan)
    before_audio = count_story_003_fact_signatures(original.audio_script)
    assert before_audio["KAMSA_RETURNS_CHILD"] >= 1
    repaired = apply_known_story_repairs("003", original)
    for blob in (repaired.main_story, repaired.audio_script):
        counts = count_story_003_fact_signatures(blob)
        for sig, count in counts.items():
            assert count <= 1, f"{sig}={count}"
        assert "kīrtimān" in blob.lower() or "kirtiman" in blob.lower().replace("ī", "i")
        assert "vasudeva" in blob.lower()
        assert "eighth" in blob.lower()
        assert blob.strip()
        assert not re.search(r"\n{3,}", blob)
    again = repair_story_003_dedup(repaired)
    assert again.main_story == repaired.main_story
    assert again.audio_script == repaired.audio_script
