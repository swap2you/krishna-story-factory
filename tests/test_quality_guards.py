from __future__ import annotations

from pathlib import Path

from krishna_story_factory.models import PackagePaths, PlanRow, StoryContent
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.pdf.word_search import build_word_search
from krishna_story_factory.quality.checks import run_quality_checks


def _paths(tmp_path: Path) -> PackagePaths:
    root = tmp_path / "pkg"
    root.mkdir()
    paths = PackagePaths(
        root=root,
        story_md=root / "story.md",
        audio_script=root / "audio_script.txt",
        whatsapp_caption=root / "whatsapp_caption.txt",
        activity_sheet=root / "activity_sheet.pdf",
        story_card=root / "story_card.png",
        story_card_square=root / "story_card_square.png",
        story_card_wide=root / "story_card_wide.png",
        coloring_page=root / "coloring_page.png",
        image_prompt=root / "image_prompt.txt",
        hero_image_prompt=root / "hero_image_prompt.txt",
        story_card_square_prompt=root / "story_card_square_prompt.txt",
        story_card_wide_prompt=root / "story_card_wide_prompt.txt",
        line_art_prompt=root / "line_art_prompt.txt",
        coloring_page_prompt=root / "coloring_page_prompt.txt",
        ambient_prompt=root / "ambient_prompt.txt",
        parent_notes=root / "parent_notes.md",
        manifest=root / "manifest.json",
        narration_mp3=root / "narration.mp3",
    )
    for name in [
        "story_md",
        "audio_script",
        "whatsapp_caption",
        "activity_sheet",
        "story_card",
        "image_prompt",
        "line_art_prompt",
        "coloring_page_prompt",
        "parent_notes",
        "narration_mp3",
    ]:
        p = getattr(paths, name)
        p.write_text("x" * 20, encoding="utf-8")
    return paths


def _story_md(words: int) -> str:
    body = " ".join(["word"] * words)
    return (
        f"# Title\n\n## Recap\n{body}\n\n## Main Story\n{body}\n\n"
        f"## Moral\nmoral\n\n## Takeaway\ntakeaway\n\n## Five-Star Challenge\n1. one\n"
    )


def test_story_below_750_words_fails_quality_in_prod(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(100), encoding="utf-8")
    paths.manifest.write_text(
        '{"source_reference":"x","library_id":"krishna_book","age_range":"6-12","generated_at":"now","generation":{"story_source":"x","audio_source":"x","image_source":"x"}}',
        encoding="utf-8",
    )
    ok, errors = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("too short" in e for e in errors)


def test_audio_script_below_500_words_fails_quality_in_prod(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(900), encoding="utf-8")
    paths.audio_script.write_text("short script", encoding="utf-8")
    paths.manifest.write_text(
        '{"source_reference":"x","library_id":"krishna_book","age_range":"6-12","generated_at":"now","generation":{"story_source":"x","audio_source":"x","image_source":"x"}}',
        encoding="utf-8",
    )
    ok, errors = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("audio_script" in e for e in errors)


def test_caption_containing_group_fails_quality(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(900), encoding="utf-8")
    paths.audio_script.write_text(" ".join(["word"] * 700), encoding="utf-8")
    paths.whatsapp_caption.write_text("Please reply to this group today.", encoding="utf-8")
    paths.manifest.write_text(
        '{"source_reference":"x","library_id":"krishna_book","age_range":"6-12","generated_at":"now","generation":{"story_source":"x","audio_source":"x","image_source":"x"}}',
        encoding="utf-8",
    )
    ok, errors = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("group" in e.lower() for e in errors)


def test_parent_notes_required(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.parent_notes.unlink()
    ok, errors = run_quality_checks(paths, mode="test")
    assert not ok
    assert any("parent_notes" in e for e in errors)


def test_word_search_grid_exists() -> None:
    puzzle = build_word_search(["Krishna", "Devaki", "Vasudeva", "Kamsa", "Wedding", "Prayer", "Chariot", "Voice", "Mathura", "Faith"])
    assert len(puzzle.grid) >= 10
    assert len(puzzle.grid[0]) >= 10
    assert len(puzzle.answer_key) >= 3


def test_story_002_fails_if_kamsa_is_called_king() -> None:
    plan = PlanRow(
        chapter_no="002",
        slug="devaki-and-vasudeva-wedding",
        title="Wedding",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 1",
        scripture_reference="SB 10.1",
        summary_seed="seed",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
    )
    content = StoryContent(
        title="Wedding",
        recap="recap",
        main_story="King Kamsa heard a voice.",
        moral="moral",
        takeaway="takeaway",
        five_star_challenge=["a"],
        audio_script="audio",
        whatsapp_caption="",
        image_prompt="img",
        line_art_prompt="line",
        story_card_text="Wedding",
        parent_notes="notes",
    )
    errors = run_source_guard(plan, content)
    assert errors


def test_story_001_fails_unrelated_pastimes() -> None:
    plan = PlanRow(
        chapter_no="001",
        slug="the-earth-prays-for-krishna",
        title="The Earth Prays for Krishna to Come",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 1",
        scripture_reference="SB 10.1",
        summary_seed="seed",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
    )
    content = StoryContent(
        title=plan.title,
        recap="recap",
        main_story="Then Putana came to Gokula and Damodara pastime appeared.",
        moral="moral",
        takeaway="takeaway",
        five_star_challenge=["a"],
        audio_script="audio",
        whatsapp_caption="",
        image_prompt="img",
        line_art_prompt="line",
        story_card_text=plan.title,
        parent_notes="notes",
    )
    errors = run_source_guard(plan, content)
    assert errors
