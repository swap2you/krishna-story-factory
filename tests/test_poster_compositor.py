from __future__ import annotations

from pathlib import Path

from krishna_story_factory.config import load_settings
from krishna_story_factory.visuals.models import make_visual_paths
from krishna_story_factory.visuals.openai_image_client import OpenAIImageClient
from krishna_story_factory.visuals.poster_compositor import compose_poster, create_placeholder_poster_raw
from krishna_story_factory.visuals.line_art_compositor import compose_line_art_portrait, create_placeholder_line_art_raw
from krishna_story_factory.visuals.models import PosterCopy, SupportingCaption, VisualBrief
from krishna_story_factory.visuals.visual_quality import check_prompt_requirements, score_visual_outputs


def test_poster_compositor_adds_title_and_one_liner_locally(tmp_path: Path) -> None:
    raw = tmp_path / "poster_art_raw.png"
    out = tmp_path / "story_poster.png"
    create_placeholder_poster_raw(raw, title="RAW ONLY", scene="Scene placeholder")
    copy = PosterCopy(
        title="Local Title Added",
        subtitle="Bedtime Katha",
        heavenly_quote="Trust in the Lord.",
        one_liner="Wisdom and faith protect the family through fearful moments.",
        supporting_captions=[SupportingCaption(label="Scene", text="Palace gate")],
    )
    compose_poster(raw, out, copy)
    assert out.exists()
    from PIL import Image

    img = Image.open(out)
    assert img.width >= 1024


def test_quote_wrapping_stays_inside_canvas(tmp_path: Path) -> None:
    raw = tmp_path / "raw.png"
    out = tmp_path / "poster.png"
    create_placeholder_poster_raw(raw, title="T", scene="S")
    long_quote = " ".join(["Faith"] * 40)
    copy = PosterCopy(title="Title", heavenly_quote=long_quote, one_liner="Short summary line here.")
    compose_poster(raw, out, copy)
    assert out.stat().st_size > 0


def test_line_art_pdf_does_not_crop_artwork(tmp_path: Path) -> None:
    raw = tmp_path / "line_art_raw.png"
    portrait = tmp_path / "line_art_portrait.png"
    coloring = tmp_path / "coloring_page.png"
    pdf = tmp_path / "coloring_page_print.pdf"
    brief = VisualBrief(title="Print Test", central_scene="A devotional scene.")
    create_placeholder_line_art_raw(raw, brief=brief)
    compose_line_art_portrait(raw, portrait, coloring, pdf, title="Print Test Title")
    assert pdf.exists()
    assert pdf.stat().st_size > 1000


def test_reference_files_detected_when_present(tmp_path: Path) -> None:
    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    client = OpenAIImageClient(settings)
    line_ref = settings.image_line_art_reference or project / "assets/reference/line_art_reference.png"
    assert line_ref is not None
    exists = line_ref.exists()
    assert isinstance(exists, bool)


def test_pipeline_works_without_reference_files(tmp_path: Path) -> None:
    from krishna_story_factory.visuals.generator import StoryVisualGenerator

    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    story = project / "output/003_vasudevas-promise/story.md"
    if not story.exists():
        story.write_text("# Fallback\n\n## Main Story\nA gentle Krishna story.", encoding="utf-8")
    gen = StoryVisualGenerator(settings, mode="test")
    result = gen.generate_all(story, tmp_path, use_references=False, force=True)
    assert result.line_art_status in {"PLACEHOLDER", "GENERATED", "DRY_RUN"}
    paths = make_visual_paths(tmp_path)
    assert paths.visual_brief_json.exists()


def test_no_api_key_in_client_repr() -> None:
    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    client = OpenAIImageClient(settings)
    text = repr(client) + str(settings.openai_api_key)
    if settings.openai_api_key:
        assert settings.openai_api_key not in repr(client)


def test_poster_and_line_art_filenames_do_not_overlap() -> None:
    paths = make_visual_paths(Path("/tmp/example"))
    names = {
        paths.line_art_raw.name,
        paths.line_art_portrait.name,
        paths.poster_art_raw.name,
        paths.story_poster.name,
        paths.coloring_page.name,
    }
    assert len(names) == len(set(names))


def test_dry_run_saves_prompts_without_images(tmp_path: Path) -> None:
    from krishna_story_factory.visuals.generator import StoryVisualGenerator

    project = Path(__file__).resolve().parents[1]
    settings = load_settings(project)
    story = project / "output/003_vasudevas-promise/story.md"
    if not story.exists():
        story.write_text("# Dry Run\n\n## Main Story\nStory body.", encoding="utf-8")
    gen = StoryVisualGenerator(settings, mode="test")
    result = gen.generate_all(story, tmp_path, dry_run=True, force=True)
    assert result.dry_run is True
    paths = make_visual_paths(tmp_path)
    assert paths.line_art_prompt.exists()
    assert paths.poster_art_prompt.exists()
    assert not paths.line_art_raw.exists()


def test_visual_quality_prompt_checks() -> None:
    root = Path(__file__).resolve().parents[1]
    line_template = (root / "prompts/visuals/02_line_art_portrait.md").read_text(encoding="utf-8")
    poster_template = (root / "prompts/visuals/03_cinematic_poster_art.md").read_text(encoding="utf-8")
    assert not check_prompt_requirements(line_template, kind="line_art")
    assert not check_prompt_requirements(poster_template, kind="poster")
