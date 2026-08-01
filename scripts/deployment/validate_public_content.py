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

REQUIRED_WEB_ASSETS = {
    "reader.md",
    "reader.txt",
    "source_links.json",
    "reflections.json",
    "shlokas.json",
    "sync.json",
    "waveform.json",
    "web_manifest.json",
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

REQUIRED_RIGHTS_ATTR = (
    "Svarna Gauranga Das",
    "Dauji Publication",
    "Bhāva",
)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def _validate_web_assets(root: Path, max_story: int) -> None:
    web_root = root / "web-assets"
    if not web_root.is_dir():
        raise SystemExit("Missing required web-assets/ directory in content bundle.")

    for number in range(1, max_story + 1):
        story_no = f"{number:03d}"
        dest = web_root / story_no
        if not dest.is_dir():
            raise SystemExit(f"Missing web-assets/{story_no}/")
        names = {item.name for item in dest.iterdir() if item.is_file()}
        missing = REQUIRED_WEB_ASSETS - names
        if missing:
            raise SystemExit(f"web-assets/{story_no}/ missing required files: {sorted(missing)}")

        manifest_path = dest / "web_manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Invalid web_manifest.json for {story_no}: {exc}") from exc

        for field in ("package_manifest_sha256", "story_md_sha256", "generated_at", "assets"):
            if field not in manifest:
                raise SystemExit(f"web-assets/{story_no}/web_manifest.json missing {field}")

        assets = manifest.get("assets")
        if not isinstance(assets, dict):
            raise SystemExit(f"web-assets/{story_no}/web_manifest.json assets invalid")

        for name in REQUIRED_WEB_ASSETS:
            if name == "web_manifest.json":
                continue
            path = dest / name
            if path.stat().st_size < 1:
                raise SystemExit(f"web-assets/{story_no}/{name} is empty")
            meta = assets.get(name)
            if not isinstance(meta, dict):
                raise SystemExit(f"web-assets/{story_no}/web_manifest.json missing assets.{name}")
            if meta.get("sha256") != digest(path):
                raise SystemExit(f"web-assets/{story_no}/{name} hash mismatch vs web_manifest")
            if meta.get("bytes") != path.stat().st_size:
                raise SystemExit(f"web-assets/{story_no}/{name} size mismatch vs web_manifest")

        _validate_public_rights(dest, story_no, manifest)


def _validate_public_rights(dest: Path, story_no: str, manifest: dict) -> None:
    rights = manifest.get("rights")
    if not isinstance(rights, dict) or not rights:
        raise SystemExit(f"web-assets/{story_no}/web_manifest.json rights must be non-empty")
    if "contact_email" in rights:
        raise SystemExit(
            f"web-assets/{story_no}/web_manifest.json rights must omit contact_email"
        )
    rights_blob = json.dumps(rights, ensure_ascii=False)
    for token in REQUIRED_RIGHTS_ATTR:
        if token not in rights_blob:
            raise SystemExit(
                f"web-assets/{story_no}/web_manifest.json rights missing {token!r}"
            )
    if "used with permission" in rights_blob.lower():
        raise SystemExit(
            f"web-assets/{story_no}/web_manifest.json rights must not claim "
            "'used with permission'"
        )
    if "@gmail" in rights_blob.lower() or "contact_email" in rights_blob.lower():
        raise SystemExit(
            f"web-assets/{story_no}/web_manifest.json rights must not contain contact email"
        )
    if "Windows\\Fonts" in rights_blob or "artifact_notes" in rights:
        raise SystemExit(
            f"web-assets/{story_no}/web_manifest.json rights must not leak operator paths"
        )

    reader_path = dest / "reader.md"
    reader = reader_path.read_text(encoding="utf-8")
    if "## Rights and Credits" not in reader:
        raise SystemExit(f"web-assets/{story_no}/reader.md missing Rights and Credits section")
    if "contact_email" in reader.lower():
        raise SystemExit(f"web-assets/{story_no}/reader.md must not contain contact_email")
    if "@gmail" in reader.lower():
        raise SystemExit(f"web-assets/{story_no}/reader.md must not contain contact email")
    for token in REQUIRED_RIGHTS_ATTR:
        if token not in reader:
            raise SystemExit(
                f"web-assets/{story_no}/reader.md Rights section missing {token!r}"
            )


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

    _validate_web_assets(root, max_story)


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
