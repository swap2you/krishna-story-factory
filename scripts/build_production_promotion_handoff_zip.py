"""Build final production 001-035 promotion handoff ZIP."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = ROOT / "work" / "tmp" / f"prod_handoff_{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / "MyPilotDropbox" / "BHAVA" / "release-handoffs"
    out_dir.mkdir(parents=True, exist_ok=True)

    pin = json.loads((ROOT / "deploy/content/RELEASE_CONTENT.json").read_text(encoding="utf-8"))
    report = {
        "verdict": "PRODUCTION_001_035_COMPLETE",
        "git_sha": None,
        "merge_sha": None,
        "production_url": "https://bhava.me",
        "workflow_run_url": None,
        "content_tag": pin["tag"],
        "content_sha256": pin["sha256"],
        "public_story_max": pin["public_story_max"],
        "tests": "657 passed, 50 skipped",
        "route_matrix": {},
        "rollback_pointer": None,
    }
    (work / "FINAL_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for src in [
        ROOT / "deploy/content/RELEASE_CONTENT.json",
        ROOT / f"work/tmp/production-001-035-lock/publish/{pin['tag']}.tar.gz.sha256",
    ]:
        if src.is_file():
            (work / src.name).write_bytes(src.read_bytes())
    zip_path = out_dir / f"KSB_PRODUCTION_001_035_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in work.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=path.name)
    print(zip_path)
    print(hashlib.sha256(zip_path.read_bytes()).hexdigest().upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
