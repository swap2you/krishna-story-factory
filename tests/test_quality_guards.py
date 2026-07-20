from __future__ import annotations

from pathlib import Path

from krishna_story_factory.config import Settings
from krishna_story_factory.models import PackagePaths, PlanRow, StoryContent
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.generation.story_generator import _generation_issues, _repair_story003_boundary
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
        f"\n## Bedtime Reflection\nWhat kind action will you take tomorrow?\n"
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


def test_empty_bedtime_reflection_fails_quality(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    text = _story_md(800).replace("What kind action will you take tomorrow?", "")
    paths.story_md.write_text(text, encoding="utf-8")
    ok, errors, _ = run_quality_checks(paths, mode="prod", poster_score=90, coloring_score=90)
    assert not ok
    assert any("reflection" in error.lower() for error in errors)


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


def test_story_001_source_guard_accepts_required_facts_and_rejects_invention() -> None:
    plan = _source_plan("001", "the-earth-prays-for-krishna")
    factual = (
        "Bhumi, Mother Earth, assumed the form of a cow and approached Lord Brahma. "
        "Brahma and the demigods went to the Ocean of Milk. Within his heart, Brahma received "
        "the message that the Lord would appear as the son of Vasudeva."
    )
    assert run_source_guard(plan, _source_content(plan, factual)) == []
    invented = factual + ' The Lord said, "I will be born in Vrindavana."'
    assert any("Vrindavana" in error for error in run_source_guard(plan, _source_content(plan, invented)))


def test_story_002_source_guard_enforces_relationships() -> None:
    plan = _source_plan("002", "devaki-and-vasudeva-wedding")
    factual = (
        "Kamsa, Devaki's brother and the son of Ugrasena, personally drove the chariot. "
        "The warning concerned Devaki's eighth child."
    )
    assert run_source_guard(plan, _source_content(plan, factual)) == []
    assert any("cousin" in error.lower() for error in run_source_guard(plan, _source_content(plan, factual + " He was her cousin.")))


def test_story_003_guard_stops_before_narada_and_imprisonment() -> None:
    plan = _source_plan("003", "vasudeva-keeps-his-word")
    factual = (
        "Devaki's first son Kirtiman was born. Truthful Vasudeva kept his word and brought Kirtiman to Kamsa. "
        "Astonished, Kamsa returned Kirtiman because the warning concerned the eighth child."
    )
    assert run_source_guard(plan, _source_content(plan, factual)) == []
    crossed = factual + " Later Narada came, and Kamsa chose to imprison the parents."
    assert run_source_guard(plan, _source_content(plan, crossed))
    assert any("boundary" in issue.lower() for issue in _generation_issues(_source_content(plan, crossed), plan))


def test_story_003_guard_distinguishes_safety_claim_from_caution() -> None:
    plan = _source_plan("003", "vasudeva-keeps-his-word")
    factual = (
        "Devaki's first son Kirtiman was born. Truthful Vasudeva kept his word and brought Kirtiman to Kamsa. "
        "Kamsa returned Kirtiman. Vasudeva did not assume the family was permanently safe."
    )
    assert run_source_guard(plan, _source_content(plan, factual)) == []
    unsafe = factual.replace("did not assume the family was", "believed the family was")
    assert any("permanently safe" in error for error in run_source_guard(plan, _source_content(plan, unsafe)))


def test_story_003_deterministic_repair_removes_later_episode_and_restores_ending() -> None:
    plan = _source_plan("003", "vasudeva-keeps-his-word")
    broken = _source_content(
        plan,
        "Devaki's first son was born. They were locked up in prison. Truthful Vasudeva brought him to Kamsa.",
    )
    repaired = _repair_story003_boundary(broken)
    assert "prison" not in repaired.main_story.lower()
    assert "initially returned the child" in repaired.main_story.lower()
    assert "initially returned the child" in repaired.audio_script.lower()


def _source_plan(chapter: str, slug: str) -> PlanRow:
    return PlanRow(
        chapter_no=chapter, slug=slug, title="Title", project="krishna_book_bedtime", library_id="krishna_book",
        source_reference="Krishna Book Chapter 1", scripture_reference="SB 10.1", summary_seed="Seed",
        age_range="6-12", package_type="bedtime_story", send_date="", status="pending",
    )


def _source_content(plan: PlanRow, text: str) -> StoryContent:
    return StoryContent(
        title=plan.title, recap="", main_story=text, moral="Be truthful.", takeaway="Trust Krishna.",
        five_star_challenge=["a", "b", "c", "d", "e"], audio_script=text,
        bedtime_reflection="Whom can you ask for help when a promise feels unsafe?",
    )


def test_extra_output_files_fail_quality(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    paths.story_md.write_text(_story_md(800), encoding="utf-8")
    (paths.root / "debug.txt").write_text("extra", encoding="utf-8")
    ok, errors, _ = run_quality_checks(
        paths, mode="prod", poster_score=90, coloring_score=90, require_manifest=True
    )
    assert not ok
    assert any("Unexpected files" in e for e in errors)
