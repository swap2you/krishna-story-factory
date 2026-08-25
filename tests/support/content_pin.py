"""Read the committed production content pin (deploy/content/RELEASE_CONTENT.json)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIN_PATH = ROOT / "deploy" / "content" / "RELEASE_CONTENT.json"


@lru_cache(maxsize=1)
def production_public_story_max() -> int:
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    return int(pin["public_story_max"])
