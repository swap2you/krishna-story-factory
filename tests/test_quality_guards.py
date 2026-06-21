from __future__ import annotations

from pathlib import Path

from krishna_story_factory.config import Settings
from krishna_story_factory.models import PackagePaths, PlanRow, StoryContent
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.quality.checks import run_quality_checks


def _paths(tmp_path: Path) -> PackagePaths:
    root = tmp_path / "pkg"
    root.mkdir()
    paths = PackagePaths(
        root=root,
        story_md=root / "story.md",
        narration_mp3=root / "narration.mp3",
        story_poster=root / "story_poster.png",
        coloring_page=root / "coloring_page.png",
        activity_sheet=root / "activity_sheet.pdf",
        whatsapp_caption=root / "whatsapp_caption.txt",
        manifest=root / "manifest.json",
    )
    for name in FINAL_OUTPUT_FILES:
        p = root / name
        if p.suffix == ".mp3":
            p.write_bytes(b"x" * 600_000)
        else:
            p.write_text("x" * 20, encoding="utf-8")
    return paths


def _story_md(main_words: int) -> str:
    main = " ".join(f"scene{i}" for i in range(main_words))
    return (
        f"# Title\n\n## Recap\nrecap text here\n\n## Main Story\n{main}\n\n"
        f"## Moral\nmoral words here\n\n## Takeaway\ntakeaway words here\n\n"
        f"## Five-Star Challenge\n1. one\n2. two\n3. three\n4. four\n5. five\n"
    )


def test_main_story_word_count_uses_main_section_only(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(800), encoding="utf-8")
    ok, errors, _ = run_quality_checks(paths, mode="prod", poster_score=90, coloring_score=90)
    assert ok, errors


def test_main_story_too_short_fails_prod(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(400), encoding="utf-8")
    ok, errors, _ = run_quality_checks(paths, mode="prod", poster_score=90, coloring_score=90)
    assert not ok
    assert any("too short" in e.lower() for e in errors)


def test_source_guard_blocks_wrong_pastime_for_chapter_002() -> None:
    plan = PlanRow(
        chapter_no="002",
        slug="devaki-and-vasudeva-wedding",
        title="The Wedding and the Heavenly Voice",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 1",
        scripture_reference="SB 10.1",
        summary_seed="Wedding and prophecy",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
    )
    content = StoryContent(
        title=plan.title,
        recap="Recap about Putana coming to Gokula.",
        main_story="Putana tried to poison baby Krishna in Gokula.",
        moral="Krishna protects.",
        takeaway="Trust Krishna.",
        five_star_challenge=["a", "b", "c", "d", "e"],
        audio_script="audio",
    )
    errors = run_source_guard(plan, content)
    assert errors


def test_extra_output_files_fail_quality(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(800), encoding="utf-8")
    (paths.root / "debug.txt").write_text("extra", encoding="utf-8")
    ok, errors, _ = run_quality_checks(
        paths, mode="prod", poster_score=90, coloring_score=90, require_manifest=True
    )
    assert not ok
    assert any("Unexpected files" in e for e in errors)
