#!/usr/bin/env python3
"""Repair Story 021 narration + activity only (no image/caption regeneration).

- Deterministically sync Audio Narration = Main Story (no LLM rewrite)
- Sample-first + one full TTS
- Rebuild activity from ActivityStoryMap
- Preserve poster/coloring/simple_coloring/whatsapp hashes
- Optional Drive replace for changed finals
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CHAPTER = "021"
LOCKED_HASH_FILES = (
    "story_poster.png",
    "coloring_page.png",
    "simple_coloring_page.png",
    "whatsapp_caption.txt",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    from mutagen.mp3 import MP3

    from krishna_story_factory.activities.models import SequenceCard
    from krishna_story_factory.activities.planner import ActivityPlanner
    from krishna_story_factory.activities.story_map import (
        evaluate_activity_semantic_qa,
        write_activity_semantic_qa,
    )
    from krishna_story_factory.audio.drift import narration_source_sha
    from krishna_story_factory.audio.pace import evaluate_pace_qa, write_audio_quality_qa
    from krishna_story_factory.audio.provider import reset_provider_preflight_cache, select_audio_provider
    from krishna_story_factory.audio.punctuation_gate import evaluate_punctuation_gate
    from krishna_story_factory.audio.sample_pipeline import run_sample_first
    from krishna_story_factory.audio.tts import AudioGenerator
    from krishna_story_factory.audio.waveform import validate_mp3_waveform
    from krishna_story_factory.config import load_settings
    from krishna_story_factory.content.canonical_narration import (
        evaluate_canonical_narration_exact,
        extract_main_story,
        sync_audio_narration_from_main_story,
        write_canonical_narration_qa,
    )
    from krishna_story_factory.content.parent_answer_key import (
        build_parent_answer_key,
        validate_parent_answer_key,
    )
    from krishna_story_factory.csv_store import read_plan_by_chapter
    from krishna_story_factory.paths import make_package_paths
    from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
    from krishna_story_factory.storage.google_drive_uploader import replace_existing_files

    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, CHAPTER)
    assert plan is not None
    paths = make_package_paths(settings.output_root, plan, create=False)
    before_locked = {name: _sha(paths.root / name) for name in LOCKED_HASH_FILES}

    stamp = datetime.now(ZoneInfo(settings.app_timezone)).strftime("%Y%m%d-%H%M%S")
    work = ROOT / "work" / "stories" / CHAPTER / f"repair-gates-{stamp}"
    work.mkdir(parents=True, exist_ok=True)
    evidence = (
        ROOT
        / "MyPilotDropbox"
        / "bhava-production-ops"
        / "evidence"
        / "permanent-audio-activity-gates-story-021-022-20260803"
    )
    evidence.mkdir(parents=True, exist_ok=True)

    original_md = paths.story_md.read_text(encoding="utf-8")
    main_before = extract_main_story(original_md)
    synced_md = sync_audio_narration_from_main_story(original_md)
    main_after = extract_main_story(synced_md)
    if main_before != main_after:
        raise SystemExit("FAIL: Main Story wording changed during canonical sync")
    paths.story_md.write_text(synced_md, encoding="utf-8")
    audio_script = extract_main_story(synced_md)

    canon = evaluate_canonical_narration_exact(
        story_no=CHAPTER, story_md=synced_md, tts_source=audio_script
    )
    write_canonical_narration_qa(canon, work / "canonical_narration_qa.json")
    write_canonical_narration_qa(canon, evidence / "021_canonical_narration_qa.json")
    if canon.result != "PASS":
        raise SystemExit(f"Canonical QA FAIL: {canon.failure_reasons}")

    punct = evaluate_punctuation_gate(audio_script)
    (work / "punctuation_gate.json").write_text(
        json.dumps(
            {
                "status": punct.status,
                "failures": list(punct.failures),
                "warnings": list(punct.warnings),
                "detail": punct.detail,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if punct.status != "PASS":
        raise SystemExit(f"Punctuation FAIL: {punct.detail}")

    reuse_narration = "--reuse-narration" in sys.argv
    staging_mp3 = work / "narration.mp3"
    sample_retry = 0
    source = "openai"
    audio = None
    decision = None
    sample = None

    if reuse_narration:
        candidates = sorted(ROOT.glob("work/stories/021/repair-gates-*/narration.mp3"))
        chosen = None
        for cand in reversed(candidates):
            dur = float(MP3(cand).info.length)
            pace_try = evaluate_pace_qa(narration_text=audio_script, duration_seconds=dur)
            if pace_try.status == "PASS":
                chosen = cand
                break
        if chosen is None:
            raise SystemExit("No reusable narration.mp3 with PASS pace found under work/stories/021/")
        shutil.copy2(chosen, staging_mp3)
        print(f"Reusing narration from {chosen}")
        duration = float(MP3(staging_mp3).info.length)
        wave = validate_mp3_waveform(staging_mp3, expected_duration=duration)
        pace = evaluate_pace_qa(narration_text=audio_script, duration_seconds=duration)
        audio_qa = {
            "provider": "openai",
            "model": "gpt-4o-mini-tts-2025-12-15",
            "voice": "marin",
            "settings_hash": "reused",
            "canonical_narration_hash": canon.canonical_normalized_sha256,
            "duration": round(duration, 3),
            "spoken_word_count": pace.spoken_word_count,
            "measured_wpm": pace.measured_wpm,
            "peak": wave.peak,
            "clipping_ratio": wave.clipping_ratio,
            "longest_silence": wave.longest_silence_seconds,
            "punctuation_gate": punct.status,
            "canonical_exact_match": canon.exact_match,
            "sample_retry_count": 0,
            "waveform_status": wave.status,
            "pace_status": pace.status,
            "human_listening_status": "HUMAN_REVIEW_PENDING",
            "detail": f"reused {chosen.parent.name}; {pace.detail}",
        }
    else:
        reset_provider_preflight_cache()
        decision = select_audio_provider(settings, estimated_chars=len(audio_script), require_dictionary=False)
        print(f"provider={decision.provider} status={decision.status} model={decision.model_id} voice={decision.voice}")
        if decision.status != "READY":
            raise SystemExit(f"Provider not READY: {decision}")

        audio = AudioGenerator(settings, mode="prod")
        sample = run_sample_first(
            audio_gen=audio,
            narration_text=audio_script,
            work_dir=work,
            provider_decision=decision,
            mode="prod",
            project_root=ROOT,
        )
        print(f"sample_retry={sample.retry_count} sample_dur={sample.qa.duration_seconds}")
        sample_retry = sample.retry_count

        source = audio.generate_mp3(
            audio_script,
            staging_mp3,
            provider_decision=decision,
            work_dir=work,
        )
        duration = float(MP3(staging_mp3).info.length)
        wave = validate_mp3_waveform(staging_mp3, expected_duration=duration)
        pace = evaluate_pace_qa(narration_text=audio_script, duration_seconds=duration)
        audio_qa = {
            "provider": audio.last_provider or source,
            "model": audio.last_model_id,
            "voice": audio.last_voice_name or audio.last_voice_id,
            "settings_hash": sample.binding.get("settings_hash"),
            "canonical_narration_hash": canon.canonical_normalized_sha256,
            "duration": round(duration, 3),
            "spoken_word_count": pace.spoken_word_count,
            "measured_wpm": pace.measured_wpm,
            "peak": wave.peak,
            "clipping_ratio": wave.clipping_ratio,
            "longest_silence": wave.longest_silence_seconds,
            "leading_silence": getattr(wave, "leading_silence_seconds", None),
            "trailing_silence": getattr(wave, "trailing_silence_seconds", None),
            "punctuation_gate": punct.status,
            "pronunciation_gate": "PENDING_REPORT",
            "canonical_exact_match": canon.exact_match,
            "sample_retry_count": sample.retry_count,
            "waveform_status": wave.status,
            "pace_status": pace.status,
            "human_listening_status": "HUMAN_REVIEW_PENDING",
            "detail": pace.detail,
        }
    write_audio_quality_qa(audio_qa, work / "audio_quality_qa.json")
    write_audio_quality_qa(audio_qa, evidence / "021_audio_quality_qa.json")
    if wave.status != "PASS":
        raise SystemExit(f"Waveform FAIL: {wave.detail}")
    if pace.status != "PASS":
        raise SystemExit(f"Pace FAIL: {pace.detail}")

    archive = ROOT / "output" / "_archive" / f"021_pre_gate_repair_{stamp}"
    archive.mkdir(parents=True, exist_ok=True)
    for name in ("narration.mp3", "activity_sheet.pdf", "manifest.json", "story.md"):
        src = paths.root / name
        if src.exists():
            shutil.copy2(src, archive / name)
    shutil.copy2(staging_mp3, paths.narration_mp3)

    # Activity rebuild
    planner = ActivityPlanner(ROOT / "tracking" / "activity_history.csv", settings=settings)
    activity = planner.plan(plan, synced_md)
    if activity.activity_type != "STORY_SEQUENCE":
        # Force sequence via map for 021 educational arc.
        from krishna_story_factory.activities.story_map import reconstruct_story_map_from_canonical
        from krishna_story_factory.activities.models import ActivityPack, ActivityPage
        from krishna_story_factory.activities.planner import _shuffled_sequence_cards

        sm = reconstruct_story_map_from_canonical(
            story_no=CHAPTER, title=plan.title, story_md=synced_md, age_band=plan.age_range or "6-12"
        )
        cards = [
            SequenceCard(event=e, drawing_prompt=f"Draw one detail from: {e}", source_order=i + 1)
            for i, e in enumerate(sm.sequence_events())
        ]
        printed = _shuffled_sequence_cards(cards, plan.summary_seed or plan.title)
        activity = ActivityPack(
            activity_title=f"Put {plan.title} in Order",
            activity_type="STORY_SEQUENCE",
            send_mode="SEND_NOW",
            estimated_minutes=15,
            parent_effort="Low",
            learning_goal="Retell the pastime in correct order.",
            story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
            materials=["pencil", "crayons"],
            pages=[
                ActivityPage(
                    page_title="Story sequence cards",
                    page_type="STORY_SEQUENCE_CARDS",
                    instructions=["Number the cards in story order.", "Draw one source-faithful detail on each card."],
                    components=printed,
                    story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
                ),
                ActivityPage(
                    page_title="Family kindness mission",
                    page_type="FAMILY_MISSION",
                    instructions=["Choose one kind action from the story and do it today."],
                    components=["family mission card", "completion checkbox"],
                    story_connection=f"Every printable piece comes from the central scene of {plan.title}.",
                ),
            ],
            answer_key=[c.event for c in sorted(cards, key=lambda x: x.source_order)],
        )

    seq_events = [
        item.event
        for page in activity.pages
        if page.page_type == "STORY_SEQUENCE_CARDS"
        for item in page.components
        if isinstance(item, SequenceCard)
    ]
    semantic = evaluate_activity_semantic_qa(
        activity_type=activity.activity_type,
        events=seq_events,
        parent_answer_events=list(activity.answer_key or []),
        required_tokens=["Brahmā", "Kṛṣṇa"],
        canonical_story=audio_script,
    )
    write_activity_semantic_qa(semantic, work / "activity_semantic_qa.json")
    write_activity_semantic_qa(semantic, evidence / "021_activity_semantic_qa.json")
    if semantic.result != "PASS":
        raise SystemExit(f"Activity semantic FAIL: {semantic.failure_reasons}")

    gen = ActivitySheetGenerator()
    gen.generate(plan, activity, paths.activity_sheet)
    render_dir = work / "activity_pages"
    pdf_check = validate_activity_pdf(paths.activity_sheet, render_dir, activity=activity)
    layout = {
        "page_count": pdf_check.page_count,
        "errors": list(pdf_check.errors),
        "coverage": list(pdf_check.coverage),
        "matching_meta": pdf_check.matching_coverage,
        "render_dir": str(render_dir),
        "result": "PASS" if not pdf_check.errors else "FAIL",
    }
    (work / "activity_layout_qa.json").write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    (evidence / "021_activity_layout_qa.json").write_text(json.dumps(layout, indent=2) + "\n", encoding="utf-8")
    if pdf_check.errors:
        raise SystemExit("Activity layout/PDF FAIL: " + " | ".join(pdf_check.errors))
    if render_dir.exists():
        dest_pages = evidence / "021_activity_renders"
        if dest_pages.exists():
            shutil.rmtree(dest_pages)
        shutil.copytree(render_dir, dest_pages)

    parent_key = build_parent_answer_key(activity)
    key_errors = validate_parent_answer_key(activity, parent_key)
    if key_errors:
        raise SystemExit("Parent answer key FAIL: " + " | ".join(key_errors))

    # Manifest update
    manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
    manifest["generated_at"] = datetime.now(ZoneInfo(settings.app_timezone)).isoformat(timespec="seconds")
    metrics = dict(manifest.get("metrics") or {})
    metrics["audio_duration_seconds"] = round(duration, 1)
    metrics["audio_bytes"] = paths.narration_mp3.stat().st_size
    metrics["audio_script_words"] = len(audio_script.split())
    metrics["peak"] = wave.peak
    metrics["clipping_ratio"] = wave.clipping_ratio
    metrics["longest_silence_seconds"] = wave.longest_silence_seconds
    metrics["waveform_validation_status"] = wave.status
    metrics["measured_wpm"] = pace.measured_wpm
    manifest["metrics"] = metrics
    manifest["audio"] = {
        "provider": (audio.last_provider if audio else None) or source or "openai",
        "model_id": (audio.last_model_id if audio else None) or "gpt-4o-mini-tts-2025-12-15",
        "voice": (audio.last_voice_name if audio else None) or "marin",
        "speed": float(getattr(settings, "openai_tts_speed", 0.90) or 0.90),
        "response_format": getattr(settings, "openai_tts_response_format", "mp3") or "mp3",
        "generation_verified": True,
        "sha256": _sha(paths.narration_mp3),
        "bytes": paths.narration_mp3.stat().st_size,
        "duration_seconds": round(duration, 1),
        "measured_wpm": pace.measured_wpm,
        "waveform_validation_status": wave.status,
        "audio_stale": False,
        "narration_source_sha": narration_source_sha(audio_script),
        "human_listening_status": "HUMAN_REVIEW_PENDING",
        "repair_note": "Gate repair 2026-08-03: canonical Main Story TTS + semantic activity.",
        "sample_retry_count": sample_retry,
    }
    manifest["activity"] = {
        "type": activity.activity_type,
        "title": activity.activity_title,
        "recommended_send_mode": activity.send_mode,
        "estimated_minutes": activity.estimated_minutes,
        "parent_effort": activity.parent_effort,
        "page_count": pdf_check.page_count,
        "qa_score": manifest.get("activity", {}).get("qa_score", 0),
        "answer_key": list(activity.answer_key or []),
        "matching_coverage": pdf_check.matching_coverage,
        "parent_answer_key": parent_key.to_dict() if hasattr(parent_key, "to_dict") else parent_key,
        "semantic_qa": semantic.result,
        "layout_qa": layout["result"],
    }
    paths.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    after_locked = {name: _sha(paths.root / name) for name in LOCKED_HASH_FILES}
    if after_locked != before_locked:
        raise SystemExit(f"LOCKED HASH DRIFT: before={before_locked} after={after_locked}")

    checksums = {
        "before_locked": before_locked,
        "after_locked": after_locked,
        "story_md": _sha(paths.story_md),
        "narration.mp3": _sha(paths.narration_mp3),
        "activity_sheet.pdf": _sha(paths.activity_sheet),
        "manifest.json": _sha(paths.manifest),
        "main_story_unchanged": True,
        "events": seq_events,
        "duration": duration,
        "wpm": pace.measured_wpm,
    }
    (evidence / "021_after_checksums.json").write_text(json.dumps(checksums, indent=2) + "\n", encoding="utf-8")

    if "--upload-drive" in sys.argv:
        result = replace_existing_files(
            settings,
            source_dir=paths.root,
            manifest_path=paths.manifest,
            filenames=("story.md", "narration.mp3", "activity_sheet.pdf", "manifest.json"),
        )
        print(f"Drive: {result.status} {result.detail}")
        if result.status not in {"UPLOADED", "REPLACED", "OK", "SUCCESS"} and "UPLOADED" not in result.status:
            raise SystemExit(f"Drive repair failed: {result.status} {result.detail}")
        (evidence / "021_drive_readback.json").write_text(
            json.dumps(
                {
                    "status": result.status,
                    "detail": result.detail,
                    "folder_id": result.folder_id,
                    "uploaded_files": list(result.uploaded_files or ()),
                    "remote_files": [dict(x) if isinstance(x, dict) else str(x) for x in (result.remote_files or ())],
                },
                indent=2,
                default=str,
            )
            + "\n",
            encoding="utf-8",
        )

    print(json.dumps({"status": "SUCCESS", **checksums}, indent=2, default=str)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
