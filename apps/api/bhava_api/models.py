"""Derived catalog tables. Package manifests remain authoritative."""
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    stories: Mapped[list["Story"]] = relationship(back_populates="collection")


class Story(Base):
    __tablename__ = "stories"
    __table_args__ = (UniqueConstraint("story_no", name="uq_story_story_no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    story_no: Mapped[str] = mapped_column(String(3), index=True)
    slug: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(255))
    source_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scripture_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quality_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    package_path: Mapped[str] = mapped_column(String(1024))
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"))
    collection: Mapped[Collection] = relationship(back_populates="stories")
    assets: Mapped[list["Asset"]] = relationship(
        back_populates="story", cascade="all, delete-orphan"
    )


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("story_id", "filename", name="uq_asset_filename"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(100))
    relative_path: Mapped[str] = mapped_column(String(1024))
    story: Mapped[Story] = relationship(back_populates="assets")
