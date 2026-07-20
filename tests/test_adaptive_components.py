from __future__ import annotations

import csv
from pathlib import Path

import pytest

from krishna_story_factory.activities.models import ActivityPack, ActivityPage, pack_from_dict
from krishna_story_factory.activities.planner import ALLOWED_ACTIVITY_TYPES, ActivityPlanner
from krishna_story_factory.images.generator import _identity_constraints
from krishna_story_factory.models import PlanRow
from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf
from krishna_story_factory.prompts_loader import load_project_text


def row(chapter="004", title="A Krishna Book Story"):
    return PlanRow(chapter, "story", title, "p", "l", "Krishna Book", "SB 10", "seed about a kind choice", "6-13", "daily", "", "done")


def write_history(path: Path, types: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("chapter_no", "slug", "activity_type", "activity_title", "recommended_send_mode", "generated_at"))
        writer.writeheader()
        for idx, kind in enumerate(types):
            writer.writerow({
                "chapter_no": str(idx), "slug": "s", "activity_type": kind,
                "activity_title": "t", "recommended_send_mode": "SEND_NOW", "generated_at": "now",
            })


def test_activity_pack_json_parsing():
    data = {
        "activity_title": "Path Pack",
        "activity_type": "MAZE_OR_PATH",
        "send_mode": "SEND_NOW",
        "estimated_minutes": 15,
        "parent_effort": "Low",
        "learning_goal": "Follow the path",
        "story_connection": "From the pastime turning point",
        "materials": ["pencil"],
        "pages": [
            {
                "page_title": "Path",
                "page_type": "MAZE_OR_PATH",
                "instructions": ["Trace the path"],
                "components": ["start", "finish"],
                "story_connection": "From the pastime turning point",
            },
            {
                "page_title": "Mission",
                "page_type": "FAMILY_MISSION",
                "instructions": ["Do one kindness"],
                "components": ["mission card"],
                "story_connection": "From the pastime turning point",
            },
        ],
        "answer_key": ["path A"],
        "parent_note": "Low effort",
        "qa_requirements": ["no blank page"],
    }
    pack = pack_from_dict(data)
    pack.validate()
    assert pack.activity_title == "Path Pack"
    assert len(pack.pages) == 2
    assert pack.recommended_send_mode == "SEND_NOW"


def test_activity_prompt_bank_sections_exist(project_root=None):
    root = Path(__file__).resolve().parents[1]
    for name in [
        "00_ACTIVITY_SYSTEM_RULES.md",
        "01_ACTIVITY_PACK_PLANNER.md",
        "02_CRAFT_COMPONENT_GENERATOR.md",
        "03_STORY_SEQUENCE_GENERATOR.md",
        "04_ROLE_PLAY_PUPPET_GENERATOR.md",
        "05_PUZZLE_GENERATOR.md",
        "06_REFLECTION_FAMILY_MISSION_GENERATOR.md",
        "07_ACTIVITY_QA_REVIEW.md",
        "08_ACTIVITY_REPAIR.md",
    ]:
        text = load_project_text(root, f"prompts/activity_bank/{name}")
        assert text, f"Missing activity bank prompt: {name}"


def test_planner_returns_one_valid_primary_activity(tmp_path):
    plan = ActivityPlanner(tmp_path / "history.csv").plan(row(), "story")
    assert plan.activity_type in ALLOWED_ACTIVITY_TYPES
    assert 2 <= len(plan.pages) <= 4


def test_dynamic_planner_returns_multi_page_pack(tmp_path):
    pack = ActivityPlanner(tmp_path / "history.csv").plan(row("010", "Future Pastime"), "A full story about kindness.")
    assert pack.activity_type not in {"COLORING_ONLY", "QUICK_DISCUSSION"} or len(pack.pages) <= 2
    if pack.activity_type not in {"COLORING_ONLY", "QUICK_DISCUSSION"}:
        assert 2 <= len(pack.pages) <= 4
    for page in pack.pages:
        assert page.story_connection.strip()


def test_no_generic_fallback_for_enabled_stories(tmp_path):
    pack = ActivityPlanner(tmp_path / "history.csv").plan(row("020", "A Named Pastime"), "story")
    blob = " ".join(pack.printable_components + [pack.activity_title, pack.story_connection]).lower()
    assert "generic worksheet" not in blob
    assert pack.story_connection
    assert all(p.story_connection for p in pack.pages)


def test_history_prevents_immediate_repetition(tmp_path):
    history = tmp_path / "history.csv"
    write_history(history, ["STORY_SEQUENCE"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type != "STORY_SEQUENCE"


def test_word_search_not_repeated_within_six(tmp_path):
    history = tmp_path / "history.csv"
    write_history(history, ["MINI_DRAMA", "WORD_SEARCH", "FAMILY_MISSION", "MATCHING_GAME", "STORY_MAP"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type != "WORD_SEARCH"


def test_heavy_crafts_not_within_three(tmp_path):
    history = tmp_path / "history.csv"
    write_history(history, ["CUT_AND_BUILD", "STORY_SEQUENCE"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type not in {
        "PAPER_CRAFT", "CUT_AND_BUILD", "PRAYER_OR_GRATITUDE_CRAFT",
    }


def test_written_only_not_within_three(tmp_path):
    history = tmp_path / "history.csv"
    write_history(history, ["DRAW_AND_REFLECT", "MATCHING_GAME"])
    assert ActivityPlanner(history).plan(row(), "story").activity_type not in {
        "DRAW_AND_REFLECT", "QUICK_DISCUSSION", "CROSSWORD", "WORD_SEARCH",
    }


@pytest.mark.parametrize("chapter,title,expected,min_pages,max_pages", [
    ("001", "The Earth Prays for Krishna to Come", "PRAYER_OR_GRATITUDE_CRAFT", 2, 2),
    ("002", "The Wedding and the Heavenly Voice", "CUT_AND_BUILD", 3, 3),
    ("003", "Vasudeva Keeps His Word", "STORY_SEQUENCE", 2, 2),
])
def test_story_specific_activity_pdf(tmp_path, chapter, title, expected, min_pages, max_pages):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row(chapter, title), "story")
    output = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(row(chapter, title), activity, output)
    check = validate_activity_pdf(output, activity=activity)
    assert activity.activity_type == expected
    assert min_pages <= check.page_count <= max_pages
    assert not check.errors
    assert all(value >= 0.35 for value in check.coverage)


def test_activity_pdf_does_not_embed_coloring_page(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("001", "The Earth Prays for Krishna to Come"), "story")
    output = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(row("001", "The Earth Prays for Krishna to Come"), activity, output)
    assert b"coloring_page.png" not in output.read_bytes()


def test_cut_build_has_parts_sequence_and_safety(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("002", "The Wedding and the Heavenly Voice"), "story")
    assert len(activity.printable_components) >= 8
    assert len(activity.answer_key) >= 4
    assert "scissor" in activity.safety_note.lower()


def test_answer_key_not_visible_on_pdf(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("003", "Vasudeva Keeps His Word"), "story")
    output = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(row("003", "Vasudeva Keeps His Word"), activity, output)
    text = output.read_bytes().lower()
    assert b"answer key" not in text


def test_cut_fold_labels_visible_for_crafts(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("002", "The Wedding and the Heavenly Voice"), "story")
    output = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(row("002", "The Wedding and the Heavenly Voice"), activity, output)
    check = validate_activity_pdf(output, activity=activity)
    assert not check.errors
    # Source instructions and PDF renderer both expose cut/fold guidance.
    joined = " ".join(activity.instructions).lower()
    assert "cut" in joined and "fold" in joined
    from krishna_story_factory.pdf import activity_sheet as pdf_mod

    source = Path(pdf_mod.__file__).read_text(encoding="utf-8")
    assert 'c.drawString' in source and '"CUT"' in source and '"FOLD"' in source


def test_story_001_plan_has_prayer_craft_and_support(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("001", "The Earth Prays for Krishna to Come"), "story")
    assert activity.activity_title == "Prayer Petal Wheel"
    assert any(p.page_type == "PRAYER_WHEEL" for p in activity.pages)
    assert any(p.page_type == "MATCHING_CARDS" for p in activity.pages)
    petal_parts = [c for c in activity.printable_components if "petal" in c.lower()]
    assert len(petal_parts) == 6


def test_story_002_plan_has_chariot_and_support(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("002", "The Wedding and the Heavenly Voice"), "story")
    assert activity.activity_title == "Build the Wedding Chariot"
    types = {p.page_type for p in activity.pages}
    assert "CUT_AND_BUILD_PARTS" in types
    assert "STORY_SEQUENCE_CARDS" in types
    assert "ROLE_PLAY_CARDS" in types


def test_story_003_plan_has_truthfulness_path(tmp_path):
    activity = ActivityPlanner(tmp_path / "history.csv").plan(row("003", "Vasudeva Keeps His Word"), "story")
    assert activity.recommended_send_mode == "PARENT_GUIDED"
    assert activity.printable_components == [
        "The first son is born", "Vasudeva remembers his word", "Vasudeva brings the child",
        "Kamsa is astonished", "Kamsa returns the child", "Truthfulness shines",
        "keep the word branch", "break the word branch", "family promise card",
    ]
    assert any(p.page_type == "DECISION_TREE" for p in activity.pages)


def test_activity_metadata_includes_pack_fields(tmp_path):
    data = ActivityPlanner(tmp_path / "history.csv").plan(row(), "story").to_dict()
    for key in (
        "activity_title", "activity_type", "learning_goal", "story_connection",
        "recommended_send_mode", "estimated_minutes", "parent_effort", "materials",
        "pages", "instructions", "printable_components",
    ):
        assert key in data
    assert isinstance(data["pages"], list) and data["pages"]


def test_one_page_allowed_only_for_simple_types():
    pack = ActivityPack(
        activity_title="Quick Talk",
        activity_type="QUICK_DISCUSSION",
        send_mode="OPTIONAL",
        estimated_minutes=10,
        parent_effort="Low",
        learning_goal="Talk about the lesson",
        story_connection="From the story lesson",
        pages=[
            ActivityPage(
                page_title="Talk",
                page_type="QUICK_DISCUSSION",
                instructions=["Discuss one choice"],
                components=["prompt"],
                story_connection="From the story lesson",
            )
        ],
    )
    pack.validate()
