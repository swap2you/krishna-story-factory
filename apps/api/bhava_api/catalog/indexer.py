"""Index manifest facts into SQLite without mutating story packages."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Asset, Collection, Story
from .filesystem import asset_media_type, discover_packages

COLLECTION_SLUG = "krishna-book-bedtime"
COLLECTION_TITLE = "Krishna Book Bedtime Stories"


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

    indexed = 0
    for package in discover_packages():
        manifest = package.manifest
        story_no = str(manifest.get("chapter_no", "")).zfill(3)
        if not story_no or not manifest.get("slug") or not manifest.get("title"):
            continue
        story = session.scalar(select(Story).where(Story.story_no == story_no))
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
        for filename in package.files & {
            "story.md", "narration.mp3", "story_poster.png", "coloring_page.png",
            "simple_coloring_page.png", "activity_sheet.pdf", "whatsapp_caption.txt",
        }:
            relative_path = f"{story_no}/{filename}"
            if filename not in existing:
                session.add(Asset(
                    story_id=story.id, filename=filename,
                    media_type=asset_media_type(filename), relative_path=relative_path,
                ))
        indexed += 1
    session.commit()
    return indexed
