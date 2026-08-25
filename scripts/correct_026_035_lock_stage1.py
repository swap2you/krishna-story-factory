"""Corrective lock for Stories 026–035: hashes, copy, publish gates. No audio regen."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
EXACT_EIGHT = {
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
}
STAGING_NOTE = "Private staging review. Production publication requires owner approval."
STALE_PATTERNS = [
    re.compile(r"\s*PRIVATE draft\s*[—\-–]?\s*pending owner review\.?", re.I),
    re.compile(r"\s*PRIVATE draft\.?", re.I),
    re.compile(
        r"\s*SENIOR DEVOTIONAL REVIEW REQUIRED before any paid audio or public use\.?",
        re.I,
    ),
    re.compile(r"\s*review required before paid audio\.?", re.I),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def package_dirs() -> list[Path]:
    dirs = []
    for n in range(26, 36):
        matches = sorted(OUTPUT.glob(f"{n:03d}_*"))
        if len(matches) != 1:
            raise SystemExit(f"Expected one package for {n:03d}, found {matches}")
        dirs.append(matches[0])
    return dirs


def rewrite_parent_note(text: str) -> str:
    marker = "## Parent/Teacher Note"
    if marker not in text:
        raise SystemExit("Missing Parent/Teacher Note section")
    before, rest = text.split(marker, 1)
    # rest starts with newline then note body until next ## or HTML comment or EOF
    body_match = re.match(r"(\r?\n)(.*?)(\r?\n## |\r?\n<!--|\Z)", rest, re.S)
    if not body_match:
        raise SystemExit("Could not parse Parent/Teacher Note body")
    nl, body, trailer = body_match.groups()
    cleaned = body.strip()
    for pat in STALE_PATTERNS:
        cleaned = pat.sub("", cleaned).strip()
    # Collapse leftover double spaces from removals
    cleaned = re.sub(r"  +", " ", cleaned)
    if STAGING_NOTE not in cleaned:
        cleaned = f"{cleaned} {STAGING_NOTE}".strip() if cleaned else STAGING_NOTE
    return before + marker + nl + cleaned + trailer


def update_manifest(pkg: Path) -> dict:
    path = pkg / "manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    hashes = {}
    for name in sorted(EXACT_EIGHT - {"manifest.json"}):
        hashes[name] = sha256_file(pkg / name)
    data["file_sha256"] = hashes
    data["publishable"] = False
    data["private_staging_eligible"] = True
    review = dict(data.get("review") or {})
    review.update(
        {
            "private_only": True,
            "public_ceiling": 25,
            "private_staging_allowed": True,
            "human_approval_complete": False,
            "production_publication_requires_owner_approval": True,
            "production_publishable": False,
            "owner_authorized_private_generation": True,
            "senior_devotional_review_complete": False,
        }
    )
    # Prefer the clearer owner-approval key; keep legacy key if present for readers.
    review["production_publication_requires_owner_staging_approval"] = True
    data["review"] = review
    publication = dict(data.get("publication") or {})
    publication.update(
        {
            "status": "privately_shared",
            "visibility": "private_staging_only",
            "public_ceiling": 25,
            "catalog_exposure": "private",
            "production_publishable": False,
        }
    )
    data["publication"] = publication
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def main() -> int:
    for pkg in package_dirs():
        names = {p.name for p in pkg.iterdir() if p.is_file()}
        if names != EXACT_EIGHT:
            raise SystemExit(f"{pkg.name} not exact-eight: {sorted(names)}")
        story_path = pkg / "story.md"
        original = story_path.read_text(encoding="utf-8")
        updated = rewrite_parent_note(original)
        if updated != original:
            story_path.write_text(updated, encoding="utf-8")
            print(f"updated story.md: {pkg.name}")
        else:
            print(f"story.md already current: {pkg.name}")
        data = update_manifest(pkg)
        print(
            f"manifest {data['chapter_no']}: publishable={data['publishable']} "
            f"private_staging_eligible={data['private_staging_eligible']} "
            f"poster={data['file_sha256']['story_poster.png'][:12]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
