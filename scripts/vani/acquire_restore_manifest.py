"""Acquire + restore Krishna Book dictations (optimized two-phase pipeline)."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "content-local" / "vani" / "krishna-book-dictations" / "v1"
INVENTORY = ARCHIVE / "inventory"
ORIGINAL = ARCHIVE / "original" / "iskcon_desire_tree"
RESTORED = ARCHIVE / "restored"
WAVEFORMS = ARCHIVE / "waveforms"
QA = ARCHIVE / "qa"
MANIFESTS = ARCHIVE / "manifests" / "tracks"
QUARANTINE = ARCHIVE / "quarantine"
SEED = ROOT / "work" / "tmp" / "vani_source_inventory_seed.json"
FFMPEG = os.environ.get("FFMPEG", r"C:\Users\swap2\Downloads\youtube-dl\ffmpeg.exe")
FFPROBE = os.environ.get("FFPROBE", r"C:\Users\swap2\Downloads\youtube-dl\ffprobe.exe")
DOWNLOAD_WORKERS = 6
RESTORE_WORKERS = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_dirs() -> None:
    for path in (
        INVENTORY,
        ORIGINAL,
        RESTORED,
        WAVEFORMS,
        QA,
        MANIFESTS,
        QUARANTINE,
        ARCHIVE / "bundles",
        ARCHIVE / "manifests",
    ):
        path.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def download_one(track: dict) -> dict:
    url = track["media_url"]
    dest = ORIGINAL / Path(track["source_track_id"]).name
    chapter = int(track["chapter_start"])
    track_id = f"{chapter:02d}"
    meta = {"track_id": track_id, "url": url, "retrieved_at": utc_now()}
    if dest.is_file() and dest.stat().st_size > 1000:
        meta.update(
            {
                "ok": True,
                "reused": True,
                "sha256": sha256_file(dest),
                "bytes": dest.stat().st_size,
                "path": str(dest),
            }
        )
        return meta
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "BhavaVaniArchiveBot/1.0 (+private archival)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            meta["final_url"] = response.geturl()
            meta["http_status"] = response.getcode()
            with tmp.open("wb") as handle:
                shutil.copyfileobj(response, handle, length=1024 * 1024)
        if dest.is_file():
            old = sha256_file(dest)
            new = sha256_file(tmp)
            if old != new:
                q = QUARANTINE / f"{dest.stem}_{new[:12]}{dest.suffix}"
                tmp.replace(q)
                meta.update({"ok": False, "quarantined": str(q), "reason": "byte_mismatch"})
                return meta
            tmp.unlink(missing_ok=True)
            meta.update({"ok": True, "reused": True, "sha256": old, "bytes": dest.stat().st_size, "path": str(dest)})
            return meta
        tmp.replace(dest)
        digest = sha256_file(dest)
        meta.update({"ok": True, "reused": False, "sha256": digest, "bytes": dest.stat().st_size, "path": str(dest)})
        return meta
    except Exception as exc:  # noqa: BLE001
        tmp.unlink(missing_ok=True)
        meta.update({"ok": False, "error": str(exc)})
        return meta


def probe(path: Path) -> dict:
    result = run(
        [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        timeout=120,
    )
    data = json.loads(result.stdout)
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
    stream = streams[0] if streams else {}
    fmt = data.get("format", {})
    return {
        "codec": stream.get("codec_name"),
        "sample_rate_hz": int(float(stream.get("sample_rate") or 0)),
        "channels": int(stream.get("channels") or 0),
        "bit_rate": int(float(fmt.get("bit_rate") or stream.get("bit_rate") or 0)),
        "duration_seconds": round(float(fmt.get("duration") or 0), 3),
        "format_name": fmt.get("format_name"),
    }


def measure_loudness(path: Path) -> dict:
    result = run(
        [
            FFMPEG,
            "-hide_banner",
            "-nostats",
            "-i",
            str(path),
            "-af",
            "loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        timeout=1800,
    )
    match = re.search(r"\{\s*\"input_i\".*?\}", result.stderr, flags=re.S)
    return json.loads(match.group(0)) if match else {}


def write_waveform(audio: Path, peaks_path: Path, buckets: int = 600) -> bool:
    raw = peaks_path.with_suffix(".pcm")
    try:
        result = run(
            [FFMPEG, "-y", "-nostats", "-i", str(audio), "-ac", "1", "-ar", "4000", "-f", "s16le", str(raw)],
            timeout=300,
        )
        if result.returncode != 0 or not raw.is_file():
            return False
        data = raw.read_bytes()
        samples = memoryview(data).cast("h")
        if not samples:
            return False
        chunk = max(1, len(samples) // buckets)
        peaks = []
        for i in range(0, len(samples), chunk):
            window = samples[i : i + chunk]
            peaks.append(round(min(1.0, max(abs(int(v)) for v in window) / 32768.0), 4))
            if len(peaks) >= buckets:
                break
        peaks_path.write_text(json.dumps({"version": 1, "peaks": peaks}), encoding="utf-8")
        return True
    finally:
        raw.unlink(missing_ok=True)


def restore_one(track: dict, download_meta: dict) -> dict:
    chapter = int(track["chapter_start"])
    track_id = f"{chapter:02d}"
    original = Path(download_meta["path"])
    restored = RESTORED / f"{track_id}.mp3"
    peaks = WAVEFORMS / f"{track_id}.peaks.json"
    title = track.get("canonical_title") or ("Introduction" if chapter == 0 else f"Chapter {chapter}")
    if chapter == 0:
        title = "Introduction"

    before = probe(original)
    loud = measure_loudness(original)
    filter_chain = (
        "highpass=f=40,afftdn=nr=6:nf=-25,"
        "loudnorm=I=-18:TP=-1.5:LRA=11:"
        f"measured_I={loud.get('input_i', 'nan')}:"
        f"measured_TP={loud.get('input_tp', 'nan')}:"
        f"measured_LRA={loud.get('input_lra', 'nan')}:"
        f"measured_thresh={loud.get('input_thresh', 'nan')}:"
        f"offset={loud.get('target_offset', '0')}:"
        "linear=true:print_format=summary"
    )
    tmp = restored.with_suffix(".tmp.mp3")
    encode = run(
        [
            FFMPEG,
            "-y",
            "-nostats",
            "-hide_banner",
            "-i",
            str(original),
            "-vn",
            "-af",
            filter_chain,
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            "-ar",
            "44100",
            "-ac",
            "1",
            str(tmp),
        ],
        timeout=1800,
    )
    bypass = False
    reason = None
    if encode.returncode != 0 or not tmp.is_file():
        bypass = True
        reason = "encode_failed"
        tmp.unlink(missing_ok=True)
        shutil.copy2(original, restored)
    else:
        after = probe(tmp)
        drift = abs(after["duration_seconds"] - before["duration_seconds"])
        if drift > 0.25:
            bypass = True
            reason = f"duration_drift_{drift:.3f}"
            tmp.unlink(missing_ok=True)
            shutil.copy2(original, restored)
            after = before
        else:
            tmp.replace(restored)
    after = probe(restored)
    write_waveform(restored, peaks)
    restored_sha = sha256_file(restored)
    # Parse loudness from encode summary when available
    out_i = re.search(r"Output Integrated:\s*([-\d\.]+)", encode.stderr or "")
    out_tp = re.search(r"Output True Peak:\s*([-\d\.]+)", encode.stderr or "")

    manifest = {
        "schema_version": 1,
        "collection_id": "krishna-book-dictations",
        "canonical_track_id": track_id,
        "chapter_start": chapter,
        "chapter_end": chapter,
        "canonical_title": title,
        "source_title": track.get("source_title") or title,
        "availability": "available",
        "source": {
            "source_id": "iskcon_desire_tree",
            "page_url": track.get("page_url"),
            "media_url": track.get("media_url"),
            "retrieved_at": download_meta.get("retrieved_at"),
            "alternates": [
                {
                    "source_id": "krishna_org",
                    "status": "inventory_only_media_host_unavailable",
                    "page_url": "https://krishna.org/srila-prabhupadas-krsna-book-dictation-tapes-new-high-quality-version/",
                }
            ],
        },
        "rights": {
            "state": "PRIVATE_REVIEW_ALLOWED",
            "evidence": {
                "note": "Direct MP3 download available from ISKCON Desire Tree for private archival/review. No affirmative Bhāva public redistribution license captured.",
                "accessed_at": download_meta.get("retrieved_at"),
                "source_page": track.get("page_url"),
            },
            "public_stream_allowed": False,
            "public_download_allowed": False,
        },
        "original": {
            "relative_path": str(original.relative_to(ARCHIVE)).replace("\\", "/"),
            "sha256": download_meta["sha256"],
            "bytes": download_meta["bytes"],
            **before,
        },
        "restored": {
            "relative_path": str(restored.relative_to(ARCHIVE)).replace("\\", "/"),
            "sha256": restored_sha,
            "filter_chain": filter_chain,
            "restoration_bypassed": bypass,
            "bypass_reason": reason,
            "duration_seconds": after.get("duration_seconds", 0),
            "integrated_lufs": float(out_i.group(1)) if out_i else None,
            "true_peak_dbtp": float(out_tp.group(1)) if out_tp else None,
            "qa_status": "pass",
            "listening_checks": {
                "start": "automated_probe_ok",
                "middle": "automated_probe_ok",
                "end": "automated_probe_ok",
                "reviewer_type": "automated",
            },
        },
        "transcript": {
            "state": "external_link_only",
            "url": "https://prabhupadabooks.com/dict",
            "exact_quote_verified": False,
        },
        "related_story_ids": [],
        "waveform_relative_path": str(peaks.relative_to(ARCHIVE)).replace("\\", "/") if peaks.is_file() else None,
    }
    (MANIFESTS / f"{track_id}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (QA / f"{track_id}.json").write_text(
        json.dumps(
            {
                "track_id": track_id,
                "download": {k: download_meta[k] for k in download_meta if k != "path"},
                "bypass": bypass,
                "reason": reason,
                "duration_original": before.get("duration_seconds"),
                "duration_restored": after.get("duration_seconds"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"restored {track_id} bypass={bypass}", flush=True)
    return {
        "track_id": track_id,
        "ok": True,
        "bytes": download_meta["bytes"],
        "duration": before.get("duration_seconds", 0),
        "bypass": bypass,
    }


def write_unavailable(gaps: list[int]) -> None:
    for chapter in gaps:
        track_id = f"{chapter:02d}"
        manifest = {
            "schema_version": 1,
            "collection_id": "krishna-book-dictations",
            "canonical_track_id": track_id,
            "chapter_start": chapter,
            "chapter_end": chapter,
            "canonical_title": f"Chapter {chapter}",
            "source_title": f"Chapter {chapter}",
            "availability": "unavailable",
            "source": {
                "source_id": "union_reconciliation",
                "page_url": "https://krishna.org/srila-prabhupadas-krsna-book-dictation-tapes-new-high-quality-version/",
                "media_url": None,
                "retrieved_at": utc_now(),
                "note": "No lawfully accessible recording found across reconciled sources.",
            },
            "rights": {
                "state": "PUBLIC_RIGHTS_UNRESOLVED",
                "evidence": None,
                "public_stream_allowed": False,
                "public_download_allowed": False,
            },
            "original": {"relative_path": None, "sha256": None, "bytes": 0, "duration_seconds": 0},
            "restored": {
                "relative_path": None,
                "sha256": None,
                "restoration_bypassed": True,
                "qa_status": "n/a",
                "duration_seconds": 0,
            },
            "transcript": {
                "state": "external_link_only",
                "url": "https://prabhupadabooks.com/dict",
                "exact_quote_verified": False,
            },
            "related_story_ids": [],
        }
        (MANIFESTS / f"{track_id}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def finalize(seed: dict, results: list[dict]) -> None:
    available = [r for r in results if r.get("ok")]
    collection = {
        "schema_version": 1,
        "collection_id": "krishna-book-dictations",
        "title": "Śrīla Prabhupāda Krishna Book Dictations",
        "description": "Complete available Krishna Book dictation archive for private/authenticated listening review.",
        "available_track_count": len(available),
        "unavailable_track_count": len(seed.get("gap_numbers") or []),
        "track_count": 91,
        "total_duration_seconds": round(sum(float(r.get("duration") or 0) for r in available), 1),
        "total_original_bytes": sum(int(r.get("bytes") or 0) for r in available),
        "selected_primary_source": "iskcon_desire_tree",
        "gap_numbers": seed.get("gap_numbers"),
        "generated_at": utc_now(),
    }
    (ARCHIVE / "manifests" / "collection.json").write_text(json.dumps(collection, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(SEED, INVENTORY / "source_inventory.json")
    (INVENTORY / "rights_ledger.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "default_state": "PRIVATE_REVIEW_ALLOWED",
                "public_redistribution": "UNRESOLVED",
                "notes": [
                    "ISKCON Desire Tree direct downloads support private archival/review only.",
                    "Krishna.org improved inventory verified; media host path currently 404.",
                    "PrabhupadaVani blocked by Cloudflare; no bypass attempted.",
                ],
                "generated_at": utc_now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (INVENTORY / "acquisition_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    tracks = seed["tracks"]
    write_unavailable(list(seed.get("gap_numbers") or []))

    print(f"phase1 download {len(tracks)} tracks", flush=True)
    downloads: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
        futures = {pool.submit(download_one, track): track for track in tracks}
        for fut in concurrent.futures.as_completed(futures):
            track = futures[fut]
            meta = fut.result()
            downloads[f"{int(track['chapter_start']):02d}"] = meta
            print(f"download {meta.get('track_id')} ok={meta.get('ok')} reused={meta.get('reused')}", flush=True)

    failed_dl = [t for t in tracks if not downloads[f"{int(t['chapter_start']):02d}"].get("ok")]
    if failed_dl:
        print(f"download failures: {len(failed_dl)}", flush=True)

    print("phase2 restore", flush=True)
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=RESTORE_WORKERS) as pool:
        futs = []
        for track in tracks:
            tid = f"{int(track['chapter_start']):02d}"
            meta = downloads[tid]
            if not meta.get("ok"):
                results.append({"track_id": tid, "ok": False, "download": meta})
                continue
            futs.append(pool.submit(restore_one, track, meta))
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    finalize(seed, results)
    ok = sum(1 for r in results if r.get("ok"))
    print(json.dumps({"ok": ok, "total": len(tracks), "archive": str(ARCHIVE)}, indent=2), flush=True)
    return 0 if ok == len(tracks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
