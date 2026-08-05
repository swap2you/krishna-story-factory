"""Index manifest facts into SQLite without mutating story packages."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..models import Asset, Collection, Story
from .filesystem import asset_media_type, discover_packages
from .publish_gates import is_publicly_publishable
from .readiness import CatalogReadinessError, assert_public_scan_complete

logger = logging.getLogger(__name__)

COLLECTION_SLUG = "krishna-book-bedtime"
COLLECTION_TITLE = "Krishna Book Bedtime Stories"
PUBLIC_ASSET_FILES = frozenset(
    {
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
    }
)


@dataclass
class IndexResult:
    indexed: int = 0
    newly_indexed: list[str] = field(default_factory=list)

    def __int__(self) -> int:
        return self.indexed


def _normalize_story_no(chapter_no: object) -> str | None:
    """Return a 3-digit story number, or None when chapter_no is missing/invalid."""
    digits = "".join(ch for ch in str(chapter_no or "").strip() if ch.isdigit())
    if not digits:
        return None
    story_no = digits.zfill(3)
    if story_no == "000":
        return None
    return story_no


def _package_story_number(package) -> int:
    story_no = _normalize_story_no(package.manifest.get("chapter_no"))
    return int(story_no) if story_no else 0


def index_packages(session: Session) -> IndexResult:
    collection = session.scalar(select(Collection).where(Collection.slug == COLLECTION_SLUG))
    if collection is None:
        collection = Collection(
            slug=COLLECTION_SLUG,
            title=COLLECTION_TITLE,
            description="A read-only catalog of the Krishna Story Factory packages.",
        )
        session.add(collection)
        session.flush()

    settings = get_settings()
    packages = discover_packages(settings.output_root)
    # Public sites may share a content mount with private packages above max.
    # Index only stories within public_story_max so readiness stays hermetic.
    publishable_packages = [
        package
        for package in packages
        if is_publicly_publishable(package)
        and (
            not settings.public_site
            or _package_story_number(package) <= settings.public_story_max
        )
    ]
    try:
        assert_public_scan_complete(len(publishable_packages), settings)
    except CatalogReadinessError:
        # Preserve last-known-good SQLite rows; never commit a destructive empty refresh.
        session.rollback()
        logger.error(
            "catalog_incomplete_scan preserved_existing_catalog publishable=%s expected=%s",
            len(publishable_packages),
            settings.public_story_max,
        )
        raise

    seen: set[str] = set()
    result = IndexResult()
    for package in publishable_packages:
        manifest = package.manifest
        story_no = _normalize_story_no(manifest.get("chapter_no"))
        if not story_no or not manifest.get("slug") or not manifest.get("title"):
            continue
        seen.add(story_no)
        story = session.scalar(
            select(Story)
            .options(selectinload(Story.assets))
            .where(Story.story_no == story_no)
        )
        values = {
            "slug": str(manifest["slug"]),
            "title": str(manifest["title"]),
            "source_reference": manifest.get("source_reference"),
            "scripture_reference": manifest.get("scripture_reference"),
            "age_range": manifest.get("age_range"),
            "quality_status": (manifest.get("quality") or {}).get("status"),
            "package_path": str(package.path),
            "collection_id": collection.id,
        }
        if story is None:
            story = Story(story_no=story_no, **values)
            session.add(story)
            session.flush()
            result.newly_indexed.append(story_no)
        else:
            for key, value in values.items():
                setattr(story, key, value)
        existing = {asset.filename: asset for asset in story.assets}
        for filename in package.files & PUBLIC_ASSET_FILES:
            relative_path = f"{story_no}/{filename}"
            if filename not in existing:
                session.add(
                    Asset(
                        story_id=story.id,
                        filename=filename,
                        media_type=asset_media_type(filename),
                        relative_path=relative_path,
                    )
                )
        result.indexed += 1

    # Stale deletion is allowed only after a complete validated public scan (or non-public mode).
    stale = session.scalars(select(Story).where(Story.collection_id == collection.id)).all()
    for story in stale:
        if story.story_no not in seen:
            session.delete(story)

    session.commit()
    return result
