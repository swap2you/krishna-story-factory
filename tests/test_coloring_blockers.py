from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import httpx
import pytest
from PIL import Image

from krishna_story_factory.config import load_settings
from krishna_story_factory.images.client import ColoringAPIError, ImageClient
from krishna_story_factory.images.generator import generate_coloring
from krishna_story_factory.images.vision_qa import VisionReview
from krishna_story_factory.models import StoryContent
from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
from krishna_story_factory.activities.planner import ActivityPlanner
from krishna_story_factory.storage import google_drive_uploader as drive
from krishna_story_factory.pipeline import _rebuild_components
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from datetime import datetime, timezone
import hashlib
from test_adaptive_components import row


def settings(tmp_path: Path):
    return replace(
        load_settings(Path.cwd()), project_root=Path.cwd(), output_root=tmp_path / "output",
        openai_api_key="test-key", openai_image_enabled=True, openai_image_model="gpt-image-2",
        image_reference_line_art=None, google_drive_local_sync_root=None,
    )


def test_image_timeout_uses_fresh_client_and_one_retry(tmp_path, monkeypatch):
    client = ImageClient(settings(tmp_path))
    reference = tmp_path / "poster.png"; reference.write_bytes(b"poster")
    fresh = []
    monkeypatch.setattr(client, "_fresh_openai_client", lambda: fresh.append(object()) or fresh[-1])
    monkeypatch.setattr("krishna_story_factory.images.client.time.sleep", lambda _: None)
    calls = []

    def generate(_api, _prompt, output, _size, _quality, _reference, _style=None):
        calls.append(1)
        if len(calls) == 1:
            raise httpx.ReadTimeout("bounded timeout")
        output.write_bytes(b"image")

    monkeypatch.setattr(client, "_generate_with_reference", generate)
    result = client.generate("prompt", tmp_path / "candidate.png", reference_path=reference, story_title="Story")
    assert result.api_attempts == 2
    assert len(fresh) == 2


def test_two_timeouts_raise_clear_error_and_preserve_output(tmp_path, monkeypatch):
    client = ImageClient(settings(tmp_path))
    reference = tmp_path / "poster.png"; reference.write_bytes(b"poster")
    monkeypatch.setattr(client, "_fresh_openai_client", lambda: object())
    monkeypatch.setattr(client, "_generate_with_reference", lambda *_args, **_kwargs: (_ for _ in ()).throw(httpx.ReadTimeout("bounded timeout")))
    monkeypatch.setattr("krishna_story_factory.images.client.time.sleep", lambda _: None)
    output = tmp_path / "candidate.png"
    with pytest.raises(ColoringAPIError, match="COLORING_API_TIMEOUT"):
        client.generate("prompt", output, reference_path=reference, story_title="Story")
    assert not output.exists()


def _content() -> StoryContent:
    return StoryContent("Story", "recap", "story", "moral", "takeaway", [], "audio", coloring_visual_brief="brief")


def _review(score: int, identity: int, hard: bool = False) -> VisionReview:
    return VisionReview(score, identity, [], hard, ["hard"] if hard else [], score < 90 or hard, {})


@pytest.mark.parametrize("reviews,expected_calls", [([_review(94, 94)], 1), ([_review(82, 90), _review(93, 92)], 2)])
def test_next_candidate_only_after_qa_failure(tmp_path, monkeypatch, reviews, expected_calls):
    cfg = settings(tmp_path)
    poster = tmp_path / "poster.png"; Image.new("RGB", (32, 32), "white").save(poster)
    calls = []

    def fake_generate(_self, _prompt, output, **_kwargs):
        calls.append(output)
        Image.new("RGB", (32, 32), "white").save(output)

    monkeypatch.setattr(ImageClient, "generate", fake_generate)
    monkeypatch.setattr("krishna_story_factory.images.generator.review_image", lambda *_args, **_kwargs: reviews.pop(0))
    score, poster_used, _, identity = generate_coloring(
        cfg, story_md="story", content=_content(), output_path=tmp_path / "final.png",
        work_candidates=tmp_path / "candidates", work_reviews=tmp_path / "reviews",
        poster_path=poster, max_candidates=3,
    )
    assert len(calls) == expected_calls
    assert score >= 90 and identity >= 90 and poster_used


def test_poppler_fallback_works_without_pymupdf(tmp_path):
    plan = row("001", "The Earth Prays for Krishna to Come")
    activity = ActivityPlanner(tmp_path / "history.csv").plan(plan, "story")
    pdf = tmp_path / "activity.pdf"
    ActivitySheetGenerator().generate(plan, activity, pdf)
    result = validate_activity_pdf(pdf, tmp_path / "rendered", activity=activity)
    assert 2 <= result.page_count <= 4
    assert not result.errors
    assert (tmp_path / "rendered" / "activity_page_1.png").exists()


def test_drive_replacement_uploads_component_files_including_simple_coloring(tmp_path, monkeypatch):
    cfg = replace(settings(tmp_path), google_drive_upload_enabled=True, google_drive_credentials_file=tmp_path / "creds.json")
    source = tmp_path / "001_story"; source.mkdir()
    for name in ("activity_sheet.pdf", "coloring_page.png", "simple_coloring_page.png"):
        (source / name).write_bytes(b"x")
    # Provide remaining finals so migration sync can succeed in the test mock.
    for name in FINAL_OUTPUT_FILES:
        path = source / name
        if not path.exists():
            path.write_bytes(b"x")
    manifest = source / "manifest.json"
    manifest.write_text(json.dumps({"package": {"package_link": "https://drive.google.com/drive/folders/existing123"}}), encoding="utf-8")
    uploaded = []

    class Files:
        def list(self, **_kwargs): return self
        def execute(self): return {"files": [{"name": name, "id": name, "modifiedTime": "now"} for name in FINAL_OUTPUT_FILES]}
        def update(self, **_kwargs): return self

    class Service:
        def files(self): return Files()

    monkeypatch.setattr(drive, "_build_drive_service", lambda *_args: Service())
    monkeypatch.setattr(drive, "_upload_file", lambda _service, folder_id, path: uploaded.append((folder_id, path.name)))
    monkeypatch.setattr(drive, "_prune_non_final_files", lambda *_args, **_kwargs: None)
    result = drive.replace_component_files(cfg, source_dir=source, manifest_path=manifest)
    assert result.status == "UPLOADED"
    assert ("existing123", "activity_sheet.pdf") in uploaded
    assert ("existing123", "coloring_page.png") in uploaded
    assert ("existing123", "simple_coloring_page.png") in uploaded
    assert ("existing123", "manifest.json") in uploaded


def test_component_rebuild_preserves_locked_files_and_eight_file_contract(tmp_path, monkeypatch):
    cfg = replace(settings(tmp_path), project_root=tmp_path, output_root=tmp_path / "output", debug_artifacts=False)
    plan = row("001", "The Earth Prays for Krishna to Come")
    package = cfg.output_root / "001_story"; package.mkdir(parents=True)
    story = """# The Earth Prays for Krishna to Come

## Recap
recap

## Main Story
story

## Moral
moral

## Takeaway
takeaway

<!--
## Audio Performance Script
audio

## Poster Visual Brief
poster

## Coloring Visual Brief
coloring

## Activity Data
-->
"""
    (package / "story.md").write_text(story, encoding="utf-8")
    (package / "narration.mp3").write_bytes(b"audio")
    Image.new("RGB", (32, 32), "white").save(package / "story_poster.png")
    Image.new("RGB", (32, 32), "white").save(package / "coloring_page.png")
    Image.new("RGB", (32, 32), "white").save(package / "simple_coloring_page.png")
    (package / "activity_sheet.pdf").write_bytes(b"old")
    (package / "whatsapp_caption.txt").write_text("caption", encoding="utf-8")
    (package / "manifest.json").write_text(json.dumps({"package": {}, "images": {}}), encoding="utf-8")
    locked = [package / name for name in ("story.md", "narration.mp3", "story_poster.png", "whatsapp_caption.txt")]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in locked}

    def fake_coloring(_settings, **kwargs):
        Image.new("RGB", (32, 32), "white").save(kwargs["output_path"])
        return 94, True, False, 95

    def fake_simple(_settings, **kwargs):
        Image.new("RGB", (32, 32), "white").save(kwargs["output_path"])
        return 90, True

    monkeypatch.setattr("krishna_story_factory.pipeline.generate_coloring", fake_coloring)
    monkeypatch.setattr("krishna_story_factory.pipeline.generate_simple_coloring", fake_simple)
    result = _rebuild_components(
        cfg, plan, mode="test", no_upload=True, debug=False, now=datetime.now(timezone.utc),
    )
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in locked}
    assert before == after
    assert result["queue_unchanged"] is True
    assert result["final_file_count"] == 8
    assert {path.name for path in package.iterdir()} == {
        "story.md", "narration.mp3", "story_poster.png", "coloring_page.png",
        "simple_coloring_page.png", "activity_sheet.pdf", "whatsapp_caption.txt", "manifest.json",
    }
