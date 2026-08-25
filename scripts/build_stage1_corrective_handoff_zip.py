"""Build Stage 1 corrective handoff ZIP after smoke."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = ROOT / "work" / "tmp" / f"stage1_handoff_{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / "MyPilotDropbox" / "BHAVA" / "release-handoffs"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    providers = {}
    for n in range(26, 36):
        d = next((ROOT / "output").glob(f"{n:03d}_*"))
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        providers[f"{n:03d}"] = {
            "provider": m.get("audio_source") or (m.get("audio") or {}).get("provider"),
            "peak": (m.get("metrics") or {}).get("peak"),
            "duration_s": (m.get("metrics") or {}).get("audio_duration_seconds"),
            "publishable": m.get("publishable"),
            "private_staging_eligible": m.get("private_staging_eligible"),
            "poster_sha256": (m.get("file_sha256") or {}).get("story_poster.png"),
            "narration_sha256": (m.get("file_sha256") or {}).get("narration.mp3"),
        }
        for name in sorted(p.name for p in d.iterdir() if p.is_file()):
            data = (d / name).read_bytes()
            rows.append(
                {
                    "story": f"{n:03d}",
                    "file": name,
                    "sha256": hashlib.sha256(data).hexdigest().upper(),
                    "bytes": len(data),
                }
            )

    report = {
        "verdict": "READY_FOR_OWNER_STAGE1_REVIEW",
        "git_sha": "0b042707a40474871f51d4d5d3e4f00a39f50140",
        "stage1_url": "https://staging.bhava.me",
        "workflow_run_url": "https://github.com/swap2you/krishna-story-factory/actions/runs/32890819433",
        "content_tag": "bhava-content-001-035-staging-v1",
        "content_sha256": "e073df81d85ba9e873c7debb9ebbad449858ed6db65482905faf3bb9f7781e8e",
        "staging_public_story_max": 35,
        "production_public_story_max": 25,
        "production_version_observed": {
            "release_sha": "0ba600e309b9d3aedb533ba830a8b14db10a368f",
            "public_story_max": 25,
            "indexed_story_count": 25,
            "discovered_package_count": 35,
            "content_tag": "bhava-content-001-025-v1",
        },
        "tests": {
            "pytest": "655 passed, 50 skipped",
            "run_test_ps1": "OUT_OF_SCOPE_NEXT_036_REPETITION_GATE",
        },
        "stage1_smoke": {
            "catalog_ok": "library=200 api=200 count=35 first=001 last=035",
            "deployed_sha": "0b042707a40474871f51d4d5d3e4f00a39f50140",
            "public_max": 35,
            "story_036": "404",
            "noindex": "X-Robots-Tag noindex verified",
            "workflow_smoke": "PASS",
            "route_matrix": {
                "026": "page=200 api=200 audio=200",
                "027": "page=200 api=200 audio=200",
                "028": "page=200 api=200 audio=200",
                "029": "page=200 api=200 audio=200",
                "030": "page=200 api=200 audio=200",
                "031": "page=200 api=200 audio=200",
                "032": "page=200 api=200 audio=200",
                "033": "page=200 api=200 audio=200",
                "034": "page=200 api=200 audio=200",
                "035": "page=200 api=200 audio=200",
                "036": "page=404 api=404",
            },
        },
        "corrections": {
            "029_poster_hash": "recalculated to match disk",
            "030_poster": "replaced child-safe sha=03A10CFB92FD5972A770E425A681F5896EB71823D6CC14E4E28657E9CDD392F2",
            "story_md": "Private staging review. Production publication requires owner approval.",
            "manifests": "publishable=false; private_staging_eligible=true",
        },
        "loudness_note": (
            "ElevenLabs peaks higher (~0.88-0.99) than OpenAI Marin (~0.61-0.75). "
            "No re-encode performed."
        ),
        "audio_frozen": True,
        "stories_001_025_unchanged": True,
        "providers": providers,
        "package_checksums": rows,
    }
    (work / "FINAL_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Stage 1 Corrective Lock Report — Stories 026–035",
        "",
        "**Verdict:** READY_FOR_OWNER_STAGE1_REVIEW",
        "",
        f"- Git SHA: `{report['git_sha']}`",
        f"- Stage 1 URL: {report['stage1_url']}",
        f"- Workflow: {report['workflow_run_url']}",
        f"- Content: `{report['content_tag']}` SHA-256 `{report['content_sha256']}`",
        f"- Staging max: {report['staging_public_story_max']}; Production max: {report['production_public_story_max']}",
        f"- Tests: {report['tests']['pytest']}",
        f"- Smoke: PASS — {report['stage1_smoke']['catalog_ok']}; Story 036 = 404",
        "",
        "## Loudness",
        report["loudness_note"],
        "",
        "## Providers",
    ]
    for key, value in providers.items():
        lines.append(
            f"- {key}: {value['provider']} peak={value['peak']} duration={value['duration_s']}s"
        )
    (work / "FINAL_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for src in [
        ROOT / "deploy/content/RELEASE_CONTENT_STAGING.json",
        ROOT / "deploy/content/RELEASE_CONTENT.json",
        ROOT / "work/_030_poster_childsafe/poster_evidence.json",
        ROOT
        / "work/tmp/content-001-035-staging/publish/bhava-content-001-035-staging-v1.tar.gz.sha256",
    ]:
        if src.is_file():
            (work / src.name).write_bytes(src.read_bytes())

    zip_path = out_dir / f"KSB_STORIES_026_035_STAGE1_CORRECTIVE_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in work.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=path.name)
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest().upper()
    print(zip_path)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
