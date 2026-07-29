"""Publish gates for public catalog inclusion."""
from __future__ import annotations

from .filesystem import REQUIRED_PACKAGE_FILES, Package


def is_publicly_publishable(package: Package) -> bool:
    """Return True only for complete, release-gated story packages."""
    if not REQUIRED_PACKAGE_FILES.issubset(package.files):
        return False
    manifest = package.manifest
    if not manifest.get("slug") or not manifest.get("title"):
        return False
    chapter = str(manifest.get("chapter_no", "") or "").strip()
    digits = "".join(ch for ch in chapter if ch.isdigit())
    if not digits or digits.zfill(3) == "000":
        return False
    if manifest.get("publishable") is not True:
        return False
    quality = manifest.get("quality") or {}
    if str(quality.get("status", "")).upper() != "PASS":
        return False
    audio = manifest.get("audio") or {}
    if audio.get("audio_stale") is True:
        return False
    if "generation_verified" in audio and audio.get("generation_verified") is not True:
        return False
    return True
