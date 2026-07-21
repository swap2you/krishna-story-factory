"""Final repair reliability: audio fallback, activity metadata, rebuild safety."""
from __future__ import annotations

import inspect
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from krishna_story_factory.activities.planner import ActivityPlanner, _extract_event_labels, _pack_006
from krishna_story_factory.activities.qa import is_metadata_event_label, semantic_activity_errors
from krishna_story_factory.audio.assemble import _atomic_replace
from krishna_story_factory.audio.openai_tts import _retry_after_seconds
from krishna_story_factory.audio.provider import (
    elevenlabs_available_characters,
    invalidate_elevenlabs_cache,
    preflight_elevenlabs,
    reset_provider_preflight_cache,
    select_audio_provider,
)
from krishna_story_factory.audio.pronunciation import normalize_for_tts
from krishna_story_factory.audio.redact import sanitize_error_text
from krishna_story_factory.audio.sanitize import sanitize_audio_script
from krishna_story_factory.audio.tts import AudioGenerationError, AudioGenerator
from krishna_story_factory.content.repairs import (
    repair_story_002_dialogue,
    repair_story_005_philosophy,
    repair_story_006_content,
)
from krishna_story_factory.generation.source_guard import run_source_guard
from krishna_story_factory.models import PlanRow, StoryContent
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES
from krishna_story_factory.paths import assert_path_under_root


ROOT = Path(__file__).resolve().parents[1]


def _plan(chapter: str, **kwargs) -> PlanRow:
    defaults = dict(
        chapter_no=chapter,
        slug=f"story-{chapter}",
        title=f"Story {chapter}",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book",
        scripture_reference="SB",
        summary_seed="seed",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="done",
        created_at="",
        updated_at="",
        notes="",
        row_index=0,
        must_include="",
        must_avoid="forbidden later event",
        start_boundary="",
        end_boundary="",
    )
    defaults.update(kwargs)
    return PlanRow(**defaults)


def _content(**kwargs) -> StoryContent:
    base = dict(
        title="t",
        greeting="Hare Krishna",
        recap="r",
        main_story="m",
        moral="mo",
        takeaway="ta",
        five_star_challenge=["a"],
        audio_script="audio",
        bedtime_reflection="What will you remember?",
        think_about_it=["What will you remember?"],
        five_lessons=["l1", "l2", "l3", "l4", "l5"],
        devotional_meaning="meaning",
    )
    base.update(kwargs)
    return StoryContent(**base)


def test_exact_eight_files_contract() -> None:
    assert len(FINAL_OUTPUT_FILES) == 8
    assert FINAL_OUTPUT_FILES == (
        "story.md",
        "narration.mp3",
        "story_poster.png",
        "coloring_page.png",
        "simple_coloring_page.png",
        "activity_sheet.pdf",
        "whatsapp_caption.txt",
        "manifest.json",
    )


def test_story_007_remains_pending_on_live_queue() -> None:
    from krishna_story_factory.csv_store import ensure_csv_files, read_next_pending, read_plan_by_chapter

    ensure_csv_files(ROOT)
    pending = read_next_pending(ROOT)
    assert pending is not None
    assert pending.chapter_no == "007"
    for chapter in ("001", "002", "003", "004", "005", "006"):
        plan = read_plan_by_chapter(ROOT, chapter)
        assert plan is not None
        assert plan.status == "done"


def test_alias_word_boundaries_do_not_rewrite_drama(tmp_path: Path) -> None:
    yaml_path = tmp_path / "input" / "audio_pronunciations.yaml"
    yaml_path.parent.mkdir(parents=True)
    yaml_path.write_text('aliases:\n  "Rama": "RAA-muh"\n', encoding="utf-8")
    result = normalize_for_tts("A quiet drama about Rama.", project_root=tmp_path)
    assert "drama" in result.audio_text.lower()
    assert "RAA-muh" in result.audio_text


def test_secret_redaction() -> None:
    cleaned = sanitize_error_text("fail sk-proj-ABCDEFGHIJKLMNOPQRSTUV key=xi-ABCDEFGHIJKLMN")
    assert "sk-proj-" not in cleaned
    assert "xi-ABCDEF" not in cleaned
    assert "[REDACTED]" in cleaned


def test_path_traversal_rejected(tmp_path: Path) -> None:
    root = tmp_path / "approved"
    root.mkdir()
    with pytest.raises(ValueError):
        assert_path_under_root(tmp_path / "outside" / "x", root, label="bad")


def test_windows_atomic_replace_retries(tmp_path: Path) -> None:
    src = tmp_path / "a.partial"
    dest = tmp_path / "a.mp3"
    src.write_bytes(b"ok")
    dest.write_bytes(b"old")
    calls = {"n": 0}
    original = Path.replace

    def flaky(self, target):  # noqa: ANN001
        calls["n"] += 1
        if calls["n"] < 3:
            raise OSError(32, "locked")
        return original(self, target)

    with patch.object(Path, "replace", flaky):
        _atomic_replace(src, dest, attempts=5)
    assert dest.read_bytes() == b"ok"
    assert calls["n"] == 3


def test_http_date_retry_after() -> None:
    from datetime import datetime, timedelta, timezone

    when = datetime.now(timezone.utc) + timedelta(seconds=3)
    header = when.strftime("%a, %d %b %Y %H:%M:%S GMT")

    class Exc(Exception):
        response = MagicMock(headers={"Retry-After": header})

    delay = _retry_after_seconds(Exc("rate"), 0)
    assert 0.5 <= delay <= 60.0


def test_openai_strips_all_unsupported_tags() -> None:
    cleaned = sanitize_audio_script(
        'Softly [softly] speak <break time="1.0s" /> now [pause]',
        model_id="openai",
    )
    assert "<break" not in cleaned.lower()
    assert "[softly]" not in cleaned.lower()
    assert "[pause]" not in cleaned.lower()


def test_cache_reset_and_elevenlabs_invalidate() -> None:
    reset_provider_preflight_cache()
    invalidate_elevenlabs_cache(reason="quota")
    # After invalidate with empty prior cache, detail is stored as failed.
    from krishna_story_factory.audio import provider as provider_mod

    assert provider_mod._CACHE.elevenlabs is not None
    assert provider_mod._CACHE.elevenlabs.get("ok") is False
    reset_provider_preflight_cache()
    assert provider_mod._CACHE.elevenlabs is None


def test_malformed_elevenlabs_subscription_does_not_crash() -> None:
    class Resp:
        status_code = 200

        def json(self):
            raise ValueError("nope")

    with patch("krishna_story_factory.audio.provider.requests.get", return_value=Resp()):
        available, detail = elevenlabs_available_characters("fake-key")
    assert available == 0
    assert detail["error"] == "subscription_malformed_json"


def test_elevenlabs_timeout_falls_back_in_preflight(monkeypatch) -> None:
    import requests
    from dataclasses import replace

    from krishna_story_factory.config import load_settings

    settings = replace(load_settings(ROOT), openai_tts_enabled=True, openai_api_key="sk-test")
    reset_provider_preflight_cache()

    def boom(*_a, **_k):
        raise requests.Timeout("timed out")

    monkeypatch.setattr("krishna_story_factory.audio.provider.requests.get", boom)
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.preflight_openai_tts",
        lambda **kwargs: {"ok": True, "provider": "openai", "model_id": "gpt-4o-mini-tts-2025-12-15", "voice": "marin"},
    )
    decision = select_audio_provider(settings, estimated_chars=100, require_dictionary=False)
    assert decision.status == "READY"
    assert decision.provider == "openai"


def test_synthesis_time_elevenlabs_fallback_to_openai(tmp_path: Path, monkeypatch) -> None:
    from krishna_story_factory.config import load_settings

    settings = load_settings(ROOT)
    gen = AudioGenerator(settings, mode="prod")
    decision = MagicMock(status="READY", provider="elevenlabs", model_id="eleven_v3")
    out = tmp_path / "narration.mp3"
    out.write_bytes(b"partial")

    def fail_el(*_a, **_k):
        raise AudioGenerationError("ElevenLabs TTS failed: 429 insufficient quota")

    calls = {"openai": 0}

    def fake_openai(self, text, output_path, **kwargs):
        calls["openai"] += 1
        Path(output_path).write_bytes(b"1234567890" * 20)
        self.last_provider = "openai"
        self.last_model_id = kwargs.get("model") or "gpt-4o-mini-tts-2025-12-15"
        return "openai"

    monkeypatch.setattr(AudioGenerator, "_synthesize_elevenlabs", fail_el)
    monkeypatch.setattr(AudioGenerator, "_synthesize_openai", fake_openai)
    monkeypatch.setattr(
        "krishna_story_factory.audio.provider.preflight_openai",
        lambda _s: {"ok": True, "model_id": "gpt-4o-mini-tts-2025-12-15", "voice": "marin"},
    )
    provider = gen.generate_mp3("Hare Krishna soft bedtime story.", out, provider_decision=decision)
    assert provider == "openai"
    assert calls["openai"] == 1
    assert gen.last_provider == "openai"
    assert out.exists() and out.stat().st_size > 50


def test_source_guard_checks_audio_script() -> None:
    plan = _plan("099", must_avoid="forbidden later event")
    content = _content(main_story="safe story", audio_script="mentions forbidden later event here")
    errors = run_source_guard(plan, content)
    assert any("forbidden later event" in e for e in errors)


def test_metadata_event_labels_rejected() -> None:
    assert is_metadata_event_label("title: The Birth")
    assert is_metadata_event_label("source_reference: Krishna Book")
    assert is_metadata_event_label("Hare Kṛṣṇa, dear children")
    assert is_metadata_event_label("---")
    assert not is_metadata_event_label("Krishna appeared in His four-armed form.")


def test_extract_event_labels_ignores_frontmatter() -> None:
    story = """---
title: "The Birth of Lord Krishna"
source_reference: "Krishna Book Chapter 3"
---

Hare Kṛṣṇa, dear children and families!

# Main Story
Auspicious signs appeared as the sacred night approached. Krishna appeared before Devaki and Vasudeva in His four-armed form. Devaki and Vasudeva offered prayers. Krishna assumed the form of an ordinary infant. Vasudeva's chains loosened and the prison doors opened. Vasudeva prepared to carry Krishna according to the Lord's arrangement.
"""
    labels = _extract_event_labels(story, "birth")
    joined = " ".join(labels).lower()
    assert "title:" not in joined
    assert "source_reference" not in joined
    assert "hare kṛṣṇa, dear" not in joined
    assert any("four-armed" in label.lower() or "four armed" in label.lower() for label in labels)


def test_story_006_sequence_uses_real_events() -> None:
    pack = _pack_006(_plan("006", title="The Birth of Lord Krishna"))
    errors = semantic_activity_errors(pack)
    assert not errors
    events = []
    for page in pack.pages:
        if page.page_type == "STORY_SEQUENCE_CARDS":
            events = [c.event for c in page.components]
    assert len(events) == 6
    assert all(not is_metadata_event_label(event) for event in events)
    assert any("four-armed" in event.lower() for event in events)


def test_story_006_no_duplicated_lesson() -> None:
    meaning = "Long meaning paragraph about hope and wonder that should not be copied."
    content = repair_story_006_content(
        _content(
            recap="They gathered in celestial gardens to offer their prayers.",
            main_story='Vasudeva softly spoke, "O Supreme Lord, You have kindly appeared before us."',
            audio_script="gathered in celestial gardens to offer their prayers",
            devotional_meaning=meaning,
            five_lessons=[meaning, "2", "3", "4", "5"],
        )
    )
    assert content.five_lessons[0] != meaning
    assert len(content.five_lessons) == 5
    assert "celestial gardens" not in content.recap.lower()
    assert "Vasudeva softly spoke," not in content.main_story


def test_story_002_repaired_dialogue() -> None:
    content = repair_story_002_dialogue(
        _content(
            main_story=(
                'Devaki squeezed Vasudeva\'s hand. "Thank you for saving my life," she whispered, her voice trembling but grateful. '
                'Vasudeva comforted her, whispering, "We must trust in Krishna\'s plan, even when it is hard to see."'
            ),
            audio_script='"Thank you for saving my life,"',
        )
    )
    assert "Thank you for saving my life" not in content.main_story
    assert "In paraphrase" in content.main_story


def test_story_005_repaired_philosophy() -> None:
    content = repair_story_005_philosophy(
        _content(
            main_story=(
                "Far above the earth, in the sweet-smelling gardens of the heavenly planets, a meeting was called by Lord Brahmā, the creator, and Lord Śiva, the great protector. "
                "Even Indra, king of rain, came, as well as Candra, the Moon-god, and Varuṇa, ruler of the cosmic waters. "
                "One by one, the demigods began to glorify Lord Krishna. 'You are the supreme protector,' they prayed silently. "
                "'Though You are everywhere, You now stay within the womb to delight Your dear devotees and destroy all fear.'"
            ),
            audio_script="shield for her and for the Lord",
            devotional_meaning="The loving prayers of the demigods become a shield for her and for the Lord, teaching us that sincere devotion can bring protection and peace, no matter our situation.",
        )
    )
    assert "sweet-smelling gardens" not in content.main_story.lower()
    assert "shield for her and for the lord" not in content.devotional_meaning.lower()
    assert "four-headed" in content.main_story.lower() or "Four-headed" in content.main_story


def test_manual_rebuild_script_has_no_force() -> None:
    text = (ROOT / "scripts" / "rebuild_story_packages.py").read_text(encoding="utf-8")
    assert "add_argument(\"--force\"" not in text
    assert "args.force" not in text
    ps1 = (ROOT / "scripts" / "manual_rebuild_story.ps1").read_text(encoding="utf-8")
    assert "Intentionally never append --force" in ps1


def test_drive_upload_opt_in_only() -> None:
    text = (ROOT / "scripts" / "rebuild_story_packages.py").read_text(encoding="utf-8")
    assert "--upload-drive" in text
    assert "upload_drive=bool(args.upload_drive)" in text
    assert "mutually_exclusive_group" in text


def test_waveform_vectorized_longest_silence() -> None:
    source = (ROOT / "krishna_story_factory" / "audio" / "waveform.py").read_text(encoding="utf-8")
    assert "np.diff" in source or "np.where" in source
    assert "for i, sample in enumerate" not in source


def test_changed_docs_no_seven_file_claims() -> None:
    for rel in (
        "docs/01_DAILY_RUNBOOK.md",
        "docs/15_MANUAL_STORY_REBUILD_RUNBOOK.md",
        "scripts/rebuild_story_packages.py",
        "scripts/manual_rebuild_story.ps1",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "seven-file" not in text
        assert "seven file" not in text
        assert "exactly seven" not in text
