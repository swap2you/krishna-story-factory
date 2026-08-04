#!/usr/bin/env python3
"""Compose staging content 001-022 from published v4 + local 021/022 packages."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = "bhava-content-001-022-staging-v1"
COMPOSE = ROOT / "work" / "tmp" / "content-staging-compose"
EXTRACT = COMPOSE / "extract"
OUT_DIR = COMPOSE / "publish"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    web_assets_src = EXTRACT / "web-assets"
    if not web_assets_src.is_dir():
        raise SystemExit(
            f"Missing extracted v4 web-assets at {web_assets_src}. "
            "Download/extract bhava-content-001-020-v4 into "
            "work/tmp/content-staging-compose/extract first."
        )
    web_dest = ROOT / "data" / "web-assets"
    web_dest.mkdir(parents=True, exist_ok=True)
    # Restore 001-020 web assets from approved v4 extract (do not overwrite 021/022).
    for story_dir in sorted(web_assets_src.iterdir()):
        if not story_dir.is_dir():
            continue
        if story_dir.name in {"021", "022"}:
            continue
        target = web_dest / story_dir.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(story_dir, target)

    # Ensure local 021/022 web assets exist.
    for story_no in ("021", "022"):
        if not (web_dest / story_no).is_dir():
            raise SystemExit(f"Missing local web-assets/{story_no}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tar_path = OUT_DIR / f"{TAG}.tar.gz"
    manifest_path = OUT_DIR / f"{TAG}.manifest.json"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "deployment" / "build_public_content_bundle.py"),
        "--repository-root",
        str(ROOT),
        "--output",
        str(tar_path),
        "--manifest-output",
        str(manifest_path),
        "--max-story",
        "22",
    ]
    subprocess.check_call(cmd)
    digest = sha256(tar_path)
    (OUT_DIR / f"{TAG}.tar.gz.sha256").write_text(f"{digest}  {TAG}.tar.gz\n", encoding="utf-8")
    pin = {
        "tag": TAG,
        "bundle": f"{TAG}.tar.gz",
        "sha256": digest,
        "public_story_max": 22,
        "note": (
            "Staging-only Stories 001-022 content. Production RELEASE_CONTENT.json "
            "remains pinned to bhava-content-001-020-v4 / public_story_max=20."
        ),
        "base_content": "bhava-content-001-020-v4",
    }
    pin_path = ROOT / "deploy" / "content" / "RELEASE_CONTENT_STAGING.json"
    pin_path.write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"tar": str(tar_path), "sha256": digest, "pin": str(pin_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
