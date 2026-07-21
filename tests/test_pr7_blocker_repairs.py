"""PR #7 blocker repairs: metadata fallback, markdown structure, content, swap, drift."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from krishna_story_factory.activities.models import RolePlayCard
from krishna_story_factory.activities.planner import ActivityPlanner, _extract_event_labels, _pack_002
from krishna_story_factory.activities.qa import is_metadata_event_label, semantic_activity_errors
from krishna_story_factory.audio.drift import detect_audio_stale, narration_source_sha, preserved_audio_metadata
from krishna_story_factory.content.repairs import (
    apply_known_story_repairs,
    has_invented_direct_dialogue,
    normalize_story_text,
    repair_story_002_dialogue,
    repair_story_005_philosophy,
)
from krishna_story_factory.content.story_format_v2 import (
    validate_story_comment_structure,
    validate_story_markdown_v2,
)
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.models import PlanRow, StoryContent
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.package_swap import atomic_replace_package_dir, validate_exact_eight_files


ROOT = Path(__file__).resolve().parents[1]


def _plan(chapter: str, **kwargs) -> PlanRow:
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
        devotional_meaning="meaning",
        poster_visual_brief="poster brief",
        coloring_visual_brief="coloring brief",
    )
    base.update(kwargs)
    return StoryContent(**base)


def test_seed_metadata_never_becomes_event() -> None:
    # Codex-style seed payload that previously leaked frontmatter into events.
    seed = (
        "title: The Birth of Lord Krishna; source_reference: Krishna Book Chapter 3; "
        "age_range: 6-12; story_number: 006; Hare Kṛṣṇa, dear children"
    )
    with pytest.raises(ValueError, match="metadata|placeholders|concrete"):
        _extract_event_labels("---\ntitle: only\n---\n", "title: only\nage_range: 6-12")
    labels = _extract_event_labels(
        "# Main Story\n"
        "Auspicious signs appeared as the sacred night approached. "
        "Krishna appeared before Devaki and Vasudeva in His four-armed form. "
        "Devaki and Vasudeva offered prayers with love. "
        "Krishna assumed the form of an ordinary infant. "
        "Vasudeva's chains loosened and the prison doors opened. "
        "Vasudeva prepared to carry Krishna according to the Lord's arrangement.\n",
        seed,
    )
    joined = " | ".join(labels).lower()
    assert "title:" not in joined
    assert "source_reference" not in joined
    assert "age_range" not in joined
    assert all(not is_metadata_event_label(item) for item in labels)


def test_story_002_invented_dialogue_removed_despite_apostrophe_variants() -> None:
    main = (
        "Devaki squeezed Vasudeva’s hand. “Thank you for saving my life,” she whispered, her voice trembling but grateful. "
        "Vasudeva comforted her, whispering, “We must trust in Krishna’s plan, even when it is hard to see.”"
    )
    audio = (
        "Devaki squeezed Vasudeva’s hand. “Thank you for protecting me,” she whispered. "
        "He smiled and told her, “We will trust Krishna’s plan and stay true to our hearts.”"
    )
    repaired = repair_story_002_dialogue(_content(main_story=main, audio_script=audio, title="Wedding"))
    for blob in (repaired.main_story, repaired.audio_script):
        norm = normalize_story_text(blob).lower()
        assert "thank you for saving my life" not in norm
        assert "thank you for protecting my life" not in norm
        assert "thank you for protecting me" not in norm
        assert "we must trust in krishna" not in norm
        assert "we will trust krishna" not in norm
    assert "In paraphrase" in repaired.main_story


def test_story_002_role_cards_complete_and_printable() -> None:
    pack = _pack_002(_plan("002", title="The Wedding and the Heavenly Voice"))
    assert not semantic_activity_errors(pack)
    role_page = next(p for p in pack.pages if p.page_type == "ROLE_PLAY_CARDS")
    cards = [c for c in role_page.components if isinstance(c, RolePlayCard)]
    assert len(cards) == 4
    for card in cards:
        assert card.role.strip()
        assert len(card.line.strip()) > 20
        assert "I will help in" not in card.line
        assert "part of the story" not in card.line.lower()


def test_story_005_main_and_audio_clean_from_actual_file() -> None:
    path = ROOT / "output" / "005_prayers-by-the-demigods-for-lord-krishna-in-the-womb" / "story.md"
    if not path.exists():
        pytest.skip("Story 005 package not present locally")
    from krishna_story_factory.pipeline import _content_from_story_md

    plan = _plan(
        "005",
        title="Prayers by the Demigods for Lord Krishna in the Womb",
        slug="prayers-by-the-demigods-for-lord-krishna-in-the-womb",
    )
    content = apply_known_story_repairs("005", _content_from_story_md(path.read_text(encoding="utf-8"), plan))
    md = content.to_markdown()
    assert not validate_story_comment_structure(md)
    bad = (
        "celestial garden",
        "heavenly garden",
        "sweet-smelling gardens",
        "shield for her and for the lord",
        "ghost-like",
        "candra",
        "varuna",
        "varuṇa",
        "wind gods",
        "in the of the heavenly",
        "become a , teaching",
        "the the demigods",
        "you are the supreme protector",
        "you are never touched",
    )
    for blob in (content.main_story, content.audio_script):
        low = blob.lower()
        for phrase in bad:
            assert phrase not in low, phrase
        assert not has_invented_direct_dialogue(blob, allow_heavenly_voice=False)
    errors = run_source_guard(plan, content)
    assert not errors, errors
    # Audio should be grammatical enough: no empty 'a ,' fragments.
    assert "become a ," not in content.audio_script
    assert "in the of the" not in content.audio_script.lower()


def test_source_guard_scans_audio_script_for_story_005() -> None:
    plan = _plan("005", title="Prayers by the Demigods for Lord Krishna in the Womb")
    content = repair_story_005_philosophy(
        _content(
            main_story="Devaki carries Krishna in her womb while Brahma Shiva Narada pray.",
            audio_script="They gathered in celestial gardens and said 'You are the supreme protector.'",
            bedtime_reflection="What will you remember?",
            think_about_it=["What will you remember?"],
        )
    )
    # After rewrite, audio is clean.
    assert "celestial gardens" not in content.audio_script.lower()
    dirty = _content(
        main_story=content.main_story,
        audio_script="Far above in celestial gardens, Candra and Varuna acted. They become a shield for her and for the Lord.",
        bedtime_reflection="What will you remember?",
        think_about_it=["What will you remember?"],
        five_lessons=content.five_lessons,
    )
    errors = run_source_guard(plan, dirty)
    assert any("audio_script" in e or "shield" in e.lower() or "celestial" in e.lower() for e in errors)


def test_story_006_generic_invented_dialogue_patterns_fail() -> None:
    plan = _plan("006", title="The Birth of Lord Krishna")
    content = _content(
        main_story="Krishna appeared in four-armed form as an infant. Vasudeva whispered, \"O Lord save us now.\" Chains fell.",
        audio_script="Krishna appeared. Vasudeva said, \"Please protect us forever.\" Chains loosened.",
        five_lessons=["a", "b", "c", "d", "e"],
        bedtime_reflection="What will you remember?",
        think_about_it=["What will you remember?"],
    )
    errors = run_source_guard(plan, content)
    assert any("invented dialogue" in e.lower() or "quotation" in e.lower() for e in errors)


def test_one_valid_hidden_comment_block_only() -> None:
    content = apply_known_story_repairs(
        "002",
        _content(
            title="The Wedding and the Heavenly Voice",
            main_story="Kamsa drove the chariot. " * 40,
            audio_script="Narration about Devaki and Vasudeva. " * 30,
            think_about_it=["One?", "Two?", "Three?", "Four?", "<!--"],
            five_star_challenge=["1", "2", "3", "4", "5"],
            next_story_preview="Next story about truthfulness.",
            parent_note="Parent note about wedding and prophecy with enough words here for clarity.",
            poster_visual_brief="Poster of the wedding chariot.",
            coloring_visual_brief="Coloring of the wedding chariot.",
            bedtime_prayer="Dear Krishna. Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare.",
        ),
    )
    md = content.to_markdown()
    assert md.count("<!--") == 1
    assert md.count("-->") == 1
    assert not validate_story_comment_structure(md)
    assert "5. <!--" not in md


def test_actual_story_files_round_trip_structure() -> None:
    from krishna_story_factory.pipeline import _content_from_story_md

    mapping = {
        "002": ROOT / "output" / "002_devaki-and-vasudeva-wedding" / "story.md",
        "005": ROOT / "output" / "005_prayers-by-the-demigods-for-lord-krishna-in-the-womb" / "story.md",
        "006": ROOT / "output" / "006_the-birth-of-lord-krishna" / "story.md",
    }
    for chapter, path in mapping.items():
        if not path.exists():
            continue
        plan = _plan(chapter, title=path.parent.name)
        content = apply_known_story_repairs(chapter, _content_from_story_md(path.read_text(encoding="utf-8"), plan))
        md = content.to_markdown()
        errors = validate_story_markdown_v2(md)
        hard = [e for e in errors if "placeholder" not in e.lower()]
        assert not validate_story_comment_structure(md), chapter
        assert md.count("<!--") == 1 and md.count("-->") == 1, chapter
        assert "## Audio Narration" in md and md.lower().count("## audio narration") == 1, chapter
        assert "## Poster Visual Brief" in md
        assert "Poster Visual Brief\n\n\n" not in md.replace("\r\n", "\n")
        poster_idx = md.index("## Poster Visual Brief")
        coloring_idx = md.index("## Coloring Visual Brief")
        assert md[poster_idx:coloring_idx].strip() != "## Poster Visual Brief"


def test_truthful_preserved_audio_metadata(tmp_path: Path) -> None:
    narration = tmp_path / "narration.mp3"
    narration.write_bytes(b"1234567890" * 50)
    source, meta = preserved_audio_metadata(narration_path=narration, prior_manifest=None, waveform_status="PASS", duration_seconds=12.5)
    assert source == "unknown_preserved"
    assert meta["provider"] == "unknown_preserved"
    assert meta["model_id"] is None
    assert meta["voice"] is None
    assert meta["generation_verified"] is False
    assert meta["sha256"]
    assert meta["bytes"] > 0


def test_stale_narration_detected_after_story_change(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    original = "Hare Krishna soft bedtime narration about Devaki."
    manifest.write_text(
        json.dumps({"narration_source_sha": narration_source_sha(original), "audio": {"provider": "openai"}}),
        encoding="utf-8",
    )
    stale, detail = detect_audio_stale(audio_script=original + " changed text", manifest_path=manifest)
    assert stale
    assert "AUDIO_STALE" in detail


def test_full_package_directory_swap_is_atomic(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    staging = output_root / "_staging" / "pkg"
    production = output_root / "006_story"
    archive = output_root / "_archive"
    staging.mkdir(parents=True)
    production.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")
    result = atomic_replace_package_dir(
        staging_dir=staging,
        production_dir=production,
        archive_root=archive,
        output_root=output_root,
    )
    assert result["status"] == "REPLACED"
    assert (production / "story.md").read_text(encoding="utf-8") == "new-story.md"
    assert not staging.exists()
    assert validate_exact_eight_files(production) == []


def test_failed_swap_rolls_back(tmp_path: Path) -> None:
    output_root = tmp_path / "output"
    staging = output_root / "_staging" / "pkg"
    production = output_root / "006_story"
    archive = output_root / "_archive"
    staging.mkdir(parents=True)
    production.mkdir(parents=True)
    for name in FINAL_OUTPUT_FILES:
        (staging / name).write_text(f"new-{name}", encoding="utf-8")
        (production / name).write_text(f"old-{name}", encoding="utf-8")

    calls = {"n": 0}
    real_retry = atomic_replace_package_dir.__globals__["_retry_rename"] if False else None
    from krishna_story_factory import package_swap as swap_mod

    real_retry = swap_mod._retry_rename

    def flaky(src, dest, *, attempts=8):  # noqa: ANN001
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError(5, "simulated failure")
        return real_retry(src, dest, attempts=attempts)

    with patch.object(swap_mod, "_retry_rename", flaky):
        with pytest.raises((OSError, RuntimeError), match="simulated failure|Directory rename failed|rollback"):
            atomic_replace_package_dir(
                staging_dir=staging,
                production_dir=production,
                archive_root=archive,
                output_root=output_root,
            )
    # Production should still have old content after rollback.
    assert (production / "story.md").read_text(encoding="utf-8") == "old-story.md"


def test_story_007_remains_pending_contract(tmp_path: Path) -> None:
    from krishna_story_factory.csv_store import ensure_csv_files, read_next_pending, read_plan_by_chapter, update_plan_status

    project = tmp_path / "proj"
    (project / "input").mkdir(parents=True)
    (project / "tracking").mkdir(parents=True)
    shutil.copy2(ROOT / "input" / "series_plan.csv", project / "input" / "series_plan.csv")
    ensure_csv_files(project)
    for chapter in ("001", "002", "003", "004", "005", "006"):
        update_plan_status(project, read_plan_by_chapter(project, chapter), "done")
    pending = read_next_pending(project)
    assert pending is not None and pending.chapter_no == "007"
