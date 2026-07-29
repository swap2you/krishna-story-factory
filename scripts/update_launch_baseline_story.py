#!/usr/bin/env python3
"""Refresh one story's locked hashes in the launch safety baseline.

Targeted on purpose: regenerating the whole baseline would drop the archive
supersession fields the hash guard relies on. Existing archive entries for other
versions are preserved untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "releases" / "BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json"
REQUIRED = (
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(folder: Path) -> dict[str, str]:
    out = {}
    for name in REQUIRED:
        path = folder / name
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        out[name] = sha(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story", default="009")
    parser.add_argument(
        "--archive-version",
        action="append",
        default=[],
        metavar="VERSION",
        help="Also record hashes for output/_archive/pre-copyright/<story>/<VERSION>",
    )
    args = parser.parse_args()

    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    entry = data["stories"][args.story]
    folder = ROOT / "output" / entry["folder"]
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))

    old_version = entry.get("version")
    old_poster = (entry.get("file_sha256") or {}).get("story_poster.png")
    entry["version"] = manifest.get("version")
    entry["file_sha256"] = hashes(folder)

    for version in args.archive_version:
        archive = ROOT / "output" / "_archive" / "pre-copyright" / args.story / version
        if not archive.is_dir():
            raise SystemExit(f"missing archive {archive}")
        key = "prior_" + version.replace(".", "_").replace("-", "_") + "_sha256"
        entry[key] = hashes(archive)
        entry["archive_" + version.replace(".", "_").replace("-", "_")] = (
            f"output/_archive/pre-copyright/{args.story}/{version}"
        )

    data["updated_for"] = manifest.get("version")
    data["recorded_at"] = datetime.now(timezone.utc).isoformat()
    BASELINE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"story {args.story}: {old_version} -> {entry['version']}")
    print(f"  story_poster.png {old_poster} -> {entry['file_sha256']['story_poster.png']}")
    for version in args.archive_version:
        print(f"  recorded archive {version}")
    print(f"wrote {BASELINE}")

    _refresh_portal_lock(args.story, folder, manifest)
    _refresh_v11_baseline(args.story, folder, manifest)
    return 0


def _refresh_portal_lock(story: str, folder: Path, manifest: dict) -> None:
    """Portal drift guard records uppercase hashes for the same eight files."""
    lock_file = ROOT / "data" / "catalog" / "locked_story_hashes.json"
    if not lock_file.is_file():
        return
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    stories = data.get("stories") or {}
    if story not in stories:
        return
    stories[story] = {name: value.upper() for name, value in hashes(folder).items()}
    data["updated_for"] = f"poster_text_unicode_{manifest.get('version')}"
    data["recorded_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    lock_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {lock_file}")


def _refresh_v11_baseline(story: str, folder: Path, manifest: dict) -> None:
    """The V1.1 safety baseline covers Stories 001-007 only."""
    baseline = ROOT / "docs" / "releases" / "BHAVA_V1_1_SAFETY_BASELINE.json"
    if not baseline.is_file():
        return
    data = json.loads(baseline.read_text(encoding="utf-8"))
    stories = data.get("stories") or {}
    if story not in stories:
        return
    entry = stories[story]
    entry["files"] = hashes(folder)
    entry["version"] = manifest.get("version")
    entry["note"] = "Poster title/caption bands rebuilt with the validated Unicode font."
    data["updated_for"] = f"poster_text_unicode_{manifest.get('version')}"
    baseline.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {baseline}")


if __name__ == "__main__":
    raise SystemExit(main())
