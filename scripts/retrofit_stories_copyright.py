#!/usr/bin/env python3
"""Versioned copyright retrofit for Stories 001–009 (no silent overwrite).

Archives each current public package under output/_archive/pre-copyright/,
builds exact-eight replacements in staging, validates, then atomically swaps.
Does not call paid providers, regenerate narrative/TTS/images, or touch Drive.
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
from krishna_story_factory.publication.identity import load_identity  # noqa: E402
from krishna_story_factory.publication.work_manifest import (  # noqa: E402
    build_story_rights_block,
    first_publication_year,
    validate_work_manifest,
)

NEW_VERSION = "2.1.0-copyright"
PRIOR_VERSION_DEFAULT = "2.0"


def discover_story_packages(output_root: Path) -> list[Path]:
    packages: list[Path] = []
    for chapter in range(1, 10):
        matches = sorted(output_root.glob(f"{chapter:03d}_*"))
        matches = [p for p in matches if p.is_dir() and (p / "manifest.json").is_file()]
        if len(matches) != 1:
            raise SystemExit(f"Expected exactly one package for {chapter:03d}, found {matches}")
        packages.append(matches[0])
    return packages


def inventory_package(package: Path) -> dict:
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    hashes = {name: sha256_file(package / name).lower() for name in FINAL_OUTPUT_FILES}
    return {
        "folder": package.name,
        "path": str(package),
        "title": manifest.get("title"),
        "slug": manifest.get("slug"),
        "chapter_no": str(manifest.get("chapter_no")).zfill(3),
        "manifest_version": manifest.get("version"),
        "source_reference": manifest.get("source_reference"),
        "scripture_reference": manifest.get("scripture_reference"),
        "generated_at": manifest.get("generated_at"),
        "audio": manifest.get("audio") or {},
        "images": manifest.get("images") or {},
        "file_sha256": hashes,
    }


def archive_package(package: Path, archive_root: Path, version: str) -> Path:
    story_no = package.name.split("_", 1)[0]
    dest = archive_root / story_no / version
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(package, dest)
    (dest / "_ARCHIVE_NOTE.txt").write_text(
        "Pre-copyright public package archive. Not for public catalog exposure.\n",
        encoding="utf-8",
    )
    return dest


def build_replacement(
    package: Path,
    staging_root: Path,
    prior: dict,
    identity,
) -> tuple[Path, dict]:
    story_no = prior["chapter_no"]
    staging = staging_root / package.name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    # Start from a full copy, then rewrite notice-bearing artifacts.
    for name in FINAL_OUTPUT_FILES:
        shutil.copy2(package / name, staging / name)

    year = first_publication_year(
        {
            "status": "publicly_available_unreviewed",
            "first_publication_date": None,
        }
    )
    work_id = f"bhava-kb-bedtime-{story_no}"
    prior_version = str(prior.get("manifest_version") or PRIOR_VERSION_DEFAULT)

    story_text = (staging / "story.md").read_text(encoding="utf-8")
    (staging / "story.md").write_text(
        apply_story_md_rights(
            story_text,
            work_id=work_id,
            version=NEW_VERSION,
            source_reference=prior.get("source_reference"),
            scripture_reference=prior.get("scripture_reference"),
            year=year,
            identity=identity,
        ),
        encoding="utf-8",
    )

    caption = (staging / "whatsapp_caption.txt").read_text(encoding="utf-8")
    (staging / "whatsapp_caption.txt").write_text(
        apply_caption_notice(caption, year=year, identity=identity),
        encoding="utf-8",
    )

    image_notes = {}
    ai_image = bool((prior.get("images") or {}).get("model"))
    for image_name in ("story_poster.png", "coloring_page.png", "simple_coloring_page.png"):
        image_notes[image_name] = append_image_credit_strip(
            staging / image_name,
            staging / image_name,
            year=year,
            ai_image=ai_image and image_name == "story_poster.png",
            identity=identity,
        )

    pdf_note = stamp_pdf_footer(
        staging / "activity_sheet.pdf",
        staging / "activity_sheet.pdf",
        year=year,
        identity=identity,
    )

    audio = prior.get("audio") or {}
    sound_status = "needs_manual_review"
    if str(audio.get("provider") or "").lower() in {"openai", "tts", "elevenlabs"}:
        sound_status = "needs_manual_review"
    audio_note = write_audio_metadata(
        staging / "narration.mp3",
        staging / "narration.mp3",
        title=str(prior.get("title") or f"Story {story_no}"),
        year=year,
        identity=identity,
        sound_recording_claim_status=sound_status,
        rights_url="https://bhava.me/rights",
    )

    new_hashes = {name: sha256_file(staging / name).lower() for name in FINAL_OUTPUT_FILES}
    ai_assistance = {
        "story_text": "human_edited_adaptation",
        "images": {
            "provider_model": (prior.get("images") or {}).get("model"),
            "human_modification": "bottom_credit_strip_and_publication_design",
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
        title=str(prior.get("title")),
        version=NEW_VERSION,
        supersedes=prior_version,
        source_reference=prior.get("source_reference"),
        scripture_reference=prior.get("scripture_reference"),
        file_sha256=new_hashes,
        prior_sha256=prior["file_sha256"],
        identity=identity,
        ai_assistance=ai_assistance,
        human_authorship_claim=human_authorship,
        sound_recording_claim_status=sound_status,
        status="publicly_available_unreviewed",
        first_publication_date=None,
    )
    rights_errors = validate_work_manifest(rights)
    if rights_errors:
        raise SystemExit(f"Rights validation failed for {story_no}: {rights_errors}")

    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    manifest["version"] = NEW_VERSION
    manifest["rights"] = rights
    manifest["publication"] = {
        "copyright_owner": identity.copyright_owner,
        "publisher": identity.publisher,
        "project": identity.project,
        "contact_email": identity.contact_email,
        "location": identity.location,
        "phone": None,
        "supersedes": prior_version,
        "archive_relative": f"_archive/pre-copyright/{story_no}/{prior_version}",
        "artifact_notes": {
            "images": image_notes,
            "pdf": pdf_note,
            "audio": audio_note,
        },
        "drive_status_note": (
            "Drive still contains the earlier package version. Manual Drive update "
            "required; this pass does not mutate Drive."
        ),
    }
    # Keep publish gates intact.
    manifest["publishable"] = True
    (staging / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Recompute manifest hash after write.
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
        "prior_version": prior_version,
        "new_version": NEW_VERSION,
        "prior_sha256": prior["file_sha256"],
        "new_sha256": new_hashes,
        "rights_validation": rights_errors,
        "artifact_notes": {"images": image_notes, "pdf": pdf_note, "audio": audio_note},
    }
    return staging, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Perform archive + atomic swap")
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs" / "legal" / "_generated" / "story_version_migration.json",
    )
    args = parser.parse_args()

    identity = load_identity(ROOT)
    output_root = ROOT / "output"
    archive_root = output_root / "_archive" / "pre-copyright"
    staging_root = output_root / "_staging" / "copyright-retrofit"
    staging_root.mkdir(parents=True, exist_ok=True)

    packages = discover_story_packages(output_root)
    reports = []
    staging_dirs: list[tuple[Path, Path, dict]] = []

    for package in packages:
        prior = inventory_package(package)
        # Skip if already on copyright version and archive exists.
        if str(prior.get("manifest_version")) == NEW_VERSION:
            print(f"SKIP {prior['chapter_no']}: already {NEW_VERSION}")
            reports.append({"story_no": prior["chapter_no"], "skipped": True, **prior})
            continue
        archive_path = archive_package(
            package,
            archive_root,
            str(prior.get("manifest_version") or PRIOR_VERSION_DEFAULT),
        )
        staging, report = build_replacement(package, staging_root, prior, identity)
        report["archive_path"] = str(archive_path)
        reports.append(report)
        staging_dirs.append((package, staging, report))
        print(f"STAGED {prior['chapter_no']} -> {staging}")

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
