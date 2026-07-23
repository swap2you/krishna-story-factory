"""Safe catalog freshness: re-index packages without mutating story files."""
from __future__ import annotations

import threading
import time
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import SessionLocal
from .indexer import index_packages

DEFAULT_MIN_INTERVAL_SEC = 20.0


class CatalogFreshness:
    """Throttle filesystem re-indexing while the API stays up."""

    def __init__(self, min_interval_sec: float = DEFAULT_MIN_INTERVAL_SEC) -> None:
        self.min_interval_sec = min_interval_sec
        self._lock = threading.Lock()
        self._last_refresh = 0.0
        self._fingerprint = ""
        self._indexed = 0

    def fingerprint(self, output_root: Path | None = None) -> str:
        root = (output_root or get_settings().output_root).resolve()
        if not root.exists():
            return "missing"
        parts: list[str] = []
        for manifest in sorted(root.glob("*/manifest.json")):
            try:
                stat = manifest.stat()
                parts.append(f"{manifest.parent.name}:{stat.st_mtime_ns}:{stat.st_size}")
            except OSError:
                continue
        return "|".join(parts)

    def refresh_if_stale(self, session: Session | None = None, force: bool = False) -> int:
        now = time.monotonic()
        with self._lock:
            if not force and (now - self._last_refresh) < self.min_interval_sec:
                return self._indexed
            current = self.fingerprint()
            if not force and current == self._fingerprint and self._last_refresh > 0:
                self._last_refresh = now
                return self._indexed
            with SessionLocal() as local:
                self._indexed = index_packages(local)
            self._fingerprint = current
            self._last_refresh = now
            if session is not None:
                session.expire_all()
            return self._indexed


catalog_freshness = CatalogFreshness()


def refresh_if_stale(session: Session | None = None, force: bool = False) -> int:
    return catalog_freshness.refresh_if_stale(session=session, force=force)
