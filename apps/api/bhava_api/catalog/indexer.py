"""Index manifest facts into SQLite without mutating story packages."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Asset, Collection, Story
from .filesystem import asset_media_type, discover_packages
from .publish_gates import is_publicly_publishable

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


def _normalize_story_no(chapter_no: object) -> str | None:
    """Return a 3-digit story number, or None when chapter_no is missing/invalid."""
    digits = "".join(ch for ch in str(chapter_no or "").strip() if ch.isdigit())
    if not digits:
        return None
    story_no = digits.zfill(3)
    if story_no == "000":
        return None
    return story_no


def index_packages(session: Session) -> int:
    collection = session.scalar(select(Collection).where(Collection.slug == COLLECTION_SLUG))
    if collection is None:
        collection = Collection(
            slug=COLLECTION_SLUG,
            title=COLLECTION_TITLE,
            description="A read-only catalog of the Krishna Story Factory packages.",
        )
        session.add(collection)
        session.flush()

    seen: set[str] = set()
    indexed = 0
    for package in discover_packages():
        if not is_publicly_publishable(package):
            continue
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
        indexed += 1

    stale = session.scalars(select(Story).where(Story.collection_id == collection.id)).all()
    for story in stale:
        if story.story_no not in seen:
            session.delete(story)

    session.commit()
    return indexed
