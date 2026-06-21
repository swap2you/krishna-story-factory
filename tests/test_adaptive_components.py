from __future__ import annotations

import csv
from pathlib import Path

import pytest

from krishna_story_factory.activities.planner import ALLOWED_ACTIVITY_TYPES, ActivityPlanner
from krishna_story_factory.images.generator import _identity_constraints
from krishna_story_factory.models import PlanRow
from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf


def row(chapter="003", title="A Krishna Book Story"):
    return PlanRow(chapter, "story", title, "p", "l", "Krishna Book", "SB 10", "seed", "6-13", "daily", "", "done")


def write_history(path: Path, types: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("chapter_no", "slug", "activity_type", "activity_title", "recommended_send_mode", "generated_at"))
        writer.writeheader()
        for idx, kind in enumerate(types):
            writer.writerow({"chapter_no": str(idx), "slug": "s", "activity_type": kind, "activity_title": "t", "recommended_send_mode": "SEND_NOW", "generated_at": "now"})


def test_planner_returns_one_valid_primary_activity(tmp_path):
    plan = ActivityPlanner(tmp_path / "history.csv").plan(row(), "story")
    assert plan.activity_type in ALLOWED_ACTIVITY_TYPES
    assert isinstance(plan.activity_type, str)


def test_history_prevents_immediate_repetition(tmp_path):
    history = tmp_path / "history.csv"; write_history(history, ["STORY_SEQUENCE"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type != "STORY_SEQUENCE"


def test_word_search_not_repeated_within_five(tmp_path):
    history = tmp_path / "history.csv"; write_history(history, ["MINI_DRAMA", "WORD_SEARCH", "FAMILY_MISSION"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type != "WORD_SEARCH"


def test_heavy_crafts_are_not_consecutive(tmp_path):
    history = tmp_path / "history.csv"; write_history(history, ["CUT_AND_BUILD"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type not in {"PAPER_CRAFT", "CUT_AND_BUILD", "PRAYER_OR_GRATITUDE_CRAFT"}


@pytest.mark.parametrize("chapter,title,expected,pages", [
    ("001", "The Earth Prays for Krishna to Come", "PRAYER_OR_GRATITUDE_CRAFT", 1),
    ("002", "The Wedding and the Heavenly Voice", "CUT_AND_BUILD", 2),
])
def test_story_specific_activity_pdf(tmp_path, chapter, title, expected, pages):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row(chapter, title), "story")
    output = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(row(chapter, title), activity, output)
    check = validate_activity_pdf(output)
    assert activity.activity_type == expected
    assert check.page_count == pages
    assert not check.errors
    assert all(value >= .35 for value in check.coverage)


def test_activity_pdf_does_not_embed_coloring_page(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("001", "The Earth Prays for Krishna to Come"), "story")
    output = tmp_path / "activity_sheet.pdf"; ActivitySheetGenerator().generate(row("001", "The Earth Prays for Krishna to Come"), activity, output)
    assert b"coloring_page.png" not in output.read_bytes()


def test_cut_build_has_parts_sequence_and_safety(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("002", "The Wedding and the Heavenly Voice"), "story")
    assert len(activity.printable_components) >= 8
    assert len(activity.answer_key) >= 4
    assert "scissor" in activity.safety_note.lower()


def test_story_002_identifies_adult_kamsa_as_charioteer():
    prompt = _identity_constraints("The Wedding and the Heavenly Voice")
    assert "adult" in prompt.lower()
    assert "Kamsa" in prompt and "driving" in prompt
    assert "No peacock feathers" in prompt


def test_non_krishna_feather_rule_is_universal():
    prompt = _identity_constraints("Any story")
    assert "Only Krishna may wear a peacock feather" in prompt


def test_story_001_plan_has_six_petals(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("001", "The Earth Prays for Krishna to Come"), "story")
    assert activity.activity_title == "Prayer Petal Wheel"
    assert "six" in " ".join(activity.printable_components).lower()


def test_activity_metadata_is_strict_internal_json_shape(tmp_path):
    data = ActivityPlanner(tmp_path / "history.csv").plan(row(), "story").to_dict()
    assert set(data) == {"activity_title", "activity_type", "learning_goal", "story_connection", "recommended_send_mode", "estimated_minutes", "parent_effort", "age_variants", "materials", "instructions", "review_questions", "printable_components", "safety_note", "completion_prompt"}
