"""Compose staging-only content 001-035; keep production pin at 001-025."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "work" / "tmp" / "content-001-035-staging" / "publish"
STAGING_TAG = "bhava-content-001-035-staging-v1"
STAGING_MAX = 35


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    for story_no in [f"{n:03d}" for n in range(1, STAGING_MAX + 1)]:
        if not (ROOT / "data" / "web-assets" / story_no).is_dir():
            raise SystemExit(f"Missing data/web-assets/{story_no}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tar_path = OUT_DIR / f"{STAGING_TAG}.tar.gz"
    manifest_path = OUT_DIR / f"{STAGING_TAG}.manifest.json"
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
        str(STAGING_MAX),
    ]
    subprocess.check_call(cmd)
    digest = sha256(tar_path)
    (OUT_DIR / f"{STAGING_TAG}.tar.gz.sha256").write_text(
        f"{digest}  {STAGING_TAG}.tar.gz\n", encoding="utf-8"
    )

    prod = json.loads((ROOT / "deploy" / "content" / "RELEASE_CONTENT.json").read_text(encoding="utf-8"))
    if int(prod["public_story_max"]) != 25:
        raise SystemExit(f"Production pin must remain 25, got {prod}")

    staging_pin = {
        "tag": STAGING_TAG,
        "bundle": f"{STAGING_TAG}.tar.gz",
        "sha256": digest,
        "public_story_max": STAGING_MAX,
        "note": (
            "Stage 1 private staging content Stories 001-035. "
            "Production RELEASE_CONTENT.json remains bhava-content-001-025-v1 / public_story_max=25. "
            "Stories 026-035 are private_staging_eligible only (publishable=false)."
        ),
        "base_content": "bhava-content-001-025-staging-v1",
    }
    (ROOT / "deploy" / "content" / "RELEASE_CONTENT_STAGING.json").write_text(
        json.dumps(staging_pin, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"staging_tar": str(tar_path), "sha256": digest, "max": STAGING_MAX}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
