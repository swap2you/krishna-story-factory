#!/usr/bin/env python3
"""Compose staging + production content 001-025 from local packages/web-assets."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "work" / "tmp" / "content-001-025-compose" / "publish"
STAGING_TAG = "bhava-content-001-025-staging-v1"
PROD_TAG = "bhava-content-001-025-v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(tag: str, max_story: int = 25) -> tuple[Path, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tar_path = OUT_DIR / f"{tag}.tar.gz"
    manifest_path = OUT_DIR / f"{tag}.manifest.json"
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
        str(max_story),
    ]
    subprocess.check_call(cmd)
    digest = sha256(tar_path)
    (OUT_DIR / f"{tag}.tar.gz.sha256").write_text(f"{digest}  {tag}.tar.gz\n", encoding="utf-8")
    return tar_path, digest


def main() -> int:
    for story_no in ("023", "024", "025"):
        if not (ROOT / "data" / "web-assets" / story_no).is_dir():
            raise SystemExit(f"Missing data/web-assets/{story_no}")

    # Build once; staging and production tags share identical bytes for this closure.
    staging_tar, digest = build(STAGING_TAG)
    prod_tar = OUT_DIR / f"{PROD_TAG}.tar.gz"
    prod_tar.write_bytes(staging_tar.read_bytes())
    (OUT_DIR / f"{PROD_TAG}.tar.gz.sha256").write_text(f"{digest}  {PROD_TAG}.tar.gz\n", encoding="utf-8")
    # Manifest for prod tag: reuse staging build output under the prod name.
    staging_manifest = OUT_DIR / f"{STAGING_TAG}.manifest.json"
    prod_manifest = OUT_DIR / f"{PROD_TAG}.manifest.json"
    manifest = json.loads(staging_manifest.read_text(encoding="utf-8"))
    manifest["tag"] = PROD_TAG
    prod_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    staging_pin = {
        "tag": STAGING_TAG,
        "bundle": f"{STAGING_TAG}.tar.gz",
        "sha256": digest,
        "public_story_max": 25,
        "note": (
            "Staging Stories 001-025 content. Production RELEASE_CONTENT.json pins "
            "bhava-content-001-025-v1 / public_story_max=25; Story 026+ remains private."
        ),
        "base_content": "bhava-content-001-022-v1",
    }
    prod_pin = {
        "tag": PROD_TAG,
        "bundle": f"{PROD_TAG}.tar.gz",
        "sha256": digest,
        "public_story_max": 25,
        "note": (
            "Immutable public Stories 001-025 content v1: accepted packages for 023-025 "
            "promoted without regeneration; Stories 001-022 preserved from prior v1 lineage. "
            "Story 026+ remains private. CI verifies a downloaded bundle against this "
            "committed digest before any test trusts its bytes."
        ),
    }
    (ROOT / "deploy" / "content" / "RELEASE_CONTENT_STAGING.json").write_text(
        json.dumps(staging_pin, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "deploy" / "content" / "RELEASE_CONTENT.json").write_text(
        json.dumps(prod_pin, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "staging_tar": str(staging_tar),
                "prod_tar": str(prod_tar),
                "sha256": digest,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
