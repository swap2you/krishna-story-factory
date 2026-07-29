"""One-shot safety baseline for Bhāva Stories Production Launch."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "story.md",
    "narration.mp3",
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "activity_sheet.pdf",
    "whatsapp_caption.txt",
    "manifest.json",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cmd(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, cwd=ROOT).strip()
    except Exception:
        return ""


def main() -> None:
    stories: dict = {}
    for n in range(1, 10):
        chapter = f"{n:03d}"
        pkgs = [p for p in sorted((ROOT / "output").glob(f"{chapter}_*")) if p.is_dir()]
        if not pkgs:
            raise SystemExit(f"missing package for {chapter}")
        pkg = pkgs[0]
        for cand in pkgs:
            man_path = cand / "manifest.json"
            if not man_path.is_file():
                continue
            try:
                m = json.loads(man_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if m.get("publishable") is True:
                pkg = cand
                break
        files = {}
        for name in REQUIRED:
            path = pkg / name
            if not path.is_file():
                raise SystemExit(f"missing {chapter}/{name} in {pkg}")
            files[name] = _sha(path)
        man = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
        stories[chapter] = {
            "folder": pkg.name,
            "title": man.get("title"),
            "source_reference": man.get("source_reference"),
            "publishable": man.get("publishable"),
            "quality": (man.get("quality") or {}).get("status"),
            "file_sha256": files,
        }
        print(chapter, pkg.name, len(files))

    queue = ROOT / "tracking" / "queue_state.csv"
    qhash = _sha(queue) if queue.is_file() else None
    out010 = list((ROOT / "output").glob("010_*"))
    tags = _cmd(["git", "tag", "--list"]).splitlines()
    main_sha = _cmd(["git", "rev-parse", "origin/main"]) or _cmd(["git", "rev-parse", "main"])
    baseline = {
        "release": "BHAVA_STORIES_PRODUCTION_LAUNCH",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "starting_head_sha": "87930f87b34deb9887afc994458f6981e0effd4e",
        "origin_sha": _cmd(["git", "rev-parse", "origin/feature/bhava-portal-v1"]),
        "main_sha": main_sha,
        "tags": tags,
        "queue_state_sha256": qhash,
        "queue_009": "done",
        "queue_010": {"slug": "baby-krishna-breaks-the-cart", "status": "pending"},
        "queue_011": {"slug": "the-salvation-of-trinavarta", "status": "pending"},
        "story_010_present": bool(out010),
        "node": _cmd(["node", "--version"]),
        "npm": _cmd(["npm", "--version"]),
        "installed_web_deps_note": "Recorded from apps/web package.json before controlled upgrade",
        "stories": stories,
    }
    out = ROOT / "docs" / "releases" / "BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print("wrote", out, "stories", len(stories), "file_hashes", sum(len(s["file_sha256"]) for s in stories.values()))


if __name__ == "__main__":
    main()
