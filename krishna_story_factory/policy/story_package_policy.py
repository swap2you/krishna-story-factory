"""Load the authoritative story package policy (fail-closed)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

POLICY_RELATIVE = Path("config") / "story_package_policy_v1.json"


class StoryPackagePolicyError(RuntimeError):
    """Raised when the governed package policy is missing or invalid."""


@lru_cache(maxsize=1)
def load_story_package_policy(project_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
    path = root / POLICY_RELATIVE
    if not path.is_file():
        raise StoryPackagePolicyError(f"Missing authoritative policy: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StoryPackagePolicyError(f"Invalid policy JSON at {path}: {exc}") from exc
    if data.get("policy_version") != "story_package_policy_v1":
        raise StoryPackagePolicyError(
            f"Unexpected policy_version={data.get('policy_version')!r}; expected story_package_policy_v1"
        )
    if data.get("narration_equivalence_mode") != "exact":
        raise StoryPackagePolicyError("narration_equivalence_mode must be exact")
    if not data.get("sample_first_tts_required"):
        raise StoryPackagePolicyError("sample_first_tts_required must be true")
    activity = data.get("activity") or {}
    if not activity.get("prohibit_generic_role_card_fallback"):
        raise StoryPackagePolicyError("generic activity fallback must remain prohibited")
    if int(activity.get("sequence_beats_required") or 0) != 6:
        raise StoryPackagePolicyError("sequence_beats_required must be 6")
    publication = data.get("publication") or {}
    if not publication.get("private_by_default"):
        raise StoryPackagePolicyError("packages must remain private by default")
    return data


def require_sample_first(policy: dict[str, Any] | None = None) -> bool:
    data = policy or load_story_package_policy()
    return bool(data.get("sample_first_tts_required"))


def bedtime_wpm_bounds(policy: dict[str, Any] | None = None) -> tuple[float, float, float]:
    data = policy or load_story_package_policy()
    band = data.get("bedtime_wpm") or {}
    try:
        return (
            float(band["minimum_hard"]),
            float(band["minimum_accept"]),
            float(band["maximum_accept"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise StoryPackagePolicyError(f"Invalid bedtime_wpm bounds in policy: {exc}") from exc


__all__ = [
    "POLICY_RELATIVE",
    "StoryPackagePolicyError",
    "bedtime_wpm_bounds",
    "load_story_package_policy",
    "require_sample_first",
]
