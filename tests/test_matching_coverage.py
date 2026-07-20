from __future__ import annotations

from pathlib import Path

from krishna_story_factory.activities.models import MatchingCard
from krishna_story_factory.activities.planner import ActivityPlanner
from krishna_story_factory.activities.qa import matching_coverage_from_pdf_text
from krishna_story_factory.models import PlanRow
from krishna_story_factory.pdf.activity_sheet import ActivitySheetGenerator, validate_activity_pdf


def _plan() -> PlanRow:
    return PlanRow(
        "005",
        "prayers-by-the-demigods-for-lord-krishna-in-the-womb",
        "Prayers by the Demigods for Lord Krishna in the Womb",
        "p",
        "l",
        "Krishna Book Ch. 2",
        "SB 10.2.25-42",
        "Demigods pray to Krishna within Devaki",
        "6-13",
        "daily",
        "",
        "pending",
    )


def test_story_005_five_matching_pairs_render_without_truncation(tmp_path: Path) -> None:
    activity = ActivityPlanner(tmp_path / "history.csv").plan(_plan(), "story")
    matching = next(p for p in activity.pages if p.page_type == "MATCHING_CARDS")
    pairs = [c for c in matching.components if isinstance(c, MatchingCard)]
    assert len(pairs) == 5
    assert {c.pair_id for c in pairs} == {"A", "B", "C", "D", "E"}
    assert {c.left for c in pairs} == {
        "Brahma", "Shiva", "Narada", "other demigods", "Devaki",
    }
    assert "leads the prayer gathering" in {c.right for c in pairs}
    assert "carries Krishna unseen within her" in {c.right for c in pairs}

    out = tmp_path / "activity_sheet.pdf"
    ActivitySheetGenerator().generate(_plan(), activity, out)
    check = validate_activity_pdf(out, tmp_path / "pages", activity=activity)
    assert not check.errors, check.errors
    assert check.matching_coverage is not None
    assert check.matching_coverage["expected_pairs"] == 5
    assert check.matching_coverage["rendered_pairs"] == 5
    assert check.matching_coverage["missing_labels"] == []
    assert check.matching_coverage["pass"] is True
    assert out.read_bytes()  # document exists
    # PDF metadata title
    raw = out.read_bytes()
    assert b"The Secret Prayer Gathering" in raw or activity.activity_title == "The Secret Prayer Gathering"


def test_matching_coverage_fails_when_label_missing() -> None:
    from krishna_story_factory.activities.models import ActivityPack, ActivityPage

    pack = ActivityPack(
        activity_title="The Secret Prayer Gathering",
        activity_type="MATCHING_GAME",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal="Match helpers",
        story_connection="Demigods pray to Krishna within Devaki",
        pages=[
            ActivityPage(
                "Who Came to Pray?",
                "MATCHING_CARDS",
                ["Match"],
                [
                    MatchingCard("Brahma", "leads the prayer gathering", "who", "A"),
                    MatchingCard("Devaki", "carries Krishna unseen within her", "who", "B"),
                ],
                story_connection="Demigods pray to Krishna within Devaki",
            ),
            ActivityPage(
                "Family",
                "FAMILY_MISSION",
                ["Share"],
                ["mission"],
                story_connection="Demigods pray to Krishna within Devaki",
            ),
        ],
        age_variants={"ages_6_8": "draw", "ages_9_13": "write"},
    )
    coverage = matching_coverage_from_pdf_text(pack, "Brahma leads the prayer gathering")
    assert coverage.pass_ is False
    assert any("Devaki" in label or "unseen" in label for label in coverage.missing_labels)


def test_matching_coverage_fails_on_orphan_count_mismatch() -> None:
    from krishna_story_factory.activities.models import ActivityPack, ActivityPage

    pack = ActivityPack(
        activity_title="The Secret Prayer Gathering",
        activity_type="MATCHING_GAME",
        send_mode="SEND_NOW",
        estimated_minutes=15,
        parent_effort="Low",
        learning_goal="Match helpers",
        story_connection="Demigods pray to Krishna within Devaki",
        pages=[
            ActivityPage(
                "Who Came to Pray?",
                "MATCHING_CARDS",
                ["Match"],
                [
                    MatchingCard("Brahma", "leads the prayer gathering", "who", "A"),
                    MatchingCard("Shiva", "joins and offers prayers", "who", "B"),
                    MatchingCard("Devaki", "carries Krishna unseen within her", "who", "C"),
                ],
                story_connection="Demigods pray to Krishna within Devaki",
            ),
            ActivityPage(
                "Family",
                "FAMILY_MISSION",
                ["Share"],
                ["mission"],
                story_connection="Demigods pray to Krishna within Devaki",
            ),
        ],
        age_variants={"ages_6_8": "draw", "ages_9_13": "write"},
    )
    # Only two left labels and two rights → missing third pair + orphan mismatch.
    text = "Brahma Shiva leads the prayer gathering joins and offers prayers"
    coverage = matching_coverage_from_pdf_text(pack, text)
    assert coverage.pass_ is False
    assert coverage.orphan_labels or coverage.missing_labels


def test_story_005_lotus_page_has_no_matching_language(tmp_path: Path) -> None:
    activity = ActivityPlanner(tmp_path / "history.csv").plan(_plan(), "story")
    lotus = next(p for p in activity.pages if p.page_type == "PRAYER_WHEEL")
    joined = " ".join(lotus.instructions).lower()
    assert "match" not in joined
    assert "younger: draw" in joined
    assert "older: write" in joined
    assert "family: discuss" in joined
