from __future__ import annotations

import json
from pathlib import Path

import dataclasses

from krishna_story_factory.config import load_settings
from krishna_story_factory.manifest import write_manifest
from krishna_story_factory.models import PackagePaths, PlanRow, StoryContent
from krishna_story_factory.visuals.models import make_visual_paths
from krishna_story_factory.visuals.visual_quality import score_visual_outputs


def test_manifest_includes_visual_outputs(tmp_path: Path) -> None:
    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    out = tmp_path / "001_test"
    out.mkdir()
    paths = PackagePaths(
        root=out,
        story_md=out / "story.md",
        audio_script=out / "audio_script.txt",
        whatsapp_caption=out / "whatsapp_caption.txt",
        activity_sheet=out / "activity_sheet.pdf",
        story_card=out / "story_card.png",
        story_card_square=out / "story_card_square.png",
        story_card_wide=out / "story_card_wide.png",
        coloring_page=out / "coloring_page.png",
        image_prompt=out / "image_prompt.txt",
        hero_image_prompt=out / "hero_image_prompt.txt",
        story_card_square_prompt=out / "story_card_square_prompt.txt",
        story_card_wide_prompt=out / "story_card_wide_prompt.txt",
        line_art_prompt=out / "line_art_prompt.txt",
        coloring_page_prompt=out / "coloring_page_prompt.txt",
        ambient_prompt=out / "ambient_prompt.txt",
        parent_notes=out / "parent_notes.md",
        manifest=out / "manifest.json",
        narration_mp3=out / "narration.mp3",
    )
    for field in dataclasses.fields(paths):
        path = getattr(paths, field.name)
        if not isinstance(path, Path) or path == paths.root:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in {".png", ".pdf", ".mp3"}:
            path.write_bytes(b"x")
        else:
            path.write_text("sample", encoding="utf-8")

    vpaths = make_visual_paths(out)
    vpaths.visual_brief_json.write_text('{"title":"T","central_scene":"S"}', encoding="utf-8")
    vpaths.visual_generation_manifest.write_text(
        json.dumps({"line_art_status": "PLACEHOLDER", "poster_status": "PLACEHOLDER", "quality_score": 88}),
        encoding="utf-8",
    )

    plan = PlanRow(
        chapter_no="001",
        slug="test",
        title="Test",
        project="Krishna Book Bedtime",
        library_id="KB-001",
        age_range="6-12",
        package_type="daily",
        source_reference="Krishna Book",
        scripture_reference="",
        summary_seed="",
        send_date="",
        status="pending",
    )
    content = StoryContent(
        title="Test",
        recap="",
        main_story="",
        moral="",
        takeaway="",
        five_star_challenge=[],
        audio_script="script",
        whatsapp_caption="",
        image_prompt="prompt",
        line_art_prompt="line",
        story_card_text="Test",
        parent_notes="",
    )
    write_manifest(
        settings=settings,
        plan=plan,
        content=content,
        paths=paths,
        mode="test",
        quality_status="PASS",
        quality_errors=[],
        story_source="test",
        audio_source="test",
        image_source="test",
    )
    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    assert "visual_brief_json" in manifest["outputs"]
    assert manifest["visuals"]["quality_score"] == 88


def test_score_detects_missing_files(tmp_path: Path) -> None:
    paths = make_visual_paths(tmp_path)
    score, issues = score_visual_outputs(
        paths,
        line_prompt="portrait ages 6-13 outline white background large colorable spaces expressive faces safe print margins no cropping no gray shading no modern objects central scene",
        poster_prompt="portrait poster ultra-realistic 3d devotional cinematic clear focal hierarchy expressive indian faces ancient indian no modern objects do not generate final typography child-safe central hero scene",
    )
    assert score < 80
    assert any("Missing" in issue for issue in issues)
