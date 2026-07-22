"""SQLite persistence for the derived, disposable catalog index."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def make_engine():
    settings = get_settings()
    settings.catalog_db.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{settings.catalog_db.as_posix()}", future=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
