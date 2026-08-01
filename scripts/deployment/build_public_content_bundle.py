from __future__ import annotations

import argparse
import hashlib
import json
import shutil
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def story_number(folder: Path) -> int:
    prefix = folder.name.split("_", 1)[0]
    if not prefix.isdigit():
        return 0
    return int(prefix)


def _require_web_assets(web_assets: Path, story_no: str) -> None:
    if not web_assets.is_dir():
        raise SystemExit(
            f"Required web-assets/{story_no}/ missing. "
            "Build derived web assets before packaging public content."
        )
    names = {item.name for item in web_assets.iterdir() if item.is_file()}
    missing = REQUIRED_WEB_ASSETS - names
    if missing:
        raise SystemExit(
            f"web-assets/{story_no}/ incomplete. Missing={sorted(missing)}"
        )
    manifest_path = web_assets / "web_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid web_manifest.json for {story_no}: {exc}") from exc
    for field in ("package_manifest_sha256", "story_md_sha256", "generated_at", "assets"):
        if field not in manifest:
            raise SystemExit(f"web-assets/{story_no}/web_manifest.json missing {field}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    parser.add_argument("--max-story", type=int, default=10)
    args = parser.parse_args()

    repository = args.repository_root.resolve()
    output_root = repository / "output"
    packages = [
        path for path in output_root.iterdir()
        if path.is_dir() and 1 <= story_number(path) <= args.max_story
    ]
    packages.sort(key=story_number)

    expected_numbers = list(range(1, args.max_story + 1))
    actual_numbers = [story_number(path) for path in packages]
    if actual_numbers != expected_numbers:
        raise SystemExit(
            f"Expected one package for Stories 001-{args.max_story:03d}; found {actual_numbers}"
        )

    forbidden = [
        path for path in output_root.iterdir()
        if path.is_dir() and story_number(path) > args.max_story
    ]
    # Higher-numbered local packages may exist, but they must never enter the bundle.
    forbidden_names = [path.name for path in forbidden]

    with tempfile.TemporaryDirectory(prefix="bhava-public-content-") as temp:
        staging = Path(temp)
        bundle_root = staging / "bhava-public-content"
        deployed_output = bundle_root / "output"
        deployed_web_assets = bundle_root / "web-assets"
        deployed_output.mkdir(parents=True)
        deployed_web_assets.mkdir(parents=True)

        manifest: dict = {
            "schema_version": 1,
            "public_story_min": 1,
            "public_story_max": args.max_story,
            "forbidden_local_packages_observed": forbidden_names,
            "packages": [],
            "web_assets": [],
        }

        for package in packages:
            names = {item.name for item in package.iterdir() if item.is_file()}
            if names != REQUIRED:
                missing = sorted(REQUIRED - names)
                extras = sorted(names - REQUIRED)
                raise SystemExit(
                    f"{package.name} is not exact-eight. Missing={missing}; extras={extras}"
                )

            destination = deployed_output / package.name
            destination.mkdir()
            file_rows = []
            for name in sorted(REQUIRED):
                source = package / name
                target = destination / name
                shutil.copy2(source, target)
                file_rows.append(
                    {"name": name, "sha256": sha256(target), "bytes": target.stat().st_size}
                )

            story_no = f"{story_number(package):03d}"
            manifest["packages"].append(
                {
                    "story_no": story_no,
                    "directory": package.name,
                    "files": file_rows,
                }
            )

            web_assets = repository / "data" / "web-assets" / story_no
            _require_web_assets(web_assets, story_no)
            shutil.copytree(
                web_assets,
                deployed_web_assets / story_no,
                dirs_exist_ok=True,
            )
            web_rows = []
            for name in sorted(REQUIRED_WEB_ASSETS):
                target = deployed_web_assets / story_no / name
                web_rows.append(
                    {"name": name, "sha256": sha256(target), "bytes": target.stat().st_size}
                )
            manifest["web_assets"].append({"story_no": story_no, "files": web_rows})

        manifest_path = bundle_root / "BHAVA_DEPLOYMENT_CONTENT_MANIFEST.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(args.output, "w:gz") as archive:
            archive.add(bundle_root, arcname=".")

        args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest_path, args.manifest_output)

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
