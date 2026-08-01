#!/usr/bin/env python3
"""Locally recompose Stories 001–020 poster title/caption bands (no paid APIs).

Uses the finished-poster recovery path: strip credit → extract art → compose_poster
→ append credit. Artwork pixels are not regenerated.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from krishna_story_factory.publication.identity import load_identity  # noqa: E402
from krishna_story_factory.publication.poster_text import (  # noqa: E402
    has_text_bands,
    poster_band_crops,
    rebuild_poster_from_finished,
)
from krishna_story_factory.publication.work_manifest import first_publication_year  # noqa: E402

# Known published poster captions (preserve wording; title typography only).
KNOWN_CAPTIONS = {
    "007": "Yoga-māyā warns Kaṁsa; soft hearts need good association.",
    "009": "Kṛṣṇa’s mercy is greater than anyone's faults.",
}


def poster_caption(story_md: str) -> str:
    visible = story_md.split("<!--", 1)[0]
    match = re.search(r"##\s+Five Lessons\s*\n(.*?)(?=\n##\s|\Z)", visible, re.DOTALL)
    if not match:
        raise SystemExit("Could not locate Five Lessons for caption.")
    lessons = [
        re.sub(r"^\d+\.\s*", "", line).strip()
        for line in match.group(1).splitlines()
        if line.strip()
    ]
    if not lessons:
        raise SystemExit("Five Lessons empty.")
    return lessons[-1]


def packages(output: Path) -> list[Path]:
    found: list[Path] = []
    for n in range(1, 21):
        matches = [p for p in sorted(output.glob(f"{n:03d}_*")) if (p / "manifest.json").is_file()]
        if len(matches) != 1:
            raise SystemExit(f"Expected one package for {n:03d}, found {matches}")
        found.append(matches[0])
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT / "output")
    parser.add_argument("--only", nargs="*", default=None, help="Optional story numbers, e.g. 019")
    args = parser.parse_args()
    identity = load_identity()
    selected = {s.zfill(3) for s in args.only} if args.only else None

    report: list[dict] = []
    for package in packages(args.output_root):
        story_no = package.name.split("_", 1)[0]
        if selected and story_no not in selected:
            continue
        poster = package / "story_poster.png"
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        title = str(manifest.get("title") or "")
        if not has_text_bands(poster):
            report.append({"story_no": story_no, "status": "skipped_no_text_bands", "title": title})
            print(f"{story_no}: skip (no title/caption bands)")
            continue
        prior_note = (
            ((manifest.get("publication") or {}).get("artifact_notes") or {})
            .get("images")
            or {}
        ).get("story_poster.png") or {}
        caption = (
            KNOWN_CAPTIONS.get(story_no)
            or prior_note.get("caption_text")
            or poster_caption((package / "story.md").read_text(encoding="utf-8"))
        )
        # Do not keep a previously bad Five-Lessons substitute for known captions.
        if story_no in KNOWN_CAPTIONS:
            caption = KNOWN_CAPTIONS[story_no]
        year = first_publication_year(
            {"status": "publicly_available_unreviewed", "first_publication_date": None}
        )
        ai_image = bool((manifest.get("images") or {}).get("model"))
        staging = args.output_root / "_staging" / f"poster-title-{package.name}"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        dest = staging / "story_poster.png"
        note = rebuild_poster_from_finished(
            poster,
            dest,
            title=title,
            caption=caption,
            year=year,
            ai_image=ai_image,
            identity=identity,
        )
        # Quick geometry sanity: title crop must contain non-backdrop ink.
        crops = poster_band_crops(dest)
        title_band = crops["title"]
        ink = any(
            title_band.getpixel((x, y)) != (0x12, 0x0C, 0x06)
            for y in range(2, title_band.height - 2, 3)
            for x in range(2, title_band.width - 2, 12)
        )
        if not ink:
            raise SystemExit(f"{story_no}: recomposed title band has no ink")
        shutil.copy2(dest, poster)
        publication = dict(manifest.get("publication") or {})
        notes = dict(publication.get("artifact_notes") or {})
        images = dict(notes.get("images") or {})
        images["story_poster.png"] = {
            **(images.get("story_poster.png") or {}),
            **note,
            "title_bounds_fix": "d12-v3",
        }
        notes["images"] = images
        publication["artifact_notes"] = notes
        manifest["publication"] = publication
        (package / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        report.append(
            {
                "story_no": story_no,
                "status": "recomposed",
                "title": title,
                "title_band_h": crops["title"].size[1],
                "composed_size": note.get("composed_size"),
            }
        )
        print(f"{story_no}: recomposed title band h={crops['title'].size[1]} :: {title}")

    out_report = ROOT / "work" / "poster_title_recompose_001_020.json"
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out_report}")


if __name__ == "__main__":
    main()
