"""Rewrite public Next Story Preview from the series plan (never mutate packages)."""
from __future__ import annotations

import csv
import re
from functools import lru_cache

from ..config import get_settings

_NEXT_PREVIEW_RE = re.compile(
    r"(^|\n)##\s+Next Story Preview\s*\n.*?(?=\n##\s|\Z)",
    re.IGNORECASE | re.DOTALL,
)


@lru_cache(maxsize=1)
def _series_plan_rows() -> dict[str, dict[str, str]]:
    path = get_settings().repository_root / "input" / "series_plan.csv"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        raw = str(row.get("chapter_no") or "").strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            continue
        chapter = digits.zfill(3)
        out[chapter] = {
            "chapter_no": chapter,
            "title": str(row.get("title") or "").strip(),
            "slug": str(row.get("slug") or "").strip(),
        }
    return out


def next_plan_story(story_no: str) -> dict[str, str] | None:
    """Return the next row in series_plan.csv, without applying the public ceiling."""
    padded = "".join(ch for ch in str(story_no) if ch.isdigit()).zfill(3)
    try:
        nxt = f"{int(padded) + 1:03d}"
    except ValueError:
        return None
    return _series_plan_rows().get(nxt)


def _public_next_allowed(chapter_no: str) -> bool:
    """On the public site, never advertise a story past the governed ceiling."""
    settings = get_settings()
    if not settings.public_site:
        return True
    try:
        return int(chapter_no) <= int(settings.public_story_max)
    except ValueError:
        return False


def next_story_preview_markdown(story_no: str) -> str:
    nxt = next_plan_story(story_no)
    if nxt is None or not nxt.get("title") or not _public_next_allowed(nxt["chapter_no"]):
        return (
            "## Next Story Preview\n\n"
            "You have reached a beautiful milestone in Krishna Book Bedtime. "
            "Celebrate with gratitude and remember the Lord together.\n"
        )
    return (
        f"## Next Story Preview\n\n"
        f"Next time: Story {nxt['chapter_no']} — {nxt['title']}. "
        "A new scene of the Krishna Book awaits, filled with devotion and gentle surprise.\n"
    )


def apply_dynamic_next_preview(reader_md: str, story_no: str) -> str:
    """Replace or append the Next Story Preview section from series_plan.csv."""
    replacement = next_story_preview_markdown(story_no).rstrip() + "\n"
    if _NEXT_PREVIEW_RE.search(reader_md):
        return _NEXT_PREVIEW_RE.sub(lambda m: f"{m.group(1)}{replacement.rstrip()}", reader_md, count=1)
    return reader_md.rstrip() + "\n\n" + replacement


def clear_next_preview_caches() -> None:
    _series_plan_rows.cache_clear()
