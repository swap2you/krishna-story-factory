#!/usr/bin/env python3
"""Artifact correction → package version 2.1.2-copyright (poster text glyphs).

Rebuilds a story poster's title and caption bands with the validated Unicode font
resolver, starting from the clean pre-credit 2.0 artwork master. The narrative,
narration audio, PDF, coloring pages and caption file are carried over from the
live package byte-for-byte; only story_poster.png is re-rendered and only
story.md's Rights-section version stamp changes for bookkeeping consistency.

This is an artifact correction inside the existing Bhāva Stories Production
Launch. It is not a new product release. It calls no image or TTS provider.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from krishna_story_factory.outputs import FINAL_OUTPUT_FILES  # noqa: E402
from krishna_story_factory.package_swap import (  # noqa: E402
    atomic_replace_package_dir,
    sha256_file,
    validate_exact_eight_files,
)
from krishna_story_factory.publication.fonts import resolve_unicode_fonts  # noqa: E402
from krishna_story_factory.publication.identity import load_identity  # noqa: E402
from krishna_story_factory.publication.notices import image_credit_line  # noqa: E402
from krishna_story_factory.publication.poster_text import (  # noqa: E402
    count_missing_glyph_boxes,
    poster_band_crops,
    rebuild_poster_from_master,
    validate_poster_text,
    verify_legacy_text_preserved,
)
from krishna_story_factory.publication.work_manifest import (  # noqa: E402
    build_story_rights_block,
    first_publication_year,
    validate_work_manifest,
)

NEW_VERSION = "2.1.2-copyright"
MASTER_VERSION = "2.0"
CARRIED_FILES = (
    "narration.mp3",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
)


def find_package(output_root: Path, story_no: str) -> Path:
    matches = [p for p in sorted(output_root.glob(f"{story_no}_*")) if (p / "manifest.json").is_file()]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one package for {story_no}, found {matches}")
    return matches[0]


def narrative_before_rights(text: str) -> str:
    idx = text.find("## Rights and Credits")
    if idx >= 0:
        return text[:idx].rstrip()
    comment = text.find("<!--")
    return text[:comment].rstrip() if comment >= 0 else text.rstrip()


def restamp_story_version(story_md: str, old_version: str, new_version: str) -> str:
    """Replace the single Rights-section version stamp, touching nothing else."""
    marker = f"- Version: `{old_version}`"
    if story_md.count(marker) != 1:
        raise SystemExit(
            f"Expected exactly one {marker!r} line in story.md, found {story_md.count(marker)}."
        )
    return story_md.replace(marker, f"- Version: `{new_version}`")


def poster_caption(story_md: str) -> str:
    """Mirror pipeline's caption source: the last of the Five Lessons."""
    visible = story_md.split("<!--", 1)[0]
    match = re.search(r"##\s+Five Lessons\s*\n(.*?)(?=\n##\s|\Z)", visible, re.DOTALL)
    if not match:
        raise SystemExit("Could not locate the Five Lessons section for the poster caption.")
    lessons = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in match.group(1).splitlines()
        if line.strip()
    ]
    if not lessons:
        raise SystemExit("Five Lessons section is empty; cannot derive poster caption.")
    return lessons[-1]


def archive_package(package: Path, archive_root: Path, version: str) -> Path:
    story_no = package.name.split("_", 1)[0]
    dest = archive_root / story_no / version
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package, dest)
    (dest / "_ARCHIVE_NOTE.txt").write_text(
        f"Archived public package version {version}. Not for public catalog exposure.\n",
        encoding="utf-8",
    )
    return dest


def build_replacement(
    package: Path,
    staging_root: Path,
    archive_root: Path,
    identity,
    caption_override: str | None = None,
) -> tuple[Path, dict]:
    story_no = package.name.split("_", 1)[0]
    staging = staging_root / package.name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    current = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    live_version = str(current.get("version") or "")
    if live_version == NEW_VERSION:
        raise SystemExit(f"{package.name} is already {NEW_VERSION}; nothing to correct.")
    prior_hashes = {name: sha256_file(package / name).lower() for name in FINAL_OUTPUT_FILES}
    year = first_publication_year(
        {"status": "publicly_available_unreviewed", "first_publication_date": None}
    )
    work_id = f"bhava-kb-bedtime-{story_no}"

    # Carry the untouched public files across byte-for-byte.
    for name in CARRIED_FILES:
        shutil.copy2(package / name, staging / name)

    # story.md: bump only the Rights-section version stamp. Regenerating the whole
    # section would also churn unrelated whitespace, so restamp surgically.
    live_story = (package / "story.md").read_text(encoding="utf-8")
    staged_story = restamp_story_version(live_story, live_version, NEW_VERSION)
    (staging / "story.md").write_text(staged_story, encoding="utf-8")
    if staged_story.replace(NEW_VERSION, live_version) != live_story:
        raise SystemExit(
            f"story.md changed beyond the version stamp for {story_no}; refusing to continue."
        )
    if narrative_before_rights(staged_story) != narrative_before_rights(live_story):
        raise SystemExit(f"Narrative drift for {story_no}; refusing to continue.")
    master_story = (archive_root / story_no / MASTER_VERSION / "story.md").read_text(encoding="utf-8")
    if narrative_before_rights(staged_story) != narrative_before_rights(master_story):
        raise SystemExit(f"Narrative drift vs 2.0 master for {story_no}; refusing to continue.")

    # Poster: recompose title/caption from clean 2.0 artwork with Unicode fonts.
    title = str(current.get("title") or "")
    caption = caption_override if caption_override is not None else poster_caption(live_story)
    ai_image = bool((current.get("images") or {}).get("model"))
    credit = image_credit_line(year=year, ai_image=ai_image, identity=identity)
    glyphs = validate_poster_text(title, caption, credit)
    if not glyphs["ok"]:
        raise SystemExit(f"Poster text glyph validation failed for {story_no}: {glyphs}")
    master_poster = archive_root / story_no / MASTER_VERSION / "story_poster.png"
    if not master_poster.is_file():
        raise SystemExit(f"Missing clean poster master {master_poster}")

    # Prove the wording is preserved: rendering these exact strings with the old
    # default font must reproduce the live poster's bands byte-for-byte.
    with Image.open(master_poster) as master_img:
        composed_size = master_img.size
    preserved = verify_legacy_text_preserved(
        package / "story_poster.png", composed_size, title, caption
    )
    if not (preserved["title_preserved"] and preserved["caption_preserved"]):
        raise SystemExit(
            f"Refusing to rebuild {story_no}: the supplied title/caption do not reproduce "
            f"the current poster text ({preserved}). Rebuilding would silently change "
            "visible wording rather than only repairing glyphs."
        )

    poster_note = rebuild_poster_from_master(
        master_poster,
        staging / "story_poster.png",
        title=title,
        caption=caption,
        year=year,
        ai_image=ai_image,
        identity=identity,
    )
    poster_note["wording_preserved_vs_previous_version"] = preserved

    # The rebuilt bands must contain no missing-glyph boxes.
    fonts_pair = resolve_unicode_fonts()
    crops = poster_band_crops(staging / "story_poster.png")
    boxes = {
        "title": count_missing_glyph_boxes(crops["title"], fonts_pair.pillow_bold(42)),
        "caption": count_missing_glyph_boxes(crops["caption"], fonts_pair.pillow_regular(24)),
        "credit": count_missing_glyph_boxes(crops["credit"], fonts_pair.pillow_regular(20)),
    }
    if any(boxes.values()):
        raise SystemExit(f"Rebuilt poster for {story_no} still shows missing-glyph boxes: {boxes}")
    poster_note["missing_glyph_boxes"] = boxes

    new_hashes = {
        name: sha256_file(staging / name).lower()
        for name in FINAL_OUTPUT_FILES
        if name != "manifest.json"
    }
    for name in CARRIED_FILES:
        if new_hashes[name] != prior_hashes[name]:
            raise SystemExit(f"Carried file {name} changed for {story_no}; refusing to continue.")

    audio = current.get("audio") or {}
    sound_status = "needs_manual_review"
    ai_assistance = {
        "story_text": "human_edited_adaptation",
        "images": {
            "provider_model": (current.get("images") or {}).get("model"),
            "human_modification": "poster_title_caption_and_credit_strip_unicode_font",
            "full_image_copyright_claim": "limited" if ai_image else "standard",
        },
        "audio": {
            "provider": audio.get("provider"),
            "model_id": audio.get("model_id"),
            "voice": audio.get("voice"),
            "human_editing_and_production": True,
            "sound_recording_claim_status": sound_status,
        },
    }
    human_authorship = (
        "Original child-friendly adaptation, selection and arrangement, educational "
        "activities, editing, graphic publication design, and production packaging "
        f"by {identity.copyright_owner}. Prompting alone is not claimed as authorship."
    )
    rights = build_story_rights_block(
        story_no=story_no,
        title=title,
        version=NEW_VERSION,
        supersedes=live_version,
        source_reference=current.get("source_reference"),
        scripture_reference=current.get("scripture_reference"),
        file_sha256=new_hashes,
        prior_sha256=prior_hashes,
        identity=identity,
        ai_assistance=ai_assistance,
        human_authorship_claim=human_authorship,
        sound_recording_claim_status=sound_status,
        status="publicly_available_unreviewed",
        first_publication_date=None,
    )
    rights["correction_history"] = list(
        (current.get("rights") or {}).get("correction_history") or []
    ) + [
        {
            "change": "poster_title_and_caption_unicode_font",
            "from_version": live_version,
            "to_version": NEW_VERSION,
            "note": (
                "Poster title and caption bands were composited with Pillow's default "
                "bitmap font, rendering Sanskrit diacritics and the em dash as "
                "missing-glyph boxes. Both bands plus the credit strip are now drawn "
                "with the validated Unicode font resolver from the clean 2.0 artwork "
                "master. Artwork pixels, narrative and narration are unchanged."
            ),
        }
    ]
    rights_errors = validate_work_manifest(rights)
    if rights_errors:
        raise SystemExit(f"Rights validation failed for {story_no}: {rights_errors}")

    prior_publication = dict(current.get("publication") or {})
    prior_notes = dict((prior_publication.get("artifact_notes") or {}))
    image_notes = dict(prior_notes.get("images") or {})
    image_notes["story_poster.png"] = poster_note
    fonts = resolve_unicode_fonts()

    manifest = dict(current)
    manifest["version"] = NEW_VERSION
    manifest["rights"] = rights
    manifest["publication"] = {
        **prior_publication,
        "supersedes": live_version,
        "archive_relative": f"_archive/pre-copyright/{story_no}/{live_version}",
        "masters_relative": f"_archive/pre-copyright/{story_no}/{MASTER_VERSION}",
        "artifact_notes": {
            "images": image_notes,
            "pdf": prior_notes.get("pdf"),
            "audio": prior_notes.get("audio"),
        },
        "unicode_font": str(fonts.regular_path),
        "unicode_font_bold": str(fonts.bold_path),
        "poster_text_glyph_validation": glyphs,
    }
    manifest["publishable"] = True
    for _ in range(2):
        (staging / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        new_hashes["manifest.json"] = sha256_file(staging / "manifest.json").lower()
        manifest["rights"]["sha256"] = dict(new_hashes)

    errors = validate_exact_eight_files(staging)
    if errors:
        raise SystemExit(f"Exact-eight failed for staging {story_no}: {errors}")

    report = {
        "story_no": story_no,
        "folder": package.name,
        "prior_version": live_version,
        "new_version": NEW_VERSION,
        "prior_sha256": prior_hashes,
        "new_sha256": new_hashes,
        "changed_files": sorted(
            name for name in FINAL_OUTPUT_FILES if prior_hashes[name] != new_hashes[name]
        ),
        "carried_unchanged": list(CARRIED_FILES),
        "poster_note": poster_note,
        "poster_text_glyph_validation": glyphs,
        "narrative_unchanged_vs_2_0": True,
        "narration_unchanged": prior_hashes["narration.mp3"] == new_hashes["narration.mp3"],
    }
    return staging, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", default="009")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--caption",
        default=None,
        help=(
            "Exact on-poster caption when it is no longer derivable from story.md. "
            "It must reproduce the current poster's caption band byte-for-byte."
        ),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Defaults to docs/legal/_generated/package_version_correction_2_1_2_<story>.json",
    )
    args = parser.parse_args()
    if args.report is None:
        args.report = (
            ROOT
            / "docs"
            / "legal"
            / "_generated"
            / f"package_version_correction_{NEW_VERSION.split('-')[0].replace('.', '_')}_{args.story}.json"
        )

    fonts = resolve_unicode_fonts()
    print(f"Unicode font regular: {fonts.regular_path}")
    print(f"Unicode font bold:    {fonts.bold_path}")

    identity = load_identity(ROOT)
    output_root = ROOT / "output"
    archive_root = output_root / "_archive" / "pre-copyright"
    staging_root = output_root / "_staging" / "poster-unicode-fix"
    staging_root.mkdir(parents=True, exist_ok=True)

    package = find_package(output_root, args.story)
    live_version = str(
        json.loads((package / "manifest.json").read_text(encoding="utf-8")).get("version") or ""
    )
    archive_path = archive_package(package, archive_root, live_version)
    print(f"Archived live {live_version} -> {archive_path}")

    staging, report = build_replacement(
        package, staging_root, archive_root, identity, caption_override=args.caption
    )
    report["archive_path"] = str(archive_path)
    report["archive_label"] = live_version
    print(f"STAGED {report['story_no']}: changed={report['changed_files']}")

    if args.apply:
        swap_archive = output_root / "_archive" / "copyright-swap-backups"
        swap_archive.mkdir(parents=True, exist_ok=True)
        result = atomic_replace_package_dir(
            production_dir=package,
            staging_dir=staging,
            archive_root=swap_archive,
            output_root=output_root,
            project_root=ROOT,
        )
        report["swap_backup_dir"] = result.get("backup_dir", "")
        report["swap_backed_up_version"] = result.get("backed_up_version", "")
        print(
            f"SWAPPED {report['story_no']} "
            f"(backup holds {result.get('backed_up_version') or 'unknown'})"
        )
    else:
        print("Dry-run only. Re-run with --apply to swap.")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            {
                "new_version": NEW_VERSION,
                "release": "BHAVA_STORIES_PRODUCTION_LAUNCH",
                "correction_scope": "story_poster_text_glyphs",
                "unicode_font": str(fonts.regular_path),
                "unicode_font_bold": str(fonts.bold_path),
                "stories": [report],
                "applied": bool(args.apply),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
