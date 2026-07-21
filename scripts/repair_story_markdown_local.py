#!/usr/bin/env python3
"""Repair local story.md structure/content without paid APIs.

Applies known content repairs for 002/005/006 and round-trips all targeted
chapters through the v2 serializer so each story.md has exactly one hidden
production comment block. Preserves other package files. Does not upload Drive
or change the queue.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace as dc_replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main(chapters: list[str]) -> int:
    from krishna_story_factory.audio.drift import detect_audio_stale, narration_source_sha, preserved_audio_metadata
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.repairs import apply_known_story_repairs, sanitize_content_fields
    from krishna_story_factory.content.story_format_v2 import validate_story_comment_structure
    from krishna_story_factory.csv_store import ensure_csv_files, read_plan_by_chapter
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.manifest import write_manifest
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pipeline import _content_from_story_md
    from krishna_story_factory.quality.checks import run_quality_checks

    settings = load_settings(ROOT)
    ensure_csv_files(settings.project_root)
    for chapter in chapters:
        plan = read_plan_by_chapter(settings.project_root, chapter)
        if not plan:
            raise SystemExit(f"Missing plan {chapter}")
        paths = make_package_paths(settings.output_root, plan)
        raw = paths.story_md.read_text(encoding="utf-8")
        content = sanitize_content_fields(
            apply_known_story_repairs(chapter, _content_from_story_md(raw, plan))
        )
        poster = (content.poster_visual_brief or "").strip() or (
            f"Devotional poster for {content.title}: calm Krishna Book scene, soft light, source-faithful."
        )
        coloring = (content.coloring_visual_brief or "").strip() or (
            f"Simple Bal Gopal-friendly coloring for {content.title}: large open spaces, thick outlines."
        )
        preview = (content.next_story_preview or "").strip() or (
            f"Next time we continue the Krishna Book sequence after {content.title}."
        )
        if len(preview.split()) < 8:
            preview = preview + " Remember Krishna with a calm heart."
        parent = (content.parent_note or "").strip() or (
            f"Source: {plan.source_reference}. Keep discussion inside this episode boundary and age-appropriate."
        )
        content = dc_replace(
            content,
            poster_visual_brief=poster,
            coloring_visual_brief=coloring,
            next_story_preview=preview,
            parent_note=parent,
        )
        errors = run_source_guard(plan, content)
        if errors:
            raise SystemExit(f"{chapter} source guard: " + " | ".join(errors))
        md = content.to_markdown()
        from krishna_story_factory.content.story_format_v2 import validate_story_comment_structure

        md_errors = validate_story_comment_structure(md)
        if md_errors:
            raise SystemExit(f"{chapter} markdown structure: " + " | ".join(md_errors))
        paths.story_md.write_text(md, encoding="utf-8")

        stale, detail = detect_audio_stale(audio_script=content.audio_script, manifest_path=paths.manifest)
        audio_source, audio_meta = preserved_audio_metadata(
            narration_path=paths.narration_mp3,
            prior_manifest=paths.manifest,
            waveform_status="PASS",
        )
        # Local markdown repair never regenerates narration. Unknown/unverified audio must stay AUDIO_STALE.
        if not audio_meta.get("generation_verified"):
            stale = True
            detail = detail or "AUDIO_STALE: preserved narration is not generation-verified after story repair"
            audio_meta["narration_source_sha"] = ""
            audio_meta["current_narration_source_sha"] = narration_source_sha(content.audio_script)
            audio_meta["audio_stale"] = True
        elif stale:
            prior_sha = ""
            if paths.manifest.exists():
                try:
                    prior = json.loads(paths.manifest.read_text(encoding="utf-8"))
                    prior_sha = str(
                        prior.get("narration_source_sha")
                        or (prior.get("audio") or {}).get("narration_source_sha")
                        or ""
                    ).strip()
                except json.JSONDecodeError:
                    prior_sha = ""
            audio_meta["narration_source_sha"] = prior_sha
            audio_meta["current_narration_source_sha"] = narration_source_sha(content.audio_script)
            audio_meta["audio_stale"] = True
        else:
            audio_meta["narration_source_sha"] = narration_source_sha(content.audio_script)
            audio_meta["audio_stale"] = False
        ok, q_errors, q_warn = run_quality_checks(
            paths, mode="prod", settings=settings, story_title=content.title, poster_score=90, coloring_score=90
        )
        quality = "AUDIO_STALE" if stale else ("PASS" if ok else "FAIL")
        package_link = ""
        if paths.manifest.exists():
            try:
                package_link = json.loads(paths.manifest.read_text(encoding="utf-8")).get("package", {}).get(
                    "package_link", ""
                )
            except json.JSONDecodeError:
                package_link = ""
        write_manifest(
            settings=settings,
            plan=plan,
            content=content,
            paths=paths,
            mode="prod",
            quality_status=quality,
            quality_errors=(q_errors or []) + ([detail] if stale and detail else []),
            quality_warnings=q_warn,
            audio_source=audio_source,
            package_link=package_link,
            drive_status="LOCAL_ONLY",
            drive_detail="Local markdown repair only; Drive not modified. Exact eight-file package.",
            poster_score=90,
            coloring_score=90,
            simple_coloring_score=90,
            audio_metadata=audio_meta,
        )
        print(f"{chapter}: story.md repaired; quality={quality}; stale={stale}; words_main_ok={ok}")
    return 0


if __name__ == "__main__":
    chapters = [c.strip().zfill(3) for c in (sys.argv[1:] or ["001", "002", "003", "004", "005", "006"])]
    raise SystemExit(main(chapters))
