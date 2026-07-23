"""Read-only public catalog endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..catalog.freshness import refresh_if_stale
from ..db import get_session
from ..models import Collection, Story
from ..schemas import CollectionResponse, ShlokaResponse, SourceResponse, StoryResponse, StorySummary

router = APIRouter(prefix="/api/v1", tags=["public"])


def _asset_url(story_no: str, filename: str) -> str:
    return f"/api/v1/stories/{story_no}/assets/{filename}"


def _asset_map(story: Story) -> dict[str, str]:
    return {
        asset.filename: _asset_url(story.story_no, asset.filename)
        for asset in story.assets
    }


def _story_summary(story: Story) -> StorySummary:
    assets = _asset_map(story)
    return StorySummary(
        story_no=story.story_no,
        slug=story.slug,
        title=story.title,
        source_reference=story.source_reference,
        scripture_reference=story.scripture_reference,
        age_range=story.age_range,
        quality_status=story.quality_status,
        poster_url=assets.get("story_poster.png"),
        narration_url=assets.get("narration.mp3"),
        story_md_url=assets.get("story.md"),
    )


def _story_response(story: Story) -> StoryResponse:
    assets = _asset_map(story)
    return StoryResponse(
        story_no=story.story_no,
        slug=story.slug,
        title=story.title,
        source_reference=story.source_reference,
        scripture_reference=story.scripture_reference,
        age_range=story.age_range,
        quality_status=story.quality_status,
        poster_url=assets.get("story_poster.png"),
        narration_url=assets.get("narration.mp3"),
        story_md_url=assets.get("story.md"),
        assets=[
            {
                "filename": asset.filename,
                "media_type": asset.media_type,
                "url": assets[asset.filename],
            }
            for asset in sorted(story.assets, key=lambda item: item.filename)
        ],
    )


def _get_story(session: Session, story_no: str) -> Story:
    refresh_if_stale(session=session)
    story = session.scalar(
        select(Story).options(selectinload(Story.assets)).where(Story.story_no == story_no.zfill(3))
    )
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "bhava-api"}


@router.get("/collections", response_model=list[CollectionResponse])
def collections(session: Session = Depends(get_session)) -> list[CollectionResponse]:
    refresh_if_stale(session=session)
    records = session.scalars(select(Collection).options(selectinload(Collection.stories))).all()
    return [CollectionResponse(
        slug=item.slug, title=item.title, description=item.description, story_count=len(item.stories)
    ) for item in records]


@router.get("/collections/{slug}", response_model=CollectionResponse)
def collection(slug: str, session: Session = Depends(get_session)) -> CollectionResponse:
    refresh_if_stale(session=session)
    item = session.scalar(select(Collection).options(selectinload(Collection.stories)).where(Collection.slug == slug))
    if item is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return CollectionResponse(slug=item.slug, title=item.title, description=item.description, story_count=len(item.stories))


@router.get("/stories", response_model=list[StorySummary])
def stories(session: Session = Depends(get_session)) -> list[StorySummary]:
    refresh_if_stale(session=session)
    records = session.scalars(
        select(Story).options(selectinload(Story.assets)).order_by(Story.story_no)
    ).all()
    return [_story_summary(record) for record in records]


@router.get("/stories/{story_no}", response_model=StoryResponse)
def story(story_no: str, session: Session = Depends(get_session)) -> StoryResponse:
    return _story_response(_get_story(session, story_no))


@router.get("/stories/{story_no}/assets", response_model=list[dict])
def assets(story_no: str, session: Session = Depends(get_session)) -> list[dict]:
    return _story_response(_get_story(session, story_no)).assets


@router.get("/stories/{story_no}/source", response_model=SourceResponse)
def source(story_no: str, session: Session = Depends(get_session)) -> SourceResponse:
    item = _get_story(session, story_no)
    return SourceResponse(source_reference=item.source_reference, scripture_reference=item.scripture_reference)


@router.get("/stories/{story_no}/shlokas", response_model=ShlokaResponse)
def shlokas(story_no: str, session: Session = Depends(get_session)) -> ShlokaResponse:
    _get_story(session, story_no)
    return ShlokaResponse()


@router.get("/search", response_model=list[StorySummary])
def search(q: str = Query(min_length=1), session: Session = Depends(get_session)) -> list[StorySummary]:
    refresh_if_stale(session=session)
    term = f"%{q.strip()}%"
    records = session.scalars(
        select(Story)
        .options(selectinload(Story.assets))
        .where(
            or_(
                Story.title.ilike(term),
                Story.slug.ilike(term),
                Story.story_no.ilike(term),
                Story.source_reference.ilike(term),
                Story.scripture_reference.ilike(term),
            )
        )
        .order_by(Story.story_no)
    ).all()
    return [_story_summary(record) for record in records]
