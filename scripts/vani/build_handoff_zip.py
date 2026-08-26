"""Build final Vāṇī archive handoff ZIP (evidence only; media bundle referenced)."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "content-local" / "vani" / "krishna-book-dictations" / "v1"
OUT_DIR = ROOT / "MyPilotDropbox" / "BHAVA" / "release-handoffs"
KIT_TEMPLATES = (
    ROOT
    / "work"
    / "_vani_archive_execution_kit"
    / "BHAVA_PRABHUPADA_VANI_COMPLETE_ARCHIVE_EXECUTION_KIT_V1"
    / "templates"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = ROOT / "work" / "tmp" / f"vani_handoff_{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    collection = json.loads((ARCHIVE / "manifests" / "collection.json").read_text(encoding="utf-8"))
    inventory = json.loads((ARCHIVE / "inventory" / "source_inventory.json").read_text(encoding="utf-8"))
    rights = json.loads((ARCHIVE / "inventory" / "rights_ledger.json").read_text(encoding="utf-8"))
    results = json.loads((ARCHIVE / "inventory" / "acquisition_results.json").read_text(encoding="utf-8"))
    bundle_manifest_path = ARCHIVE / "bundles" / "BUNDLE_MANIFEST.json"
    bundle_manifest = (
        json.loads(bundle_manifest_path.read_text(encoding="utf-8")) if bundle_manifest_path.is_file() else {}
    )
    pin_path = ROOT / "deploy" / "content" / "RELEASE_VANI_CONTENT.json"
    pin = json.loads(pin_path.read_text(encoding="utf-8")) if pin_path.is_file() else {}

    originals = list((ARCHIVE / "original").rglob("*.mp3"))
    restored = list((ARCHIVE / "restored").glob("*.mp3"))
    report = {
        "verdict": "READY_FOR_OWNER_PRIVATE_REVIEW — PUBLIC_RIGHTS_GATE_PENDING",
        "generated_at": stamp,
        "code_sha": None,
        "staging_workflow_url": None,
        "production_state": "unchanged",
        "collection": collection,
        "canonical_records": 91,
        "acquired_tracks": sum(1 for r in results if r.get("ok")),
        "real_gaps": collection.get("gap_numbers"),
        "total_duration_seconds": collection.get("total_duration_seconds"),
        "total_original_bytes": collection.get("total_original_bytes"),
        "selected_primary_source": "iskcon_desire_tree",
        "rights_state": rights.get("public_redistribution"),
        "original_count": len(originals),
        "restored_count": len(restored),
        "media_bundle": bundle_manifest,
        "release_pin": pin,
        "tests": {},
        "route_matrix": {},
        "rollback_pointer": None,
        "cleanup": "execution scratch under work/tmp retained selectively; content-local is canonical archive",
        "remaining_owner_action": [
            "Review Stage 1 UX/audio quality on staging.bhava.me (authenticated).",
            "Provide affirmative public redistribution authority (BBT/rights holder) before production exposure.",
            "Approve production promotion only after rights and Stage 1 acceptance.",
        ],
    }
    (work / "FINAL_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (work / "FINAL_REPORT.md").write_text(
        "\n".join(
            [
                f"# {report['verdict']}",
                "",
                f"- Canonical records: {report['canonical_records']}",
                f"- Acquired tracks: {report['acquired_tracks']}",
                f"- Gaps: {report['real_gaps']}",
                f"- Duration seconds: {report['total_duration_seconds']}",
                f"- Original bytes: {report['total_original_bytes']}",
                f"- Primary source: {report['selected_primary_source']}",
                f"- Public rights: {report['rights_state']}",
                f"- Media bundle: {bundle_manifest}",
                "",
                "## Remaining owner action",
                *[f"- {item}" for item in report["remaining_owner_action"]],
                "",
            ]
        ),
        encoding="utf-8",
    )

    for src, name in [
        (ROOT / "docs/engineering/VANI_KRISHNA_BOOK_DICTATION_DESIGN.md", "DESIGN.md"),
        (ROOT / "docs/engineering/VANI_KRISHNA_BOOK_DICTATION_RTM.md", "REQUIREMENTS_TRACEABILITY.md"),
        (ARCHIVE / "inventory" / "source_inventory.json", "SOURCE_INVENTORY.json"),
        (ARCHIVE / "inventory" / "rights_ledger.json", "RIGHTS_LEDGER.json"),
        (ARCHIVE / "inventory" / "acquisition_results.json", "ACQUISITION_RESULTS.json"),
        (ARCHIVE / "manifests" / "collection.json", "COLLECTION_MANIFEST.json"),
        (pin_path, "RELEASE_VANI_CONTENT.json"),
        (bundle_manifest_path, "BUNDLE_MANIFEST.json"),
    ]:
        if src.is_file():
            shutil.copy2(src, work / name)

    # Checksum ledgers
    original_ledger = {
        str(p.relative_to(ARCHIVE)).replace("\\", "/"): {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }
        for p in originals
    }
    restored_ledger = {
        p.name: {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "bytes": p.stat().st_size,
        }
        for p in restored
    }
    (work / "ORIGINAL_CHECKSUMS.json").write_text(json.dumps(original_ledger, indent=2) + "\n", encoding="utf-8")
    (work / "RESTORED_CHECKSUMS.json").write_text(json.dumps(restored_ledger, indent=2) + "\n", encoding="utf-8")

    qa_dir = work / "qa"
    qa_dir.mkdir(exist_ok=True)
    for path in (ARCHIVE / "qa").glob("*.json"):
        shutil.copy2(path, qa_dir / path.name)

    tracks_dir = work / "track_manifests"
    tracks_dir.mkdir(exist_ok=True)
    for path in (ARCHIVE / "manifests" / "tracks").glob("*.json"):
        shutil.copy2(path, tracks_dir / path.name)

    zip_path = OUT_DIR / f"KSB_VANI_KRISHNA_BOOK_DICTATIONS_{stamp}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in work.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(work)).replace("\\", "/"))
    digest = sha256_file(zip_path)
    (OUT_DIR / f"{zip_path.name}.sha256").write_text(f"{digest}  {zip_path.name}\n", encoding="utf-8")
    # verify extract
    verify = ROOT / "work" / "tmp" / f"vani_handoff_verify_{stamp}"
    verify.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(verify)
    assert (verify / "FINAL_REPORT.json").is_file()
    print(f"ZIP={zip_path}")
    print(f"ZIP_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
