from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import Settings
from .models import PackagePaths, PlanRow, StoryContent, extract_main_story, word_count
from .outputs import FINAL_OUTPUT_FILES
from .activities.planner import ActivityPlan


def _is_publishable(
    *,
    mode: str,
    quality_status: str,
    quality_errors: list[str] | None,
    audio_metadata: dict | None,
    narration_source_sha: str = "",
    audio_source: str = "",
    package_dir=None,
) -> bool:
    """Publishable only for verified, non-stale, error-free production packages.

    Requires generation_verified audio with real provider + hashes and an exact
    eight-file package. Unknown/preserved/stale audio is never publishable.
    """
    meta = dict(audio_metadata or {})
    audio_stale = bool(meta.get("audio_stale")) or quality_status == "AUDIO_STALE"
    provider = str(meta.get("provider") or audio_source or "").strip()
    if provider in {"", "preserved", "unknown_preserved"}:
        return False
    if not bool(meta.get("generation_verified")):
        return False
    sha_ok = bool(str(narration_source_sha or meta.get("narration_source_sha") or "").strip())
    audio_sha_ok = bool(str(meta.get("sha256") or "").strip())
    if not sha_ok or not audio_sha_ok:
        return False
    if package_dir is not None:
        from .package_swap import validate_exact_eight_files

        if validate_exact_eight_files(package_dir):
            return False
    return (
        mode != "test"
        and quality_status == "PASS"
        and not list(quality_errors or [])
        and not audio_stale
        and bool(meta.get("generation_verified"))
    )


def write_manifest(
    *,
    settings: Settings,
    plan: PlanRow,
    content: StoryContent,
    paths: PackagePaths,
    mode: str,
    quality_status: str,
    quality_errors: list[str],
    quality_warnings: list[str] | None = None,
    audio_source: str = "",
    package_link: str = "",
    drive_status: str = "",
    drive_detail: str = "",
    poster_score: int = 0,
    coloring_score: int = 0,
    simple_coloring_score: int = 0,
    reference_used: bool = False,
    activity: ActivityPlan | None = None,
    activity_page_count: int = 0,
    activity_score: int = 0,
    poster_reference_used: bool = False,
    style_reference_used: bool = False,
    identity_consistency_score: int = 0,
    waveform_metrics=None,
    matching_coverage: dict | None = None,
    parent_answer_key: dict | None = None,
    audio_metadata: dict | None = None,
) -> None:
    now = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
    story_text = paths.story_md.read_text(encoding="utf-8") if paths.story_md.exists() else ""
    main_story_words = word_count(extract_main_story(story_text))
    audio_words = word_count(content.audio_script)
    audio_duration = _mp3_duration(paths.narration_mp3)
    audio_size = paths.narration_mp3.stat().st_size if paths.narration_mp3.exists() else 0
    metrics = {
        "main_story_words": main_story_words,
        "audio_script_words": audio_words,
        "audio_duration_seconds": audio_duration,
        "audio_bytes": audio_size,
    }
    if waveform_metrics is not None:
        metrics.update(
            {
                "peak": getattr(waveform_metrics, "peak", None),
                "clipping_ratio": getattr(waveform_metrics, "clipping_ratio", None),
                "longest_silence_seconds": getattr(waveform_metrics, "longest_silence_seconds", None),
                "waveform_validation_status": getattr(waveform_metrics, "status", None),
            }
        )
    manifest = {
        "app": "krishna-story-factory",
        "version": "2.0",
        "generated_at": now,
        "chapter_no": plan.chapter_no,
        "slug": plan.slug,
        "title": content.title,
        "source_reference": plan.source_reference,
        "scripture_reference": plan.scripture_reference,
        "age_range": plan.age_range,
        "outputs": list(FINAL_OUTPUT_FILES),
        "metrics": metrics,
        "images": {
            "model": settings.openai_image_model,
            "quality": settings.openai_image_quality,
            "requested_size": settings.openai_image_size,
            "reference_image_used": reference_used,
            "poster_qa_score": poster_score,
            "coloring_qa_score": coloring_score,
            "simple_coloring_qa_score": simple_coloring_score,
            "coloring_generation": {
                "poster_reference_used": poster_reference_used,
                "style_reference_used": style_reference_used,
                "qa_score": coloring_score,
                "identity_consistency_score": identity_consistency_score,
            },
            "simple_coloring_generation": {
                "qa_score": simple_coloring_score,
            },
        },
        "activity": {
            "type": activity.activity_type if activity else "",
            "title": activity.activity_title if activity else "",
            "recommended_send_mode": activity.recommended_send_mode if activity else "",
            "estimated_minutes": activity.estimated_minutes if activity else 0,
            "parent_effort": activity.parent_effort if activity else "",
            "page_count": activity_page_count,
            "qa_score": activity_score,
            "answer_key": activity.answer_key if activity and activity.answer_key else [],
            "matching_coverage": matching_coverage or {},
            "parent_answer_key": parent_answer_key or {},
        },
        "quality": {
            "status": quality_status,
            "errors": quality_errors,
            "warnings": quality_warnings or [],
        },
        "package": {
            "package_link": package_link,
            "drive_status": drive_status,
            "drive_detail": drive_detail,
        },
        "queue_transition": "unchanged" if mode == "test" else ("done" if quality_status == "PASS" else "pending"),
        "mode": mode,
        "audio_source": audio_source or "unknown_preserved",
        "audio": _normalize_audio_metadata(audio_metadata, paths=paths, waveform_metrics=waveform_metrics),
        "narration_source_sha": (
            (audio_metadata or {}).get("narration_source_sha")
            if isinstance(audio_metadata, dict) and audio_metadata.get("narration_source_sha")
            else ""
        ),
    }
    # Mirror stale flag onto audio block for consumers.
    if isinstance(manifest["audio"], dict):
        stale = bool(manifest["audio"].get("audio_stale")) or quality_status == "AUDIO_STALE"
        manifest["audio"]["audio_stale"] = stale
    # Only mint a fresh narration_source_sha when audio was just verified/generated.
    # Preserved/stale packages must keep a missing or prior hash so drift stays detectable.
    verified = bool(isinstance(audio_metadata, dict) and audio_metadata.get("generation_verified"))
    stale_flag = bool(isinstance(audio_metadata, dict) and audio_metadata.get("audio_stale"))
    if not manifest["narration_source_sha"] and content.audio_script and verified and not stale_flag:
        from .audio.drift import narration_source_sha

        manifest["narration_source_sha"] = narration_source_sha(content.audio_script)
        if isinstance(manifest["audio"], dict):
            manifest["audio"]["narration_source_sha"] = manifest["narration_source_sha"]
    elif isinstance(audio_metadata, dict) and audio_metadata.get("current_narration_source_sha"):
        if isinstance(manifest["audio"], dict):
            manifest["audio"]["current_narration_source_sha"] = audio_metadata["current_narration_source_sha"]
            manifest["audio"]["audio_stale"] = True
    # Final publishable gate uses normalized audio + hashes + exact eight-file check.
    audio_block = manifest["audio"] if isinstance(manifest["audio"], dict) else {}
    manifest["publishable"] = _is_publishable(
        mode=mode,
        quality_status=quality_status,
        quality_errors=quality_errors,
        audio_metadata=audio_block,
        narration_source_sha=str(manifest.get("narration_source_sha") or ""),
        audio_source=str(manifest.get("audio_source") or ""),
        package_dir=paths.root,
    )
    # Never claim an exact seven-file Drive package.
    detail = str(manifest["package"].get("drive_detail") or "")
    if "seven file" in detail.lower() or "seven-file" in detail.lower():
        manifest["package"]["drive_detail"] = detail.replace("seven", "eight").replace("Seven", "Eight")
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def _normalize_audio_metadata(audio_metadata: dict | None, *, paths: PackagePaths, waveform_metrics=None) -> dict:
    meta = dict(audio_metadata or {})
    if not meta:
        meta = {
            "provider": "unknown_preserved",
            "model_id": None,
            "voice": None,
            "generation_verified": False,
        }
    if meta.get("provider") in {"", "preserved"}:
        meta["provider"] = "unknown_preserved"
        meta["generation_verified"] = False
        meta.setdefault("model_id", None)
        meta.setdefault("voice", None)
    if paths.narration_mp3.exists() and not meta.get("sha256"):
        import hashlib

        raw = paths.narration_mp3.read_bytes()
        meta["sha256"] = hashlib.sha256(raw).hexdigest().upper()
        meta["bytes"] = len(raw)
    if meta.get("duration_seconds") is None:
        meta["duration_seconds"] = _mp3_duration(paths.narration_mp3)
    if waveform_metrics is not None:
        meta["waveform_validation_status"] = getattr(waveform_metrics, "status", None)
    return meta


def update_component_manifest(
    path, *, activity: ActivityPlan, activity_page_count: int, activity_score: int,
    coloring_score: int, identity_consistency_score: int, poster_reference_used: bool,
    style_reference_used: bool, drive_status: str | None = None, drive_detail: str | None = None,
    coloring_model: str = "", model_override: str = "", coloring_requested_size: str = "1024x1536",
    matching_coverage: dict | None = None,
    parent_answer_key: dict | None = None,
    simple_coloring_score: int | None = None,
) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["generated_at"] = datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    data["activity"] = {
        "type": activity.activity_type, "title": activity.activity_title,
        "recommended_send_mode": activity.recommended_send_mode,
        "estimated_minutes": activity.estimated_minutes, "parent_effort": activity.parent_effort,
        "page_count": activity_page_count, "qa_score": activity_score,
        "answer_key": activity.answer_key,
        "matching_coverage": matching_coverage or data.get("activity", {}).get("matching_coverage") or {},
        "parent_answer_key": parent_answer_key
        if parent_answer_key is not None
        else data.get("activity", {}).get("parent_answer_key") or {},
    }
    images = data.setdefault("images", {})
    images["coloring_qa_score"] = coloring_score
    if simple_coloring_score is not None:
        images["simple_coloring_qa_score"] = simple_coloring_score
        images["simple_coloring_generation"] = {"qa_score": simple_coloring_score}
    images["coloring_generation"] = {
        "poster_reference_used": poster_reference_used, "style_reference_used": style_reference_used,
        "qa_score": coloring_score, "identity_consistency_score": identity_consistency_score,
        "model": coloring_model or images.get("model", ""),
        "model_override": model_override,
        "requested_size": coloring_requested_size,
    }
    if drive_status is not None:
        package = data.setdefault("package", {})
        package["drive_status"] = drive_status
        package["drive_detail"] = drive_detail or ""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _mp3_duration(path) -> float | None:
    try:
        from mutagen.mp3 import MP3

        return round(float(MP3(path).info.length), 1)
    except Exception:
        return None
