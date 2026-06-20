from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path

from ..config import Settings
from .line_art_compositor import compose_line_art_portrait, create_placeholder_line_art_raw
from .models import VisualGenerationResult, VisualPaths, make_visual_paths
from .openai_image_client import OpenAIImageClient
from .poster_compositor import compose_poster, create_placeholder_poster_raw
from .prompt_renderer import render_line_art_prompt, render_poster_art_prompt
from .story_visual_brief import (
    VisualBriefError,
    generate_poster_copy,
    generate_visual_brief,
    load_poster_copy_json,
    load_visual_brief_json,
)
from .visual_quality import score_visual_outputs

logger = logging.getLogger(__name__)


class StoryVisualGenerator:
    def __init__(self, settings: Settings, mode: str = "prod") -> None:
        self.settings = settings
        self.mode = mode
        self.image_client = OpenAIImageClient(settings)

    def generate_all(
        self,
        story_md_path: Path,
        output_dir: Path,
        *,
        line_art_only: bool = False,
        poster_only: bool = False,
        use_references: bool | None = None,
        force: bool = False,
        dry_run: bool = False,
    ) -> VisualGenerationResult:
        paths = make_visual_paths(output_dir)
        story_md = story_md_path.read_text(encoding="utf-8")
        use_refs = self._resolve_use_references(use_references)
        line_ref, poster_ref = self._reference_paths()
        refs_used = False
        if use_refs:
            if line_ref.exists() or poster_ref.exists():
                refs_used = True
            else:
                logger.info("Style reference images not found; continuing with text templates only.")

        result = VisualGenerationResult(
            model=self.image_client.model,
            quality=self.settings.openai_image_quality,
            reference_images_used=refs_used,
            dry_run=dry_run,
        )

        brief = self._load_or_create_brief(story_md, paths, force=force)
        paths.visual_brief_json.write_text(json.dumps(brief.to_dict(), indent=2), encoding="utf-8")

        line_prompt = render_line_art_prompt(self.settings.project_root, brief, use_reference=use_refs)
        poster_prompt = render_poster_art_prompt(self.settings.project_root, brief, use_reference=use_refs)
        paths.line_art_prompt.write_text(line_prompt, encoding="utf-8")
        paths.poster_art_prompt.write_text(poster_prompt, encoding="utf-8")

        poster_copy = None
        if not line_art_only:
            if paths.poster_copy_json.exists() and not force:
                poster_copy = load_poster_copy_json(paths.poster_copy_json)
            else:
                poster_copy = generate_poster_copy(self.settings, story_md, brief)
                paths.poster_copy_json.write_text(json.dumps(poster_copy.to_dict(), indent=2), encoding="utf-8")

        if dry_run:
            result.line_art_status = "DRY_RUN"
            result.poster_status = "DRY_RUN"
            self._write_manifest(paths, result, [])
            return result

        records = []
        generate_line = self.settings.image_generate_line_art and not poster_only
        generate_poster_flag = self.settings.image_generate_poster and not line_art_only

        if generate_line:
            result.requested_sizes["line_art"] = self.settings.image_line_art_size
            if self._should_call_openai():
                record = self.image_client.generate(
                    line_prompt,
                    paths.line_art_raw,
                    size=self.settings.image_line_art_size,
                    reference_path=line_ref if use_refs and line_ref.exists() else None,
                )
                records.append(asdict(record))
                result.actual_sizes["line_art"] = record.actual_size
                result.line_art_status = "GENERATED"
            else:
                create_placeholder_line_art_raw(paths.line_art_raw, brief=brief)
                result.line_art_status = "PLACEHOLDER"

            quote = brief.heavenly_message_or_quote
            if self.settings.image_add_local_typography:
                compose_line_art_portrait(
                    paths.line_art_raw,
                    paths.line_art_portrait,
                    paths.coloring_page,
                    paths.coloring_page_print_pdf,
                    title=brief.title,
                    quote=quote,
                )
            else:
                paths.line_art_portrait.write_bytes(paths.line_art_raw.read_bytes())
                paths.coloring_page.write_bytes(paths.line_art_raw.read_bytes())

        if generate_poster_flag and poster_copy is not None:
            result.requested_sizes["poster"] = self.settings.image_poster_size
            if self._should_call_openai():
                record = self.image_client.generate(
                    poster_prompt,
                    paths.poster_art_raw,
                    size=self.settings.image_poster_size,
                    reference_path=poster_ref if use_refs and poster_ref.exists() else None,
                )
                records.append(asdict(record))
                result.actual_sizes["poster"] = record.actual_size
                result.poster_status = "GENERATED"
            else:
                create_placeholder_poster_raw(paths.poster_art_raw, title=brief.title, scene=brief.central_scene)
                result.poster_status = "PLACEHOLDER"

            if self.settings.image_add_local_typography:
                compose_poster(
                    paths.poster_art_raw,
                    paths.story_poster,
                    poster_copy,
                    whatsapp_path=paths.story_poster_whatsapp,
                )
            else:
                paths.story_poster.write_bytes(paths.poster_art_raw.read_bytes())

        score, issues = score_visual_outputs(
            paths,
            line_prompt=line_prompt,
            poster_prompt=poster_prompt,
            threshold=self.settings.visual_quality_threshold,
        )
        result.quality_score = score
        result.issues = issues
        self._write_manifest(paths, result, records)
        return result

    def _load_or_create_brief(self, story_md: str, paths: VisualPaths, *, force: bool):
        if paths.visual_brief_json.exists() and not force:
            try:
                return load_visual_brief_json(paths.visual_brief_json)
            except VisualBriefError:
                pass
        brief = generate_visual_brief(self.settings, story_md)
        errors = brief.validate()
        if errors:
            brief = generate_visual_brief(self.settings, story_md, repair=True)
            errors = brief.validate()
            if errors:
                raise VisualBriefError(" | ".join(errors))
        return brief

    def _should_call_openai(self) -> bool:
        return (
            self.mode != "test"
            and self.settings.openai_image_enabled
            and bool(self.settings.openai_api_key)
        )

    def _resolve_use_references(self, override: bool | None) -> bool:
        if override is not None:
            return override
        return self.settings.image_use_style_references

    def _reference_paths(self) -> tuple[Path, Path]:
        line_ref = self.settings.image_line_art_reference or (
            self.settings.project_root / "assets/reference/line_art_reference.png"
        )
        poster_ref = self.settings.image_poster_reference or (
            self.settings.project_root / "assets/reference/poster_reference.png"
        )
        return line_ref, poster_ref

    def _write_manifest(self, paths: VisualPaths, result: VisualGenerationResult, records: list) -> None:
        serializable_records = []
        for record in records:
            item = dict(record)
            if "output_path" in item:
                item["output_path"] = str(item["output_path"])
            serializable_records.append(item)
        manifest = {
            "model": result.model,
            "quality": result.quality,
            "reference_images_used": result.reference_images_used,
            "dry_run": result.dry_run,
            "line_art_status": result.line_art_status,
            "poster_status": result.poster_status,
            "quality_score": result.quality_score,
            "requested_sizes": result.requested_sizes,
            "actual_sizes": result.actual_sizes,
            "issues": result.issues,
            "generations": serializable_records,
        }
        paths.visual_generation_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
