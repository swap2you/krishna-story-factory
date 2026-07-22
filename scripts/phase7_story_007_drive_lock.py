"""Phase 7: validate local Story 007, replace Drive files, hash-verify, advance queue.

No paid generation APIs. Upload/readback only.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from mutagen.mp3 import MP3
from PIL import Image

from krishna_story_factory.config import load_settings
from krishna_story_factory.content.story_007_locked import build_story_007_locked
from krishna_story_factory.csv_store import read_plan_by_chapter, update_plan_status
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.package_swap import validate_exact_eight_files
from krishna_story_factory.paths import make_package_paths
from krishna_story_factory.pdf.activity_sheet import validate_activity_pdf
from krishna_story_factory.quality.checks import run_quality_checks
from krishna_story_factory.run_summary import write_latest_run_summary
from krishna_story_factory.audio.waveform import validate_mp3_waveform
from krishna_story_factory.storage.google_drive_uploader import (
    _build_drive_service,
    upload_files_to_folder,
    verify_drive_text_links,
)


def _download_drive_bytes(service, folder_id: str, filename: str) -> bytes:
    from googleapiclient.http import MediaIoBaseDownload
    import io

    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    files = service.files().list(q=query, fields="files(id,name)", pageSize=1).execute().get("files", [])
    if not files:
        raise FileNotFoundError(f"{filename} not found in Drive folder {folder_id}")
    request = service.files().get_media(fileId=files[0]["id"])
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "output" / "007_kamsa-begins-his-persecutions"
FOLDER_ID = "12KjkBOc42AFvIlbUSFZHPZdCDUlZRW8v"
PACKAGE_LINK = f"https://drive.google.com/drive/folders/{FOLDER_ID}?usp=sharing"
REQUIRED = list(FINAL_OUTPUT_FILES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    errs = validate_exact_eight_files(PKG)
    if errs:
        print("EXACT_EIGHT_FAIL:", " | ".join(errs))
        return 1
    local_hashes = {name: sha256(PKG / name) for name in REQUIRED}
    print("LOCAL_EXACT_EIGHT PASS")
    for name in REQUIRED:
        print(f"LOCAL {name} {local_hashes[name]}")

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "007")
    content = build_story_007_locked(plan)
    guard = run_source_guard(plan, content)
    if guard:
        print("SOURCE_GUARD_FAIL:", " | ".join(guard))
        return 1

    story_text = (PKG / "story.md").read_text(encoding="utf-8").lower()
    import re

    # Strip parent-guidance sentences that prohibit the false imprisonment claim.
    scan_text = re.sub(
        r"do not teach that[^.]*remained imprisoned[^.]*\.",
        " ",
        story_text,
        flags=re.I,
    )
    for bad in (
        "every baby boy",
        "remained imprisoned",
        "magician",
        "potion",
        "pralamba",
        "aghasura",
    ):
        if bad in scan_text:
            print("SOURCE_SCAN_FAIL forbidden:", bad)
            return 1

    manifest = json.loads((PKG / "manifest.json").read_text(encoding="utf-8"))
    poster = int(((manifest.get("images") or {}).get("poster_qa_score") or 0))
    coloring = int(((manifest.get("images") or {}).get("coloring_qa_score") or 0))
    paths = make_package_paths(ROOT / "output", plan)
    ok, qerrs, _qwarns = run_quality_checks(
        paths,
        mode="prod",
        settings=settings,
        story_title=plan.title,
        poster_score=poster,
        coloring_score=coloring,
        require_manifest=True,
    )
    if not ok:
        print("QUALITY_FAIL:", " | ".join(qerrs))
        return 1

    mp3 = PKG / "narration.mp3"
    if mp3.stat().st_size <= 500 * 1024:
        print("AUDIO_SIZE_FAIL")
        return 1
    dur = float(MP3(mp3).info.length)
    if dur < 180 or dur > 360:
        print(f"AUDIO_DURATION_FAIL {dur}")
        return 1
    metrics = validate_mp3_waveform(mp3, expected_duration=dur)
    if metrics.status != "PASS":
        print("WAVEFORM_FAIL", metrics.detail)
        return 1

    render_dir = ROOT / ".work" / "phase7_activity_pages"
    render_dir.mkdir(parents=True, exist_ok=True)
    pdf_check = validate_activity_pdf(PKG / "activity_sheet.pdf", render_dir, activity=None)
    if pdf_check.errors:
        print("PDF_FAIL:", " | ".join(pdf_check.errors))
        return 1

    for img_name in ("story_poster.png", "coloring_page.png", "simple_coloring_page.png"):
        p = PKG / img_name
        if p.stat().st_size < 1000:
            print("IMAGE_SIZE_FAIL", img_name)
            return 1
        with Image.open(p) as im:
            im.verify()

    audio_meta = dict(manifest.get("audio") or {})
    print("LOCAL_VALIDATION PASS")
    print(
        f"audio_duration={dur:.1f} provider={audio_meta.get('provider')} "
        f"voice={audio_meta.get('voice')}"
    )

    uploaded = upload_files_to_folder(
        settings,
        folder_id=FOLDER_ID,
        package_link=PACKAGE_LINK,
        source_dir=PKG,
        files=tuple(REQUIRED),
        folder_name=PKG.name,
    )
    if uploaded.status != "UPLOADED":
        print("DRIVE_UPLOAD_FAIL", uploaded.status, uploaded.detail)
        return 1
    print("DRIVE_UPLOAD", uploaded.status, uploaded.detail)

    token = settings.google_drive_token_file or ROOT / "credentials" / "google_drive_token.json"
    service = _build_drive_service(settings.google_drive_credentials_file, token)
    drive_hashes: dict[str, str] = {}
    mismatches: list[str] = []
    for name in REQUIRED:
        remote = _download_drive_bytes(service, FOLDER_ID, name)
        if not remote:
            print("DRIVE_READBACK_MISSING", name)
            return 1
        h = hashlib.sha256(remote).hexdigest().upper()
        drive_hashes[name] = h
        print(f"DRIVE {name} {h}")
        if h != local_hashes[name]:
            mismatches.append(name)

    ok_links, link_detail = verify_drive_text_links(
        settings, folder_id=FOLDER_ID, package_link=PACKAGE_LINK
    )
    print("DRIVE_TEXT_LINKS", ok_links, link_detail)
    if mismatches or not ok_links:
        print("HASH_MISMATCH", mismatches)
        print("FAIL_SAFE: hashes or link verify failed; queue NOT advanced")
        return 1
    print("HASH_COMPARE PASS")

    now = datetime.now(ZoneInfo(settings.app_timezone))
    audio = dict(manifest.get("audio") or {})
    audio["audio_stale"] = False
    audio["generation_verified"] = True
    manifest["audio"] = audio
    manifest["audio_source"] = audio.get("provider") or manifest.get("audio_source") or "openai"
    manifest["publishable"] = True
    manifest["quality"] = {"status": "PASS", "errors": [], "warnings": []}
    manifest["package"] = {
        "package_link": PACKAGE_LINK,
        "drive_status": "UPLOADED",
        "drive_detail": f"Replaced and hash-verified {len(REQUIRED)} final file(s).",
    }
    manifest["queue_transition"] = {"from": "pending", "to": "done", "next_pending": "008"}
    manifest["generated_at"] = now.isoformat(timespec="seconds")
    (PKG / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    uploaded2 = upload_files_to_folder(
        settings,
        folder_id=FOLDER_ID,
        package_link=PACKAGE_LINK,
        source_dir=PKG,
        files=("manifest.json",),
        folder_name=PKG.name,
    )
    if uploaded2.status != "UPLOADED":
        print("MANIFEST_REUPLOAD_FAIL", uploaded2.status, uploaded2.detail)
        return 1

    local_hashes["manifest.json"] = sha256(PKG / "manifest.json")
    remote_m = _download_drive_bytes(service, FOLDER_ID, "manifest.json")
    drive_hashes["manifest.json"] = hashlib.sha256(remote_m).hexdigest().upper()
    if local_hashes["manifest.json"] != drive_hashes["manifest.json"]:
        print("MANIFEST_HASH_MISMATCH_AFTER_UPDATE")
        return 1
    ok_links2, link_detail2 = verify_drive_text_links(
        settings, folder_id=FOLDER_ID, package_link=PACKAGE_LINK
    )
    if not ok_links2:
        print("POST_MANIFEST_LINK_FAIL", link_detail2)
        return 1

    update_plan_status(ROOT, plan, "done", drive_folder_id=FOLDER_ID)
    qpath = ROOT / "tracking" / "queue_state.csv"
    rows = list(csv.DictReader(qpath.open(encoding="utf-8", newline="")))
    fields = list(rows[0].keys())
    for row in rows:
        if row["chapter_no"].zfill(3) == "008":
            row["status"] = "pending"
            row["updated_at"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    with qpath.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    write_latest_run_summary(
        ROOT,
        started_at=now.isoformat(timespec="seconds"),
        completed_at=now.isoformat(timespec="seconds"),
        status="SUCCESS",
        chapter_no="007",
        title=plan.title,
        package_local_path=str(PKG),
        drive_folder_url=PACKAGE_LINK,
        provider=str(audio.get("provider") or "openai"),
        audio_duration=float(audio.get("duration_seconds") or dur),
        publishable=True,
        exact_eight_files=True,
        queue_advanced=True,
        next_pending="008",
        error_code="",
        error_summary="Phase 7 Drive replace + hash verify PASS; MWF re-enable next.",
    )

    print("QUEUE_AND_MANIFEST PASS")
    print(json.dumps({"local_hashes": local_hashes, "drive_hashes": drive_hashes}, indent=2))
    print("publishable", True)
    print("quality", "PASS")
    print("audio_stale", False)
    print("next_pending", "008")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
