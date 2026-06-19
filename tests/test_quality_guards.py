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
        "story_card_square_prompt",
        "parent_notes",
        "narration_mp3",
    ]:
        p = getattr(paths, name)
        p.write_text("x" * 20, encoding="utf-8")
    return paths


def _story_md(main_words: int, recap_words: int = 30, extra_sections: str = "") -> str:
    main = " ".join(f"scene{i}" for i in range(main_words))
    recap = " ".join(f"recap{i}" for i in range(recap_words))
    return (
        f"# Title\n\n## Recap\n{recap}\n\n## Main Story\n{main}\n\n"
        f"## Moral\nmoral words here\n\n## Takeaway\ntakeaway words here\n\n"
        f"## Five-Star Challenge\n1. one\n2. two\n{extra_sections}"
    )


def _varied_words(count: int, prefix: str = "audio") -> str:
    return " ".join(f"{prefix}{i}" for i in range(count))


def _manifest_json() -> str:
    return (
        '{"source_reference":"x","library_id":"krishna_book","age_range":"6-12",'
        '"generated_at":"now","generation":{"story_source":"x","audio_source":"x","image_source":"x"}}'
    )


def _valid_card_prompt() -> str:
    return (
        "1080x1080 ultra-realistic 3D devotional cinematic illustration, warm sacred lighting, "
        "clear focal scene, expressive Indian faces, no modern objects, not crowded."
    )


def _valid_coloring_prompt() -> str:
    return (
        "Premium children's devotional coloring-book illustration, centered composition, no cropping, "
        "large colorable spaces, thick black outlines, white background, cute sweet expressive faces."
    )


def test_main_story_951_words_passes(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(951, recap_words=200), encoding="utf-8")
    paths.audio_script.write_text(_varied_words(600), encoding="utf-8")
    paths.story_card_square_prompt.write_text(_valid_card_prompt(), encoding="utf-8")
    paths.coloring_page_prompt.write_text(_valid_coloring_prompt(), encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert ok, errors
    assert not any("too long" in e.lower() for e in errors)


def test_total_markdown_over_1050_with_valid_main_story_passes(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(900, recap_words=250), encoding="utf-8")
    paths.audio_script.write_text(_varied_words(600), encoding="utf-8")
    paths.story_card_square_prompt.write_text(_valid_card_prompt(), encoding="utf-8")
    paths.coloring_page_prompt.write_text(_valid_coloring_prompt(), encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, warnings = run_quality_checks(paths, mode="prod")
    assert ok, errors
    assert not any("story.md is too long" in e for e in errors)


def test_main_story_over_1050_fails(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(1100), encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("Main Story is too long" in e for e in errors)


def test_main_story_below_750_fails(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(100), encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("Main Story is too short" in e for e in errors)


def test_story_below_750_words_fails_quality_in_prod(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(100), encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("too short" in e for e in errors)


def test_audio_script_below_500_words_fails_quality_in_prod(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(900), encoding="utf-8")
    paths.audio_script.write_text("short script", encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("audio_script" in e for e in errors)


def test_caption_containing_group_fails_quality(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(900), encoding="utf-8")
    paths.audio_script.write_text(_varied_words(700), encoding="utf-8")
    paths.whatsapp_caption.write_text("Please reply to this group today.", encoding="utf-8")
    paths.manifest.write_text(_manifest_json(), encoding="utf-8")
    ok, errors, _warnings = run_quality_checks(paths, mode="prod")
    assert not ok
    assert any("group" in e.lower() for e in errors)


def test_parent_notes_required(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.parent_notes.unlink()
    ok, errors, _warnings = run_quality_checks(paths, mode="test")
    assert not ok
    assert any("parent_notes" in e for e in errors)


def test_word_search_grid_exists() -> None:
    puzzle = build_word_search(["Krishna", "Devaki", "Vasudeva", "Kamsa", "Wedding", "Prayer", "Chariot", "Voice", "Mathura", "Faith"])
    assert len(puzzle.grid) >= 10
    assert len(puzzle.grid[0]) >= 10
    assert len(puzzle.answer_key) >= 3


def test_story_002_recap_requires_eighth_son() -> None:
    plan = PlanRow(
        chapter_no="002",
        slug="devaki-and-vasudeva-wedding",
        title="The Wedding and the Heavenly Voice",
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
        recap="Tonight we hear about the wedding and a prophecy about future children.",
        main_story="Devaki and Vasudeva rode in a chariot while Kamsa drove.",
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
    assert any("eighth son" in e for e in errors)


def test_story_002_rejects_full_promise_phrase() -> None:
    plan = PlanRow(
        chapter_no="002",
        slug="devaki-and-vasudeva-wedding",
        title="The Wedding and the Heavenly Voice",
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
        recap="Recap about Devaki's eighth son.",
        main_story="Vasudeva said, I will bring each child to you.",
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
    assert any("each child" in e for e in errors)


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
