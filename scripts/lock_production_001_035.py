"""Metadata-only production lock: Stories 026-035 from verified staging content."""
from __future__ import annotations

import os
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING_TAG = "bhava-content-001-035-staging-v1"
STAGING_SHA = "e073df81d85ba9e873c7debb9ebbad449858ed6db65482905faf3bb9f7781e8e"
PROD_TAG = "bhava-content-001-035-v1"
PROD_MAX = 35
WORK = ROOT / "work" / "tmp" / "production-001-035-lock"
EXACT_EIGHT = {
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
}
STAGING_NOTE = "Private staging review. Production publication requires owner approval."


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def story_no_from_dirname(name: str) -> int:
    prefix = name.split("_", 1)[0]
    return int(prefix) if prefix.isdigit() else 0


def download_staging() -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    tar_path = WORK / f"{STAGING_TAG}.tar.gz"
    sha_path = WORK / f"{STAGING_TAG}.tar.gz.sha256"
    if not tar_path.is_file() or sha256_file(tar_path).lower() != STAGING_SHA.lower():
        subprocess.check_call(
            [
                "gh",
                "release",
                "download",
                STAGING_TAG,
                "--repo",
                subprocess.check_output(
                    ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                    text=True,
                ).strip(),
                "--pattern",
                f"{STAGING_TAG}.tar.gz",
                "--pattern",
                f"{STAGING_TAG}.tar.gz.sha256",
                "--dir",
                str(WORK),
            ]
        )
    actual = sha256_file(tar_path).lower()
    if actual != STAGING_SHA.lower():
        raise SystemExit(f"Staging bundle SHA mismatch: {actual} != {STAGING_SHA}")
    expected_line = sha_path.read_text(encoding="utf-8").strip().split()[0].lower()
    if expected_line != STAGING_SHA.lower():
        raise SystemExit(f"Sidecar SHA mismatch: {expected_line}")
    return tar_path


def extract_staging(tar_path: Path) -> Path:
    extract_root = WORK / "staging-extract"
    if extract_root.is_dir():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True)
    with tarfile.open(tar_path, "r:gz") as archive:
        archive.extractall(extract_root)
    # Bundle root is either ./output or ./bhava-public-content/output
    for candidate in (extract_root / "output", extract_root / "bhava-public-content" / "output"):
        if candidate.is_dir():
            return candidate
    raise SystemExit(f"No output/ in extracted staging bundle under {extract_root}")


def remove_staging_note(text: str) -> str:
    cleaned = text.replace(f" {STAGING_NOTE}", "")
    cleaned = cleaned.replace(STAGING_NOTE, "")
    cleaned = re.sub(r"  +", " ", cleaned)
    return cleaned


def production_manifest(data: dict, *, story_no: str) -> dict:
    data = dict(data)
    hashes = {}
    # Hashes filled after story.md write
    review = dict(data.get("review") or {})
    review.update(
        {
            "public_ceiling": PROD_MAX,
            "private_staging_allowed": True,
            "human_approval_complete": True,
            "owner_production_approval": True,
            "production_publication_requires_owner_approval": False,
            "production_publishable": True,
            "production_publication_requires_owner_staging_approval": False,
            "owner_authorized_private_generation": True,
        }
    )
    if story_no == "030":
        review["senior_devotional_review_complete"] = False
        review["owner_publication_approval_overrides_pending_senior_review"] = True
    else:
        review["senior_devotional_review_complete"] = review.get(
            "senior_devotional_review_complete", False
        )
    data["review"] = review
    publication = dict(data.get("publication") or {})
    publication.update(
        {
            "status": "published",
            "visibility": "public",
            "public_ceiling": PROD_MAX,
            "catalog_exposure": "public",
            "production_publishable": True,
        }
    )
    data["publication"] = publication
    data["publishable"] = True
    data["private_staging_eligible"] = True
    data["file_sha256"] = hashes
    return data


def apply_production_lock(staging_pkg: Path, local_pkg: Path) -> None:
    story_no = f"{story_no_from_dirname(staging_pkg.name):03d}"
    media_files = EXACT_EIGHT - {"story.md", "manifest.json"}
    for name in sorted(media_files):
        src = staging_pkg / name
        dst = local_pkg / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and sha256_file(dst) == sha256_file(src):
            continue
        if dst.exists() and sha256_file(dst) != sha256_file(src):
            raise SystemExit(f"{story_no}/{name}: local media differs from verified staging bytes")
        shutil.copy2(src, dst)

    story_src = staging_pkg / "story.md"
    story_text = story_src.read_text(encoding="utf-8")
    story_out = remove_staging_note(story_text)
    if STAGING_NOTE in story_out:
        raise SystemExit(f"{story_no}: staging note still present in story.md")
    (local_pkg / "story.md").write_text(story_out, encoding="utf-8")

    manifest = production_manifest(
        json.loads((staging_pkg / "manifest.json").read_text(encoding="utf-8")),
        story_no=story_no,
    )
    hashes = {}
    for name in sorted(EXACT_EIGHT - {"manifest.json"}):
        hashes[name] = sha256_file(local_pkg / name)
    manifest["file_sha256"] = hashes
    (local_pkg / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def verify_001_025_unchanged(staging_output: Path) -> None:
    drifts = []
    for n in range(1, 26):
        sn = f"{n:03d}"
        staging_matches = sorted(staging_output.glob(f"{sn}_*"))
        local_matches = sorted((ROOT / "output").glob(f"{sn}_*"))
        if len(staging_matches) != 1 or len(local_matches) != 1:
            raise SystemExit(f"Expected one package for {sn}")
        for name in EXACT_EIGHT:
            s = staging_matches[0] / name
            l = local_matches[0] / name
            if sha256_file(s) != sha256_file(l):
                drifts.append(f"{sn}/{name}")
    if drifts:
        raise SystemExit("001-025 byte drift vs staging extract:\n" + "\n".join(drifts))


def rebuild_web_assets_026_035() -> None:
    for n in range(26, 36):
        sn = f"{n:03d}"
        subprocess.check_call(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_bhava_web_assets.py"),
                "--story-no",
                sn,
            ],
            env={**os.environ, "PYTHONPATH": str(ROOT / "apps" / "api")},
        )


def build_production_bundle() -> tuple[Path, str]:
    out_dir = WORK / "publish"
    out_dir.mkdir(parents=True, exist_ok=True)
    tar_path = out_dir / f"{PROD_TAG}.tar.gz"
    manifest_path = out_dir / f"{PROD_TAG}.manifest.json"
    subprocess.check_call(
        [
            sys.executable,
            str(ROOT / "scripts" / "deployment" / "build_public_content_bundle.py"),
            "--repository-root",
            str(ROOT),
            "--output",
            str(tar_path),
            "--manifest-output",
            str(manifest_path),
            "--max-story",
            str(PROD_MAX),
        ]
    )
    digest = sha256_file(tar_path).lower()
    (out_dir / f"{PROD_TAG}.tar.gz.sha256").write_text(
        f"{digest}  {PROD_TAG}.tar.gz\n", encoding="utf-8"
    )
    return tar_path, digest


def update_release_pin(digest: str) -> None:
    pin = {
        "tag": PROD_TAG,
        "bundle": f"{PROD_TAG}.tar.gz",
        "sha256": digest,
        "public_story_max": PROD_MAX,
        "note": (
            "Immutable public Stories 001-035 production v1. Stories 026-035 promoted "
            "with metadata-only lock from verified bhava-content-001-035-staging-v1; "
            "all media bytes preserved. Story 036+ remains excluded."
        ),
        "base_content": STAGING_TAG,
        "staging_content_sha256": STAGING_SHA,
    }
    (ROOT / "deploy" / "content" / "RELEASE_CONTENT.json").write_text(
        json.dumps(pin, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    tar_path = download_staging()
    staging_output = extract_staging(tar_path)
    verify_001_025_unchanged(staging_output)

    for n in range(26, 36):
        sn = f"{n:03d}"
        staging_pkg = next(staging_output.glob(f"{sn}_*"))
        local_pkg = next((ROOT / "output").glob(f"{sn}_*"))
        apply_production_lock(staging_pkg, local_pkg)
        print(f"locked {local_pkg.name} publishable=true")

    rebuild_web_assets_026_035()
    prod_tar, digest = build_production_bundle()
    update_release_pin(digest)
    print(json.dumps({"prod_tar": str(prod_tar), "sha256": digest, "max": PROD_MAX}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
