"""Publish gates for public catalog inclusion and private staging."""
from __future__ import annotations

from .filesystem import REQUIRED_PACKAGE_FILES, Package


def _base_package_complete(package: Package) -> bool:
    if not REQUIRED_PACKAGE_FILES.issubset(package.files):
        return False
    manifest = package.manifest
    if not manifest.get("slug") or not manifest.get("title"):
        return False
    chapter = str(manifest.get("chapter_no", "") or "").strip()
    digits = "".join(ch for ch in chapter if ch.isdigit())
    if not digits or digits.zfill(3) == "000":
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


def is_publicly_publishable(package: Package) -> bool:
    """Return True only for complete, production-gated story packages."""
    if not _base_package_complete(package):
        return False
    return package.manifest.get("publishable") is True


def is_private_staging_eligible(package: Package) -> bool:
    """Return True for complete packages allowed on private/staging catalogs only."""
    if not _base_package_complete(package):
        return False
    return package.manifest.get("private_staging_eligible") is True


def is_catalog_indexable(package: Package, *, environment: str, public_site: bool) -> bool:
    """Choose catalog eligibility by environment.

    - production (public site): production publishable only
    - staging / non-production public site: publishable OR private_staging_eligible
    - local / non-public: publishable OR private_staging_eligible
    """
    env = (environment or "").strip().lower()
    if public_site and env == "production":
        return is_publicly_publishable(package)
    return is_publicly_publishable(package) or is_private_staging_eligible(package)
