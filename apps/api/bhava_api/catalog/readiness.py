"""Public catalog readiness checks without exposing host paths."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import Story
from .filesystem import discover_packages
from .publish_gates import is_publicly_publishable


class CatalogReadinessError(RuntimeError):
    """Raised when a public catalog scan is incomplete or unsafe to apply."""


@dataclass(frozen=True)
class CatalogSnapshot:
    discovered_package_count: int
    publishable_package_count: int
    indexed_story_count: int
    first_story: str | None
    last_story: str | None


def count_publishable_packages(output_root=None) -> tuple[int, int]:
    """Return (discovered_complete_packages, publishable_packages)."""
    packages = discover_packages(output_root)
    publishable = sum(1 for package in packages if is_publicly_publishable(package))
    return len(packages), publishable


def catalog_snapshot(session: Session, settings: Settings) -> CatalogSnapshot:
    discovered, publishable = count_publishable_packages(settings.output_root)
    indexed = int(session.scalar(select(func.count()).select_from(Story)) or 0)
    first = session.scalar(select(Story.story_no).order_by(Story.story_no))
    last = session.scalar(select(Story.story_no).order_by(Story.story_no.desc()))
    return CatalogSnapshot(
        discovered_package_count=discovered,
        publishable_package_count=publishable,
        indexed_story_count=indexed,
        first_story=first,
        last_story=last,
    )


def assert_public_scan_complete(publishable_count: int, settings: Settings) -> None:
    """Block destructive refresh when the filesystem scan is incomplete."""
    if not settings.public_site:
        return
    expected = settings.public_story_max
    if publishable_count != expected:
        raise CatalogReadinessError(
            "Incomplete public catalog scan: "
            f"publishable={publishable_count} expected={expected}"
        )


def public_catalog_ready(session: Session, settings: Settings) -> CatalogSnapshot:
    """Validate output, web assets presence, and catalog row counts for public mode."""
    if not settings.output_root.exists() or not settings.output_root.is_dir():
        raise CatalogReadinessError("Public output root is missing")
    if not settings.web_assets_root.exists() or not settings.web_assets_root.is_dir():
        raise CatalogReadinessError("Public web-assets root is missing")

    snap = catalog_snapshot(session, settings)
    expected = settings.public_story_max
    expected_first = "001"
    expected_last = f"{expected:03d}"

    if snap.publishable_package_count != expected:
        raise CatalogReadinessError(
            "Public package count mismatch: "
            f"publishable={snap.publishable_package_count} expected={expected}"
        )
    if snap.indexed_story_count != expected:
        raise CatalogReadinessError(
            "Public catalog count mismatch: "
            f"indexed={snap.indexed_story_count} expected={expected}"
        )
    if snap.first_story != expected_first or snap.last_story != expected_last:
        raise CatalogReadinessError(
            "Public catalog story range mismatch: "
            f"first={snap.first_story} last={snap.last_story} "
            f"expected={expected_first}-{expected_last}"
        )
    return snap
