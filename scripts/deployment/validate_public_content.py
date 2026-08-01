from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

REQUIRED = {
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
}

FORBIDDEN_PARTS = {
    ".git",
    ".env",
    "credentials",
    "MyPilotDropbox",
    "_archive",
    "work",
    "staging",
    "tracking",
    "logs",
}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def validate(root: Path, max_story: int) -> None:
    for path in root.rglob("*"):
        if any(part in FORBIDDEN_PARTS for part in path.parts):
            raise SystemExit(f"Forbidden path in content bundle: {path}")

    manifest_path = root / "BHAVA_DEPLOYMENT_CONTENT_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("Missing content manifest.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("public_story_max") != max_story:
        raise SystemExit("Manifest public_story_max mismatch.")

    packages = manifest.get("packages")
    if not isinstance(packages, list) or len(packages) != max_story:
        raise SystemExit("Invalid package count.")

    observed = []
    for package in packages:
        number = int(package["story_no"])
        if number > max_story:
            raise SystemExit("Story above public maximum.")
        observed.append(number)

        directory = root / "output" / package["directory"]
        names = {item.name for item in directory.iterdir() if item.is_file()}
        if names != REQUIRED:
            raise SystemExit(f"{directory.name} is not exact-eight.")

        expected = {row["name"]: row for row in package["files"]}
        for name in REQUIRED:
            path = directory / name
            row = expected.get(name)
            if row is None:
                raise SystemExit(f"Missing manifest hash for {path}")
            if digest(path) != row["sha256"]:
                raise SystemExit(f"Hash mismatch: {path}")
            if path.stat().st_size != row["bytes"]:
                raise SystemExit(f"Size mismatch: {path}")

    if observed != list(range(1, max_story + 1)):
        raise SystemExit(f"Unexpected story sequence: {observed}")


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bundle", type=Path)
    source.add_argument("--directory", type=Path)
    parser.add_argument("--max-story", type=int, default=10)
    args = parser.parse_args()

    if args.directory:
        validate(args.directory.resolve(), args.max_story)
        return 0

    with tempfile.TemporaryDirectory(prefix="bhava-content-validate-") as temp:
        root = Path(temp)
        with tarfile.open(args.bundle, "r:gz") as archive:
            for member in archive.getmembers():
                destination = (root / member.name).resolve()
                try:
                    destination.relative_to(root.resolve())
                except ValueError as exc:
                    raise SystemExit(f"Unsafe archive member: {member.name}") from exc
            archive.extractall(root, filter="data")
        validate(root, args.max_story)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
