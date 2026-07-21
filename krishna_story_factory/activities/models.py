from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TypeAlias

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
class RolePlayCard:
    role: str
    line: str
    action: str
    prop: str


@dataclass(slots=True)
class SequenceCard:
    event: str
    drawing_prompt: str
    source_order: int


@dataclass(slots=True)
class MatchingCard:
    left: str
    right: str
    category: str
    pair_id: str = ""


@dataclass(slots=True)
class MissionCard:
    prompt: str
    completion_check: str


@dataclass(slots=True)
class DecisionNode:
    question: str
    choices: list[str]
    guidance: str


@dataclass(slots=True)
class PrintablePart:
    label: str
    cut_line: bool = False
    fold_line: bool = False
    assembly_instruction: str = ""


ActivityComponent: TypeAlias = RolePlayCard | SequenceCard | MatchingCard | MissionCard | DecisionNode | PrintablePart


def component_label(component: ActivityComponent) -> str:
    if isinstance(component, RolePlayCard):
        return component.role
    if isinstance(component, SequenceCard):
        return component.event
    if isinstance(component, MatchingCard):
        return f"{component.left} — {component.right}"
    if isinstance(component, MissionCard):
        return component.prompt
    if isinstance(component, DecisionNode):
        return component.question
    return component.label


def _component_from_raw(page_type: str, raw, index: int) -> ActivityComponent:
    if isinstance(raw, (RolePlayCard, SequenceCard, MatchingCard, MissionCard, DecisionNode, PrintablePart)):
        return raw
    if isinstance(raw, dict):
        mapping = {
            "ROLE_PLAY_CARDS": (RolePlayCard, ("role", "line", "action", "prop")),
            "PUPPET_CARDS": (RolePlayCard, ("role", "line", "action", "prop")),
            "STORY_SEQUENCE_CARDS": (SequenceCard, ("event", "drawing_prompt", "source_order")),
            "MATCHING_CARDS": (MatchingCard, ("left", "right", "category")),
            "SORTING_CARDS": (MatchingCard, ("left", "right", "category")),
            "FAMILY_MISSION": (MissionCard, ("prompt", "completion_check")),
            "DECISION_TREE": (DecisionNode, ("question", "choices", "guidance")),
        }
        cls, required = mapping.get(page_type, (PrintablePart, ("label",)))
        missing = [name for name in required if raw.get(name) in (None, "", [])]
        if missing:
            raise ValueError(f"Malformed {page_type} component; missing: {', '.join(missing)}")
        return cls(**{name: raw[name] for name in cls.__dataclass_fields__ if name in raw})
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"Malformed {page_type} component at index {index}.")
    text = raw.strip()
    if text.startswith("{") or "components:" in text.lower():
        raise ValueError(f"Raw dictionary/JSON component rejected for {page_type}.")
    if page_type in {"ROLE_PLAY_CARDS", "PUPPET_CARDS"}:
        return RolePlayCard(text, f"In paraphrase: I remember my part in {text}.", "Act the story moment calmly.", "simple cloth")
    if page_type == "STORY_SEQUENCE_CARDS":
        return SequenceCard(text, f"Draw one detail from: {text}", index + 1)
    if page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
        return MatchingCard(text, f"Story match {index + 1}", "story detail")
    if page_type == "FAMILY_MISSION":
        return MissionCard(text, "□ We completed this together")
    if page_type == "DECISION_TREE":
        return DecisionNode(text, ["Safe and honest", "Ask a trusted adult"], "Choose safety and truthfulness.")
    if page_type == "CUT_AND_BUILD_PARTS":
        return PrintablePart(text, cut_line=True, fold_line=True, assembly_instruction=f"Attach {text} as shown.")
    return PrintablePart(text)


@dataclass(slots=True)
class ActivityPage:
    page_title: str
    page_type: str
    instructions: list[str] = field(default_factory=list)
    components: list[ActivityComponent] = field(default_factory=list)
    layout_hint: str = ""
    story_connection: str = ""

    def __post_init__(self) -> None:
        self.components = [_component_from_raw(self.page_type, item, index) for index, item in enumerate(self.components)]
        if self.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
            cards = [c for c in self.components if isinstance(c, MatchingCard)]
            # Flat string lists are authored as [lefts..., rights...]; raw conversion
            # temporarily stores each string as left with a placeholder right.
            if (
                len(cards) >= 2
                and len(cards) % 2 == 0
                and all((c.right or "").startswith("Story match ") for c in cards)
            ):
                half = len(cards) // 2
                lefts = [c.left for c in cards[:half]]
                rights = [c.left for c in cards[half:]]
                self.components = [
                    MatchingCard(lefts[i], rights[i], "story", pair_id=chr(65 + i))
                    for i in range(half)
                ]
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            next_id = 0
            for component in self.components:
                if isinstance(component, MatchingCard) and not (component.pair_id or "").strip():
                    component.pair_id = letters[next_id % len(letters)]
                    next_id += 1

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
            items.extend(component_label(component) for component in page.components)
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
            blob = " ".join(component_label(item) for item in page.components).lower()
            if "{'" in blob or '"components"' in blob or "components:" in blob:
                raise ValueError(f"Page '{page.page_title}' contains raw dictionary/JSON content.")
            if page.page_type in {"ROLE_PLAY_CARDS", "PUPPET_CARDS"}:
                cards = [item for item in page.components if isinstance(item, RolePlayCard)]
                if len(cards) < 4 or any(not (c.role and c.line and c.action) for c in cards):
                    raise ValueError("ROLE_PLAY_CARDS requires at least four complete role cards.")
            elif page.page_type == "STORY_SEQUENCE_CARDS":
                cards = [item for item in page.components if isinstance(item, SequenceCard)]
                if len(cards) < 4 or len({c.source_order for c in cards}) != len(cards):
                    raise ValueError("STORY_SEQUENCE_CARDS requires at least four ordered event cards.")
            elif page.page_type in {"MATCHING_CARDS", "SORTING_CARDS"}:
                cards = [item for item in page.components if isinstance(item, MatchingCard)]
                if len(cards) < 4 or any(not (c.left and c.right) for c in cards):
                    raise ValueError("MATCHING_CARDS requires at least four complete pairs.")
            elif page.page_type == "DRAW_AND_REFLECT":
                if not page.components or not any(component_label(c).strip() for c in page.components):
                    raise ValueError("DRAW_AND_REFLECT requires a story-specific reflection.")
            elif page.page_type == "CUT_AND_BUILD_PARTS":
                parts = [item for item in page.components if isinstance(item, PrintablePart)]
                if not parts or any(not (p.cut_line and p.fold_line and p.assembly_instruction) for p in parts):
                    raise ValueError("CUT_AND_BUILD_PARTS requires cut lines, fold lines, and assembly instructions.")
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
            components=list(p.get("components", [])),
            layout_hint=str(p.get("layout_hint", "")),
            story_connection=str(p.get("story_connection") or data.get("story_connection") or ""),
        )
        for p in pages_raw
    ]
    # Legacy flat plan → synthesize pages if needed
    if not pages:
        components = list(data.get("printable_components", []))
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
