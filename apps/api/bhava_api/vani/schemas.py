"""Manifest and response models for the Krishna Book dictation archive."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ManifestModel(BaseModel):
    """Allow additive manifest metadata while validating the serving contract."""

    model_config = ConfigDict(extra="allow")


class RightsState(str, Enum):
    PRIVATE_REVIEW_ALLOWED = "PRIVATE_REVIEW_ALLOWED"
    PUBLIC_REDISTRIBUTION_APPROVED = "PUBLIC_REDISTRIBUTION_APPROVED"
    PUBLIC_RIGHTS_UNRESOLVED = "PUBLIC_RIGHTS_UNRESOLVED"


class RightsManifest(ManifestModel):
    state: RightsState = RightsState.PUBLIC_RIGHTS_UNRESOLVED
    evidence: Any | None = None
    public_stream_allowed: bool = False
    public_download_allowed: bool = False


class SourceManifest(ManifestModel):
    source_id: str | None = None
    page_url: str | None = None
    media_url: str | None = None
    retrieved_at: str | None = None


class OriginalAudioManifest(ManifestModel):
    relative_path: str | None = None
    sha256: str | None = None
    bytes: int = 0
    codec: str | None = None
    sample_rate_hz: int = 0
    channels: int = 0
    duration_seconds: float = 0


class RestoredAudioManifest(ManifestModel):
    relative_path: str | None = None
    sha256: str | None = None
    filter_chain: Any | None = None
    restoration_bypassed: bool = False
    duration_seconds: float = 0
    integrated_lufs: float | None = None
    true_peak_dbtp: float | None = None
    qa_status: str = "pending"


class TranscriptManifest(ManifestModel):
    state: str = "external_link_only"
    url: str | None = None
    exact_quote_verified: bool = False


class TrackManifest(ManifestModel):
    schema_version: int = 1
    collection_id: str = "krishna-book-dictations"
    canonical_track_id: str
    chapter_start: int | None = None
    chapter_end: int | None = None
    canonical_title: str
    source_title: str | None = None
    availability: str = "available"
    source: SourceManifest = Field(default_factory=SourceManifest)
    rights: RightsManifest = Field(default_factory=RightsManifest)
    original: OriginalAudioManifest = Field(default_factory=OriginalAudioManifest)
    restored: RestoredAudioManifest = Field(default_factory=RestoredAudioManifest)
    transcript: TranscriptManifest = Field(default_factory=TranscriptManifest)
    related_story_ids: list[str] = Field(default_factory=list)
    waveform_relative_path: str | None = None


class CollectionManifest(ManifestModel):
    schema_version: int = 1
    collection_id: str = "krishna-book-dictations"
    title: str = "Śrīla Prabhupāda Krishna Book Dictations"
    description: str | None = None


class TrackResponse(ManifestModel):
    track_id: str
    canonical_track_id: str
    canonical_title: str
    availability: str
    stream_allowed: bool = False
    audio_url: str | None = None
    waveform_url: str | None = None
    previous_available_track_id: str | None = None
    next_available_track_id: str | None = None


class CollectionResponse(CollectionManifest):
    tracks: list[dict[str, Any]] = Field(default_factory=list)
    track_count: int = 91
    available_track_count: int = 0
