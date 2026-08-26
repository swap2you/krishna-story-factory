"""Build deployable Stage-1 Vāṇī bundle (originals + manifests; excludes inflated restored/)."""
from __future__ import annotations

import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "content-local" / "vani" / "krishna-book-dictations" / "v1"
OUT_DIR = ARCHIVE / "bundles"
TAG = "bhava-vani-krishna-book-dictations-complete-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = OUT_DIR / f"{TAG}.tar.gz"
    include = ["inventory", "original", "waveforms", "qa", "manifests"]
    # Keep full restored locally for comparison; Stage 1 serves originals (restoration_bypassed).
    with tarfile.open(bundle, "w:gz") as tar:
        for name in include:
            path = ARCHIVE / name
            if path.exists():
                tar.add(path, arcname=f"{TAG}/{name}")
    digest = sha256_file(bundle)
    (OUT_DIR / f"{TAG}.tar.gz.sha256").write_text(f"{digest}  {bundle.name}\n", encoding="utf-8")
    pin = {
        "tag": TAG,
        "bundle": f"{TAG}.tar.gz",
        "sha256": digest,
        "bytes": bundle.stat().st_size,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "includes": include,
        "note": "Stage-1 serve bundle uses original Dictaphone-source MP3s; 128k restored derivatives retained locally for comparison only.",
    }
    (OUT_DIR / "BUNDLE_MANIFEST.json").write_text(json.dumps(pin, indent=2) + "\n", encoding="utf-8")
    (ROOT / "deploy" / "content" / "RELEASE_VANI_CONTENT.json").write_text(
        json.dumps(
            {
                "tag": TAG,
                "bundle": f"{TAG}.tar.gz",
                "sha256": digest,
                "public_stream_allowed": False,
                "note": "Private/authenticated Stage 1 Vāṇī dictation archive. Public redistribution unresolved.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(pin, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
