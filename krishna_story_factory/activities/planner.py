from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..models import PlanRow

ALLOWED_ACTIVITY_TYPES = {
    "PAPER_CRAFT", "CUT_AND_BUILD", "PUPPET_PLAY", "MINI_DRAMA", "ROLE_CARDS",
    "STORY_SEQUENCE", "MATCHING_GAME", "STORY_MAP", "MAZE_OR_PATH", "SORTING_GAME",
    "PRAYER_OR_GRATITUDE_CRAFT", "FAMILY_MISSION", "MEMORY_GAME", "SIMPLE_BOARD_GAME",
    "DRAW_AND_REFLECT", "WORD_SEARCH", "CROSSWORD", "COLORING_ONLY", "QUICK_DISCUSSION",
}
HEAVY_CRAFTS = {"PAPER_CRAFT", "CUT_AND_BUILD", "PRAYER_OR_GRATITUDE_CRAFT"}
WRITTEN_TYPES = {"DRAW_AND_REFLECT", "QUICK_DISCUSSION", "CROSSWORD", "WORD_SEARCH"}
HISTORY_FIELDS = ("chapter_no", "slug", "activity_type", "activity_title", "recommended_send_mode", "generated_at")


@dataclass(slots=True)
class ActivityPlan:
    activity_title: str
    activity_type: str
    learning_goal: str
    story_connection: str
    recommended_send_mode: str
    estimated_minutes: int
    parent_effort: str
    age_variants: dict[str, str]
    materials: list[str] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    review_questions: list[str] = field(default_factory=list)
    printable_components: list[str] = field(default_factory=list)
    safety_note: str = ""
    completion_prompt: str = ""
    answer_key: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.activity_type not in ALLOWED_ACTIVITY_TYPES:
            raise ValueError(f"Invalid primary activity type: {self.activity_type}")
        if not 10 <= self.estimated_minutes <= 25:
            raise ValueError("Activity must take 10-25 minutes.")
        if self.activity_type in HEAVY_CRAFTS and "scissor" in " ".join(self.materials).lower() and not self.safety_note:
            raise ValueError("Crafts requiring scissors need a safety note.")

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("answer_key", None)
        return data


class ActivityPlanner:
    def __init__(self, history_path: Path) -> None:
        self.history_path = history_path

    def plan(self, plan: PlanRow, story_text: str) -> ActivityPlan:
        history = self.read_history()
        if plan.chapter_no == "001":
            selected = _prayer_wheel(plan)
        elif plan.chapter_no == "002":
            selected = _wedding_chariot(plan)
        elif plan.chapter_no == "003":
            selected = _truthfulness_sequence(plan)
        else:
            selected = self._generic(plan, story_text, history)
        selected.validate()
        return selected

    def read_history(self) -> list[dict[str, str]]:
        if not self.history_path.exists():
            return []
        with self.history_path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def record(self, plan: PlanRow, selected: ActivityPlan) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        exists = self.history_path.exists()
        with self.history_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow({
                "chapter_no": plan.chapter_no, "slug": plan.slug,
                "activity_type": selected.activity_type, "activity_title": selected.activity_title,
                "recommended_send_mode": selected.recommended_send_mode,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })

    def _generic(self, plan: PlanRow, story_text: str, history: list[dict[str, str]]) -> ActivityPlan:
        recent = [row.get("activity_type", "") for row in history[-5:]]
        candidates = ["STORY_SEQUENCE", "MINI_DRAMA", "MATCHING_GAME", "FAMILY_MISSION", "MAZE_OR_PATH", "WORD_SEARCH"]
        for kind in candidates:
            if recent and kind == recent[-1]:
                continue
            if kind == "WORD_SEARCH" and "WORD_SEARCH" in recent:
                continue
            if recent and kind in HEAVY_CRAFTS and recent[-1] in HEAVY_CRAFTS:
                continue
            if recent and kind in WRITTEN_TYPES and recent[-1] in WRITTEN_TYPES:
                continue
            return _generic_plan(plan, kind)
        return _generic_plan(plan, "FAMILY_MISSION")


def _prayer_wheel(plan: PlanRow) -> ActivityPlan:
    return ActivityPlan(
        activity_title="Prayer Petal Wheel", activity_type="PRAYER_OR_GRATITUDE_CRAFT",
        learning_goal="Turn Mother Earth's caring prayer into six simple acts of compassion.",
        story_connection="Mother Earth and the demigods asked Lord Vishnu to help the world.",
        recommended_send_mode="OPTIONAL", estimated_minutes=20, parent_effort="Low: supervise cutting; the child can glue the pieces.",
        age_variants={"ages_6_8": "Draw one caring picture on each petal.", "ages_9_13": "Write one sincere sentence on each petal."},
        materials=["pencil or crayons", "child-safe scissors", "glue"],
        instructions=["Write or draw on all six petals.", "Cut around each dotted petal and the center circle.", "Arrange the petal tips behind the center circle.", "Glue the pieces together and share one prayer."],
        review_questions=["How did Mother Earth's prayer show care for others?"],
        printable_components=["My Prayer for the World center", "six prompted prayer petals"],
        safety_note="PARENT HELP: An adult should supervise child-safe scissors.",
        completion_prompt="Share one petal with your family and offer that prayer together.",
    )


def _wedding_chariot(plan: PlanRow) -> ActivityPlan:
    return ActivityPlan(
        activity_title="Build the Wedding Chariot", activity_type="CUT_AND_BUILD",
        learning_goal="Build the central scene, then place its four events in story order.",
        story_connection="Kamsa drove Devaki and Vasudeva when the heavenly voice changed the celebration.",
        recommended_send_mode="WEEKEND_PROJECT", estimated_minutes=25, parent_effort="Medium: supervise cutting and help fold the standees.",
        age_variants={"ages_6_8": "Color and assemble with adult cutting help.", "ages_9_13": "Cut, fold, assemble, and retell all four events."},
        materials=["crayons", "child-safe scissors", "glue or tape", "one small recycled box (optional)"],
        instructions=["Color the parts before cutting.", "Cut only on dotted lines; fold on solid lines.", "Attach both wheels and canopy to the chariot body.", "Place Kamsa at the front driving; place adult Devaki and adult Vasudeva behind him.", "Order the four story cards, then act out the scene."],
        review_questions=["How did Vasudeva protect Devaki when Kamsa became afraid?"],
        printable_components=["chariot body", "two wheels", "canopy", "flower garlands", "Devaki standee", "Vasudeva standee", "Kamsa charioteer standee", "four sequence cards"],
        safety_note="PARENT HELP: An adult should supervise scissors. Use glue or tape carefully.",
        completion_prompt="Retell the scene: celebration, procession, heavenly voice, protection.",
        answer_key=["1", "2", "3", "4"],
    )


def _truthfulness_sequence(plan: PlanRow) -> ActivityPlan:
    return ActivityPlan(
        activity_title="Vasudeva's Truthfulness Story Path", activity_type="STORY_SEQUENCE",
        learning_goal="Retell the six source-bounded events and identify Vasudeva's truthful choice.",
        story_connection="The cards follow the first son's birth through Kamsa returning the child.",
        recommended_send_mode="PARENT_GUIDED", estimated_minutes=15, parent_effort="Low: read the cards and discuss the choice.",
        age_variants={"ages_6_8": "Number and draw one detail on each card.", "ages_9_13": "Number each card and explain the truthful choice."},
        materials=["pencil", "crayons"],
        instructions=["Number the six events in story order.", "Draw one source-faithful detail on each card.", "Circle the card showing Vasudeva's truthful choice.", "Retell the ending: Kamsa returns the child."],
        review_questions=["Why was keeping his word difficult for Vasudeva?", "What did Kamsa do after seeing Vasudeva's honesty?"],
        printable_components=[
            "The first son is born", "Vasudeva remembers his word", "Vasudeva brings the child",
            "Kamsa is astonished", "Kamsa returns the child", "Truthfulness shines",
        ],
        completion_prompt="Retell all six events, then share one promise you can keep with care.",
    )


def _generic_plan(plan: PlanRow, kind: str) -> ActivityPlan:
    titles = {"STORY_SEQUENCE": "Put the Pastime in Order", "MINI_DRAMA": "Act the Turning Point", "MATCHING_GAME": "Match the Story Clues", "FAMILY_MISSION": "Family Kindness Mission", "MAZE_OR_PATH": "Path Through the Pastime", "WORD_SEARCH": "Story Word Search"}
    return ActivityPlan(
        activity_title=titles[kind], activity_type=kind, learning_goal="Remember the main turning point and lesson.",
        story_connection=f"Every prompt uses events and choices from {plan.title}.", recommended_send_mode="SEND_NOW",
        estimated_minutes=15, parent_effort="Low", age_variants={"ages_6_8": "Use pictures or short answers.", "ages_9_13": "Explain each choice in one sentence."},
        materials=["pencil", "crayons"], instructions=["Read the story clue.", "Complete each printable part.", "Tell someone how it connects to the pastime."],
        review_questions=["What was the most important choice in this story?"], printable_components=["four story-specific activity cards"],
        completion_prompt="Share your favorite clue with your family.",
    )
