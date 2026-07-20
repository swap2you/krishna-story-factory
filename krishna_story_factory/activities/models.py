from __future__ import annotations

from dataclasses import asdict, dataclass, field

ALLOWED_ACTIVITY_TYPES = {
    "PAPER_CRAFT", "CUT_AND_BUILD", "PUPPET_PLAY", "MINI_DRAMA", "ROLE_CARDS",
    "STORY_SEQUENCE", "MATCHING_GAME", "STORY_MAP", "MAZE_OR_PATH", "SORTING_GAME",
    "PRAYER_OR_GRATITUDE_CRAFT", "FAMILY_MISSION", "MEMORY_GAME", "SIMPLE_BOARD_GAME",
    "DRAW_AND_REFLECT", "WORD_SEARCH", "CROSSWORD", "COLORING_ONLY", "QUICK_DISCUSSION",
}

PAGE_TYPES = {
    "STORY_MAP", "STORY_SEQUENCE_CARDS", "CUT_AND_BUILD_PARTS", "ROLE_PLAY_CARDS",
    "PUPPET_CARDS", "MAZE_OR_PATH", "MATCHING_CARDS", "SORTING_CARDS", "MINI_BOARD_GAME",
    "PRAYER_WHEEL", "GRATITUDE_GARLAND", "DECISION_TREE", "EMOTION_MAP",
    "DRAW_AND_REFLECT", "WORD_SEARCH", "CROSSWORD", "FAMILY_MISSION",
    "QUICK_DISCUSSION", "ANSWER_KEY_INTERNAL_ONLY",
}

HEAVY_CRAFTS = {"PAPER_CRAFT", "CUT_AND_BUILD", "PRAYER_OR_GRATITUDE_CRAFT"}
WRITTEN_TYPES = {"DRAW_AND_REFLECT", "QUICK_DISCUSSION", "CROSSWORD", "WORD_SEARCH"}
SIMPLE_TYPES = {"COLORING_ONLY", "QUICK_DISCUSSION"}
HISTORY_FIELDS = ("chapter_no", "slug", "activity_type", "activity_title", "recommended_send_mode", "generated_at")


@dataclass(slots=True)
class ActivityPage:
    page_title: str
    page_type: str
    instructions: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    layout_hint: str = ""
    story_connection: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class ActivityPack:
    activity_title: str
    activity_type: str
    send_mode: str
    estimated_minutes: int
    parent_effort: str
    learning_goal: str
    story_connection: str
    materials: list[str] = field(default_factory=list)
    pages: list[ActivityPage] = field(default_factory=list)
    answer_key: list[str] = field(default_factory=list)
    parent_note: str = ""
    qa_requirements: list[str] = field(default_factory=list)
    age_variants: dict[str, str] = field(default_factory=dict)
    safety_note: str = ""
    completion_prompt: str = ""
    review_questions: list[str] = field(default_factory=list)

    # Compatibility aliases used by existing pipeline/manifest code
    @property
    def activity_title_compat(self) -> str:
        return self.activity_title

    @property
    def recommended_send_mode(self) -> str:
        return self.send_mode

    @property
    def printable_components(self) -> list[str]:
        items: list[str] = []
        for page in self.pages:
            items.extend(page.components)
        return items

    @property
    def instructions(self) -> list[str]:
        items: list[str] = []
        for page in self.pages:
            items.extend(page.instructions)
        return items or ["Complete each printable part."]

    def validate(self) -> None:
        if self.activity_type not in ALLOWED_ACTIVITY_TYPES:
            raise ValueError(f"Invalid primary activity type: {self.activity_type}")
        if not self.pages:
            raise ValueError("ActivityPack requires at least one page.")
        if self.activity_type in SIMPLE_TYPES:
            if not 1 <= len(self.pages) <= 2:
                raise ValueError("Simple activities must be 1-2 pages.")
        else:
            if not 2 <= len(self.pages) <= 4:
                raise ValueError("Normal ActivityPacks must be 2-4 pages.")
        if len(self.pages) > 5:
            raise ValueError("ActivityPack cannot exceed 5 pages.")
        if not 10 <= self.estimated_minutes <= 30:
            raise ValueError("Activity must take 10-30 minutes.")
        for page in self.pages:
            if page.page_type not in PAGE_TYPES:
                raise ValueError(f"Invalid page type: {page.page_type}")
            if not page.story_connection.strip():
                raise ValueError(f"Page '{page.page_title}' missing story_connection.")
        if self.activity_type in HEAVY_CRAFTS and "scissor" in " ".join(self.materials).lower() and not self.safety_note:
            raise ValueError("Crafts requiring scissors need a safety note.")

    def to_dict(self) -> dict:
        data = {
            "activity_title": self.activity_title,
            "activity_type": self.activity_type,
            "recommended_send_mode": self.send_mode,
            "send_mode": self.send_mode,
            "estimated_minutes": self.estimated_minutes,
            "parent_effort": self.parent_effort,
            "learning_goal": self.learning_goal,
            "story_connection": self.story_connection,
            "materials": self.materials,
            "pages": [p.to_dict() for p in self.pages],
            "parent_note": self.parent_note,
            "qa_requirements": self.qa_requirements,
            "age_variants": self.age_variants,
            "safety_note": self.safety_note,
            "completion_prompt": self.completion_prompt,
            "review_questions": self.review_questions,
            "printable_components": self.printable_components,
            "instructions": self.instructions,
        }
        return data


# Backwards-compatible alias
ActivityPlan = ActivityPack


def pack_from_dict(data: dict) -> ActivityPack:
    pages_raw = data.get("pages") or []
    pages = [
        ActivityPage(
            page_title=str(p.get("page_title", "Activity")),
            page_type=str(p.get("page_type", "FAMILY_MISSION")),
            instructions=[str(x) for x in p.get("instructions", [])],
            components=[str(x) for x in p.get("components", [])],
            layout_hint=str(p.get("layout_hint", "")),
            story_connection=str(p.get("story_connection") or data.get("story_connection") or ""),
        )
        for p in pages_raw
    ]
    # Legacy flat plan → synthesize pages if needed
    if not pages:
        components = [str(x) for x in data.get("printable_components", [])]
        pages = [
            ActivityPage(
                page_title=str(data.get("activity_title", "Activity")),
                page_type=_infer_page_type(str(data.get("activity_type", "FAMILY_MISSION"))),
                instructions=[str(x) for x in data.get("instructions", [])],
                components=components[:8],
                story_connection=str(data.get("story_connection", "")),
            ),
            ActivityPage(
                page_title="Family reflection",
                page_type="FAMILY_MISSION",
                instructions=["Share one story-connected kindness with your family."],
                components=["family reflection card"],
                story_connection=str(data.get("story_connection", "")),
            ),
        ]
    return ActivityPack(
        activity_title=str(data.get("activity_title", "")),
        activity_type=str(data.get("activity_type", "")),
        send_mode=str(data.get("send_mode") or data.get("recommended_send_mode") or "SEND_NOW"),
        estimated_minutes=int(data.get("estimated_minutes", 15) or 15),
        parent_effort=str(data.get("parent_effort", "Low")),
        learning_goal=str(data.get("learning_goal", "")),
        story_connection=str(data.get("story_connection", "")),
        materials=[str(x) for x in data.get("materials", [])],
        pages=pages,
        answer_key=[str(x) for x in data.get("answer_key", [])],
        parent_note=str(data.get("parent_note", "")),
        qa_requirements=[str(x) for x in data.get("qa_requirements", [])],
        age_variants=dict(data.get("age_variants") or {}),
        safety_note=str(data.get("safety_note", "")),
        completion_prompt=str(data.get("completion_prompt", "")),
        review_questions=[str(x) for x in data.get("review_questions", [])],
    )


def _infer_page_type(activity_type: str) -> str:
    mapping = {
        "PRAYER_OR_GRATITUDE_CRAFT": "PRAYER_WHEEL",
        "CUT_AND_BUILD": "CUT_AND_BUILD_PARTS",
        "STORY_SEQUENCE": "STORY_SEQUENCE_CARDS",
        "MINI_DRAMA": "ROLE_PLAY_CARDS",
        "ROLE_CARDS": "ROLE_PLAY_CARDS",
        "MATCHING_GAME": "MATCHING_CARDS",
        "SORTING_GAME": "SORTING_CARDS",
        "MAZE_OR_PATH": "MAZE_OR_PATH",
        "STORY_MAP": "STORY_MAP",
        "FAMILY_MISSION": "FAMILY_MISSION",
        "WORD_SEARCH": "WORD_SEARCH",
        "CROSSWORD": "CROSSWORD",
        "DRAW_AND_REFLECT": "DRAW_AND_REFLECT",
        "QUICK_DISCUSSION": "QUICK_DISCUSSION",
        "SIMPLE_BOARD_GAME": "MINI_BOARD_GAME",
        "PUPPET_PLAY": "PUPPET_CARDS",
        "MEMORY_GAME": "MATCHING_CARDS",
        "COLORING_ONLY": "DRAW_AND_REFLECT",
        "PAPER_CRAFT": "CUT_AND_BUILD_PARTS",
    }
    return mapping.get(activity_type, "FAMILY_MISSION")
