from __future__ import annotations

import csv
import re
from pathlib import Path

REQUIRED_FIELDS = (
    "episode_no", "slug", "title", "source_book", "source_chapter",
    "source_verses_or_boundary", "original_summary_seed", "must_include", "must_avoid",
    "start_boundary", "end_boundary", "age_range", "age_sensitivity", "devotional_theme",
    "suggested_activity_category", "package_type", "enabled",
)


def load_master_plan(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Master plan is missing columns: {sorted(missing)}")
        return list(reader)


def validate_master_plan(path: Path) -> list[str]:
    rows = load_master_plan(path)
    errors: list[str] = []
    _unique(rows, "episode_no", errors)
    _unique(rows, "slug", errors)
    _unique(rows, "title", errors, casefold=True)
    chapters: set[int] = set()
    for index, row in enumerate(rows, 1):
        episode = row["episode_no"].strip() or f"row {index}"
        if not row["source_book"].strip() or not row["source_chapter"].strip() or not row["source_verses_or_boundary"].strip():
            errors.append(f"Episode {episode} has a missing source reference.")
        if not row["original_summary_seed"].strip():
            errors.append(f"Episode {episode} has an empty summary seed.")
        if not re.fullmatch(r"\d{1,2}-\d{1,2}", row["age_range"].strip()):
            errors.append(f"Episode {episode} has invalid age_range {row['age_range']!r}.")
        try:
            chapter = int(row["source_chapter"])
            if row["source_book"].strip().casefold() == "krishna book":
                chapters.add(chapter)
        except ValueError:
            errors.append(f"Episode {episode} has invalid source_chapter {row['source_chapter']!r}.")
        if index > 1:
            previous = rows[index - 2]
            if row["original_summary_seed"].strip().casefold() == previous["original_summary_seed"].strip().casefold():
                errors.append(f"Episodes {previous['episode_no']} and {episode} have identical neighboring summary seeds.")
            _check_numeric_overlap(previous, row, errors)
    missing_chapters = sorted(set(range(1, 91)) - chapters)
    if missing_chapters:
        errors.append(f"Krishna Book chapters missing from master plan: {missing_chapters}")
    return errors


def _unique(rows: list[dict[str, str]], field: str, errors: list[str], *, casefold: bool = False) -> None:
    seen: dict[str, str] = {}
    for row in rows:
        raw = row[field].strip()
        key = raw.casefold() if casefold else raw
        if not key:
            errors.append(f"Episode {row.get('episode_no', '?')} has empty {field}.")
        elif key in seen:
            errors.append(f"Duplicate {field} {raw!r} in episodes {seen[key]} and {row.get('episode_no', '?')}.")
        else:
            seen[key] = row.get("episode_no", "?")


def _check_numeric_overlap(previous: dict[str, str], current: dict[str, str], errors: list[str]) -> None:
    if previous["source_chapter"].strip() != current["source_chapter"].strip():
        return
    prev_range = _verse_range(previous["source_verses_or_boundary"])
    curr_range = _verse_range(current["source_verses_or_boundary"])
    if prev_range and curr_range and curr_range[0] <= prev_range[1]:
        errors.append(
            f"Episodes {previous['episode_no']} and {current['episode_no']} have overlapping numeric source boundaries."
        )


def _verse_range(value: str) -> tuple[int, int] | None:
    match = re.search(r"(?:\d+\.){2}(\d+)\s*[-–]\s*(\d+)", value)
    return (int(match.group(1)), int(match.group(2))) if match else None

