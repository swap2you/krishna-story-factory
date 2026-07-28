#!/usr/bin/env python3
"""Corrected Unicode copyright retrofit → package version 2.1.1-copyright.

Archives current 2.1.0-copyright packages, rebuilds image strips and PDF overlays
from clean 2.0 masters with a Unicode-complete font, preserves narrative and
audio stream, then atomically swaps public packages.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from krishna_story_factory.outputs import FINAL_OUTPUT_FILES  # noqa: E402
from krishna_story_factory.package_swap import (  # noqa: E402
    atomic_replace_package_dir,
    sha256_file,
    validate_exact_eight_files,
)
from krishna_story_factory.publication.artifacts import (  # noqa: E402
    append_image_credit_strip,
    apply_caption_notice,
    apply_story_md_rights,
    stamp_pdf_footer,
    write_audio_metadata,
)
from krishna_story_factory.publication.fonts import resolve_unicode_fonts  # noqa: E402
from krishna_story_factory.publication.identity import load_identity  # noqa: E402
from krishna_story_factory.publication.work_manifest import (  # noqa: E402
    build_story_rights_block,
    first_publication_year,
    validate_work_manifest,
)

NEW_VERSION = "2.1.1-copyright"
PRIOR_VERSION = "2.1.0-copyright"
MASTER_VERSION = "2.0"


def discover_story_packages(output_root: Path) -> list[Path]:
    packages: list[Path] = []
    for chapter in range(1, 10):
        matches = [p for p in sorted(output_root.glob(f"{chapter:03d}_*")) if p.is_dir() and (p / "manifest.json").is_file()]
        if len(matches) != 1:
            raise SystemExit(f"Expected exactly one package for {chapter:03d}, found {matches}")
        packages.append(matches[0])
    return packages


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


def master_path(archive_root: Path, story_no: str, filename: str) -> Path:
    path = archive_root / story_no / MASTER_VERSION / filename
    if not path.is_file():
        raise SystemExit(f"Missing clean master {path}")
    return path


def narrative_before_rights(text: str) -> str:
    idx = text.find("## Rights and Credits")
    if idx >= 0:
        return text[:idx].rstrip()
    comment = text.find("<!--")
    return text[:comment].rstrip() if comment >= 0 else text.rstrip()


def build_replacement(
    package: Path,
    staging_root: Path,
    archive_root: Path,
    identity,
) -> tuple[Path, dict]:
    story_no = package.name.split("_", 1)[0]
    staging = staging_root / package.name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    current = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    prior_hashes = {name: sha256_file(package / name).lower() for name in FINAL_OUTPUT_FILES}
    year = first_publication_year(
        {"status": "publicly_available_unreviewed", "first_publication_date": None}
    )
    work_id = f"bhava-kb-bedtime-{story_no}"

    # story.md: rebuild from clean 2.0 master narrative + refreshed Rights section.
    master_story = master_path(archive_root, story_no, "story.md").read_text(encoding="utf-8")
    master_before = narrative_before_rights(master_story)
    (staging / "story.md").write_text(
        apply_story_md_rights(
            master_story,
            work_id=work_id,
            version=NEW_VERSION,
            source_reference=current.get("source_reference"),
            scripture_reference=current.get("scripture_reference"),
            year=year,
            identity=identity,
        ),
        encoding="utf-8",
    )
    new_before = narrative_before_rights((staging / "story.md").read_text(encoding="utf-8"))
    if new_before != master_before:
        raise SystemExit(f"Narrative drift for {story_no}")

    # Caption from master + notice
    caption = master_path(archive_root, story_no, "whatsapp_caption.txt").read_text(encoding="utf-8")
    (staging / "whatsapp_caption.txt").write_text(
        apply_caption_notice(caption, year=year, identity=identity),
        encoding="utf-8",
    )

    # Images from clean 2.0 masters (never from already-credited 2.1.0)
    image_notes = {}
    ai_image = bool((current.get("images") or {}).get("model"))
    for image_name in ("story_poster.png", "coloring_page.png", "simple_coloring_page.png"):
        image_notes[image_name] = append_image_credit_strip(
            master_path(archive_root, story_no, image_name),
            staging / image_name,
            year=year,
            ai_image=ai_image and image_name == "story_poster.png",
            identity=identity,
        )

    # PDF from clean 2.0 master + per-page footer overlay + rights page
    pdf_note = stamp_pdf_footer(
        master_path(archive_root, story_no, "activity_sheet.pdf"),
        staging / "activity_sheet.pdf",
        year=year,
        identity=identity,
    )

    # Audio: copy current tagged file without re-encode; skip rewrite when tags present
    audio = current.get("audio") or {}
    sound_status = "needs_manual_review"
    audio_note = write_audio_metadata(
        package / "narration.mp3",
        staging / "narration.mp3",
        title=str(current.get("title") or f"Story {story_no}"),
        year=year,
        identity=identity,
        sound_recording_claim_status=sound_status,
        rights_url="https://bhava.me/rights",
        rewrite_if_present=False,
    )

    new_hashes = {name: sha256_file(staging / name).lower() for name in FINAL_OUTPUT_FILES if name != "manifest.json"}
    ai_assistance = {
        "story_text": "human_edited_adaptation",
        "images": {
            "provider_model": (current.get("images") or {}).get("model"),
            "human_modification": "bottom_credit_strip_unicode_font",
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
    # Placeholder hashes for rights block; updated after manifest write.
    rights = build_story_rights_block(
        story_no=story_no,
        title=str(current.get("title")),
        version=NEW_VERSION,
        supersedes=PRIOR_VERSION,
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
    rights["correction_history"] = list(rights.get("correction_history") or []) + [
        {
            "change": "unicode_font_and_per_page_pdf_footer",
            "from_version": PRIOR_VERSION,
            "to_version": NEW_VERSION,
            "note": "Unicode-complete font for rights/PDF/PNG; per-page compact footer; strips rebuilt from 2.0 masters.",
        }
    ]
    rights_errors = validate_work_manifest(rights)
    if rights_errors:
        raise SystemExit(f"Rights validation failed for {story_no}: {rights_errors}")

    manifest = dict(current)
    manifest["version"] = NEW_VERSION
    manifest["rights"] = rights
    manifest["publication"] = {
        "copyright_owner": identity.copyright_owner,
        "publisher": identity.publisher,
        "project": identity.project,
        "contact_email": identity.contact_email,
        "location": identity.location,
        "phone": None,
        "supersedes": PRIOR_VERSION,
        "archive_relative": f"_archive/pre-copyright/{story_no}/{PRIOR_VERSION}",
        "masters_relative": f"_archive/pre-copyright/{story_no}/{MASTER_VERSION}",
        "artifact_notes": {"images": image_notes, "pdf": pdf_note, "audio": audio_note},
        "unicode_font": str(resolve_unicode_fonts().regular_path),
        "drive_status_note": (
            "Drive still contains an earlier package version. Manual Drive update "
            "required; this pass does not mutate Drive."
        ),
    }
    manifest["publishable"] = True
    (staging / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    new_hashes["manifest.json"] = sha256_file(staging / "manifest.json").lower()
    manifest["rights"]["sha256"] = new_hashes
    (staging / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    new_hashes["manifest.json"] = sha256_file(staging / "manifest.json").lower()

    errors = validate_exact_eight_files(staging)
    if errors:
        raise SystemExit(f"Exact-eight failed for staging {story_no}: {errors}")

    report = {
        "story_no": story_no,
        "folder": package.name,
        "prior_version": PRIOR_VERSION,
        "new_version": NEW_VERSION,
        "prior_sha256": prior_hashes,
        "new_sha256": new_hashes,
        "narrative_unchanged_vs_2_0": True,
        "artifact_notes": {"images": image_notes, "pdf": pdf_note, "audio": audio_note},
    }
    return staging, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--force", action="store_true", help="Rebuild even when already on NEW_VERSION")
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs" / "legal" / "_generated" / "package_version_migration_2_1_1.json",
    )
    args = parser.parse_args()

    fonts = resolve_unicode_fonts()
    print(f"Unicode font: {fonts.regular_path}")

    identity = load_identity(ROOT)
    output_root = ROOT / "output"
    archive_root = output_root / "_archive" / "pre-copyright"
    staging_root = output_root / "_staging" / "copyright-unicode-fix"
    staging_root.mkdir(parents=True, exist_ok=True)

    packages = discover_story_packages(output_root)
    reports = []
    staging_dirs: list[tuple[Path, Path, dict]] = []

    for package in packages:
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        if str(manifest.get("version")) == NEW_VERSION and not args.force:
            print(f"SKIP {package.name}: already {NEW_VERSION}")
            continue
        archive_version = str(manifest.get("version") or PRIOR_VERSION)
        if archive_version == NEW_VERSION:
            archive_version = f"{NEW_VERSION}-pre-rebuild"
        archive_path = archive_package(package, archive_root, archive_version)
        staging, report = build_replacement(package, staging_root, archive_root, identity)
        report["archive_path"] = str(archive_path)
        reports.append(report)
        staging_dirs.append((package, staging, report))
        print(f"STAGED {report['story_no']}")

    if args.apply:
        swap_archive = output_root / "_archive" / "copyright-swap-backups"
        swap_archive.mkdir(parents=True, exist_ok=True)
        for production, staging, report in staging_dirs:
            atomic_replace_package_dir(
                production_dir=production,
                staging_dir=staging,
                archive_root=swap_archive,
                output_root=output_root,
                project_root=ROOT,
            )
            print(f"SWAPPED {report['story_no']}")
    else:
        print("Dry-run only. Re-run with --apply to swap.")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "new_version": NEW_VERSION,
        "prior_version": PRIOR_VERSION,
        "unicode_font": str(fonts.regular_path),
        "identity": {
            "copyright_owner": identity.copyright_owner,
            "publisher": identity.publisher,
            "project": identity.project,
            "contact_email": identity.contact_email,
            "phone": None,
        },
        "stories": reports,
        "applied": bool(args.apply),
    }
    args.report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
