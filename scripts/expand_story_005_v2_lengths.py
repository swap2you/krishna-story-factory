"""Expand short Story 005 Format V2 sections and re-upload story/audio/manifest."""
from __future__ import annotations

import json
import re
from pathlib import Path

from mutagen.mp3 import MP3

from krishna_story_factory.audio.tts import AudioGenerator
from krishna_story_factory.audio.waveform import validate_mp3_waveform
from krishna_story_factory.config import load_settings
from krishna_story_factory.content.story_format_v2 import (
    HARE_KRISHNA_MANTRA,
    build_audio_narration,
    build_greeting,
    extract_section,
    package_from_llm_dict,
    validate_story_format_v2,
)
from krishna_story_factory.csv_store import read_plan_by_chapter
from krishna_story_factory.models import story_content_from_v2, word_count
from krishna_story_factory.paths import make_package_paths
from krishna_story_factory.storage.google_drive_uploader import replace_existing_files, verify_drive_text_links

ROOT = Path(__file__).resolve().parents[1]
FOLDER_ID = "1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3"


def set_section(md: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\n<!--|\Z)", re.S)
    return pattern.sub(lambda match: match.group(1) + body.strip() + "\n\n", md, count=1)


def main() -> int:
    settings = load_settings(ROOT)
    plan = read_plan_by_chapter(ROOT, "005")
    paths = make_package_paths(settings.output_root, plan)
    md = paths.story_md.read_text(encoding="utf-8")

    meaning = extract_section(md, "Devotional Meaning")
    if word_count(meaning) < 100:
        meaning += (
            " This pastime teaches that Krishna's protection can first strengthen the heart with courage, "
            "even before outer danger fully changes. Children can practice the same trust by praying softly, "
            "speaking kindly, and remembering the Lord with family."
        )
    prayer = (
        "Dear Krishna, thank You for tonight's secret prayer gathering with Brahma, Shiva, Narada, and the demigods. "
        "Please protect Devaki's courage in our hearts and keep our family close to You. "
        "Help us offer sincere prayers, serve with kindness, speak truthfully, and rest without fear. "
        f"We chant: {HARE_KRISHNA_MANTRA}. "
        "Good night, dear Krishna. Please watch over us gently as we sleep peacefully in Your loving care."
    )
    preview = (
        "Next time: Story 006 — The Birth of Lord Krishna. "
        "On a sacred night filled with wonder and quiet faith, the Supreme Lord appears. "
        "We will listen with calm hearts, joyful devotion, and grateful surprise together."
    )
    md = set_section(md, "Devotional Meaning", meaning)
    md = set_section(md, "Bedtime Prayer", prayer)
    md = set_section(md, "Next Story Preview", preview)

    lessons = [re.sub(r"^\d+\.\s*", "", line).strip() for line in extract_section(md, "Five Lessons").splitlines() if line.strip()]
    think = [re.sub(r"^\d+\.\s*", "", line).strip() for line in extract_section(md, "Think About It").splitlines() if line.strip()]
    challenge = [re.sub(r"^\d+\.\s*", "", line).strip() for line in extract_section(md, "Five-Star Challenge").splitlines() if line.strip()]
    body = md.split("---", 2)[-1].strip().splitlines()
    greeting = next((line for line in body if line.strip() and not line.startswith("#")), build_greeting(settings.story_greeting_names))
    package = package_from_llm_dict(
        {
            "greeting": greeting,
            "story_number": "005",
            "title": plan.title,
            "recap": extract_section(md, "Recap"),
            "main_story": extract_section(md, "Main Story"),
            "devotional_meaning": extract_section(md, "Devotional Meaning"),
            "five_lessons": lessons,
            "think_about_it": think,
            "five_star_challenge": challenge,
            "bedtime_prayer": extract_section(md, "Bedtime Prayer"),
            "next_story_preview": extract_section(md, "Next Story Preview"),
            "parent_note": extract_section(md, "Parent/Teacher Note"),
            "poster_visual_brief": extract_section(md, "Poster Visual Brief") or "poster",
            "coloring_visual_brief": extract_section(md, "Coloring Visual Brief") or "coloring",
        },
        plan=plan,
        greeting=greeting,
    )
    package.audio_narration = build_audio_narration(package)
    words = package.audio_narration.split()
    if len(words) > 700:
        package.audio_narration = " ".join(words[:700])
    elif len(words) < 650:
        package.audio_narration += " Remember tonight with a calm heart and thank Krishna before sleep."
    md = re.sub(
        r"(## Audio Narration\n)(.*?)(?=\n## |\n-->)",
        lambda match: match.group(1) + package.audio_narration.strip() + "\n\n",
        md,
        count=1,
        flags=re.S,
    )
    paths.story_md.write_text(md, encoding="utf-8")
    content = story_content_from_v2(package)
    AudioGenerator(settings, "prod").generate_mp3(content.audio_script, paths.narration_mp3)
    duration = float(MP3(paths.narration_mp3).info.length)
    wave = validate_mp3_waveform(paths.narration_mp3, expected_duration=duration)
    if wave.status != "PASS":
        raise SystemExit(wave.detail)
    errors = validate_story_format_v2(package, next_title="The Birth of Lord Krishna")
    data = json.loads(paths.manifest.read_text(encoding="utf-8"))
    data["metrics"]["main_story_words"] = word_count(extract_section(md, "Main Story"))
    data["metrics"]["audio_script_words"] = word_count(package.audio_narration)
    data["metrics"]["audio_duration_seconds"] = round(duration, 1)
    paths.manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    package_link = f"https://drive.google.com/drive/folders/{FOLDER_ID}?usp=sharing"
    upload = replace_existing_files(
        settings,
        source_dir=paths.root,
        manifest_path=paths.manifest,
        filenames=("story.md", "narration.mp3", "manifest.json"),
    )
    if upload.status != "UPLOADED":
        raise SystemExit(upload.detail)
    ok, detail = verify_drive_text_links(settings, folder_id=FOLDER_ID, package_link=package_link)
    print(
        {
            "fmt_errors": errors,
            "meaning": word_count(extract_section(md, "Devotional Meaning")),
            "prayer": word_count(extract_section(md, "Bedtime Prayer")),
            "preview": word_count(extract_section(md, "Next Story Preview")),
            "audio_s": round(duration, 1),
            "drive": upload.detail,
            "verify": detail if ok else f"FAIL {detail}",
        }
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
