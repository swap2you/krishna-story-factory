"""Unit tests for Renee voice lock and pronunciation normalization."""
from __future__ import annotations

from pathlib import Path

import pytest

from krishna_story_factory.audio.pronunciation import (
    LOCKED_MODEL_ID,
    LOCKED_OUTPUT_FORMAT,
    LOCKED_VOICE_ID,
    LOCKED_VOICE_NAME,
    load_pronunciation_aliases,
    normalize_for_tts,
    validate_locked_voice,
)
from krishna_story_factory.audio.sanitize import sanitize_audio_script
from krishna_story_factory.audio.tts import AudioGenerator
from krishna_story_factory.outputs import FINAL_OUTPUT_FILES


ROOT = Path(__file__).resolve().parents[1]


def test_locked_voice_constants() -> None:
    assert LOCKED_VOICE_ID == "Itr6exdQTrvjpW1lNztS"
    assert "Renee" in LOCKED_VOICE_NAME
    assert LOCKED_MODEL_ID == "eleven_v3"
    assert LOCKED_OUTPUT_FORMAT == "mp3_44100_128"


def test_validate_locked_voice_rejects_mismatch() -> None:
    errors = validate_locked_voice(voice_id="wrong", voice_name="Other", model_id="eleven_multilingual_v2")
    assert errors
    assert not validate_locked_voice(
        voice_id=LOCKED_VOICE_ID,
        voice_name=LOCKED_VOICE_NAME,
        model_id=LOCKED_MODEL_ID,
    )


def test_pronunciation_dictionary_loads_required_names() -> None:
    aliases = load_pronunciation_aliases(ROOT)
    required = {
        "Hare Kṛṣṇa",
        "Kṛṣṇa",
        "Devakī",
        "Vasudeva",
        "Kaṁsa",
        "Nārada",
        "Brahmā",
        "Śiva",
        "Mathurā",
    }
    for key in required:
        assert key in aliases, f"missing alias for {key}"


def test_normalize_for_tts_keeps_display_friendly_audio_tokens() -> None:
    display = "Hare Kṛṣṇa! Devakī and Vasudeva met Kaṁsa in Mathurā with Nārada, Brahmā, and Śiva."
    result = normalize_for_tts(display, project_root=ROOT)
    assert result.display_text == display
    audio = result.audio_text
    assert "Krishna" in audio
    assert "Devaki" in audio
    assert "Kamsa" in audio
    assert "Mathura" in audio
    assert "Narada" in audio
    assert "Brahma" in audio
    assert "Shiva" in audio
    assert "Kṛṣṇa" not in audio
    assert "Devakī" not in audio
    assert result.aliases_applied


def test_no_pause_tag_survives_sanitize() -> None:
    cleaned = sanitize_audio_script("Calm night. [pause] Soft prayer.", model_id="eleven_v3")
    assert "[pause]" not in cleaned.lower()
    assert "pause" not in cleaned.lower()


def test_eleven_v3_voice_settings_omit_speed(monkeypatch, tmp_path: Path) -> None:
    from krishna_story_factory.config import load_settings

    settings = load_settings(ROOT)
    gen = AudioGenerator(settings, mode="test")
    voice = gen._voice_settings("eleven_v3")
    assert "speed" not in voice


def test_eight_file_package_contract() -> None:
    assert "simple_coloring_page.png" in FINAL_OUTPUT_FILES
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


def test_placeholder_lessons_rejected() -> None:
    from krishna_story_factory.content.story_format_v2 import StoryPackageContentV2, validate_story_format_v2

    package = StoryPackageContentV2(
        greeting="Hare Kṛṣṇa!",
        series_name="Krishna Book Bedtime",
        story_number="005",
        title="Test",
        source_reference="KB 2",
        scripture_reference="SB 10.2",
        recap=" ".join(["word"] * 90),
        main_story=" ".join(["word"] * 800),
        devotional_meaning=" ".join(["word"] * 120),
        five_lessons=[
            "Lord Krishna protects devotees with love and care always.",
            "Prayer brings courage when nights feel hard.",
            "Remember the Lord with love in this pastime (3).",
            "Serve gently with family and friends each day.",
            "Practice trust by chanting Hare Krishna together.",
        ],
        think_about_it=["Why do we pray?", "How can we trust?", "What helps courage?"],
        five_star_challenge=[
            "Draw Devaki with soft glow",
            "Say one prayer tonight",
            "Name Brahma and Shiva",
            "Thank parents kindly",
            "Chant Hare Krishna slowly",
        ],
        bedtime_prayer=" ".join(["Hare", "Kṛṣṇa"] + ["word"] * 90),
        next_story_preview=" ".join(["word"] * 40) + " birth",
        parent_note=" ".join(["word"] * 80),
        audio_narration="Story 005. " + " ".join(["word"] * 700) + " Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare. birth",
        age_range="6-12",
    )
    errors = validate_story_format_v2(package, next_title="The Birth of Lord Krishna")
    assert any("placeholder" in e.lower() or "incomplete" in e.lower() for e in errors)


def test_story_005_source_boundary_rejects_drowsy_guards() -> None:
    from krishna_story_factory.generation.source_guard import run_source_guard
    from krishna_story_factory.models import PlanRow, StoryContent

    plan = PlanRow(
        chapter_no="005",
        slug="prayers",
        title="Prayers",
        project="krishna_book_bedtime",
        library_id="krishna_book",
        source_reference="Krishna Book Chapter 2",
        scripture_reference="SB 10.2.25–42",
        summary_seed="demigods pray",
        age_range="6-12",
        package_type="bedtime_story",
        send_date="",
        status="pending",
        must_include="Devaki|womb|Brahma|Shiva|Narada",
        must_avoid="drowsy guards|Yogamaya|Yamuna",
    )
    content = StoryContent(
        title="Prayers",
        recap="Narada warned Kamsa earlier.",
        main_story="Guards, unaware, paced the hallway and soon became heavy-eyed.",
        moral="trust",
        takeaway="pray",
        five_star_challenge=["1", "2", "3", "4", "5"],
        audio_script="Guards, unaware, paced the hallway and soon became heavy-eyed.",
        five_lessons=["a"] * 5,
        think_about_it=["Why pray?"],
    )
    errors = run_source_guard(plan, content)
    assert any("leakage" in e or "heavy-eyed" in e or "guards" in e for e in errors)


def test_parse_rebuild_range_rejects_006() -> None:
    from krishna_story_factory.pipeline import PipelineError, parse_rebuild_range, rebuild_story_range
    from krishna_story_factory.config import load_settings

    start, end = parse_rebuild_range("001:005")
    assert start == "001" and end == "005"
    settings = load_settings(ROOT)
    with pytest.raises(PipelineError):
        rebuild_story_range(settings, range_spec="001:006", archive=False, replace_drive=False)
