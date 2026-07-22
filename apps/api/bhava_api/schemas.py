"""Public API response contracts."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    filename: str
    media_type: str
    url: str


class StorySummary(BaseModel):
    story_no: str
    slug: str
    title: str
    source_reference: str | None = None
    scripture_reference: str | None = None
    age_range: str | None = None
    quality_status: str | None = None


class StoryResponse(StorySummary):
    assets: list[AssetResponse] = Field(default_factory=list)


class CollectionResponse(BaseModel):
    slug: str
    title: str
    description: str | None = None
    story_count: int


class SourceResponse(BaseModel):
    source_reference: str | None = None
    scripture_reference: str | None = None


class ShlokaResponse(BaseModel):
    shlokas: list[dict] = Field(default_factory=list)
    note: str = "not yet curated"
