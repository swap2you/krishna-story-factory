from __future__ import annotations

import csv
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from ..models import PlanRow
from .models import (
    ALLOWED_ACTIVITY_TYPES,
    HEAVY_CRAFTS,
    HISTORY_FIELDS,
    SIMPLE_TYPES,
    WRITTEN_TYPES,
    ActivityPack,
    ActivityPage,
    ActivityPlan,
    pack_from_dict,
)

logger = logging.getLogger(__name__)


class ActivityPlanner:
    def __init__(self, history_path: Path, settings=None) -> None:
        self.history_path = history_path
        self.settings = settings

    def plan(self, plan: PlanRow, story_text: str) -> ActivityPack:
        history = self.read_history()
        selected = self._preferred_pack(plan)
        preferred = selected is not None
        if selected is None:
            selected = self._llm_pack(plan, story_text, history)
        if selected is None:
            selected = self._dynamic_pack(plan, story_text, history)
        # Preferred story packs are source overrides; do not diversify them away.
        if not preferred:
            selected = self._enforce_diversity(selected, history)
        selected.validate()
        return selected

    def read_history(self) -> list[dict[str, str]]:
        if not self.history_path.exists():
            return []
        with self.history_path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def record(self, plan: PlanRow, selected: ActivityPack) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        exists = self.history_path.exists()
        with self.history_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HISTORY_FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow({
                "chapter_no": plan.chapter_no,
                "slug": plan.slug,
                "activity_type": selected.activity_type,
                "activity_title": selected.activity_title,
                "recommended_send_mode": selected.send_mode,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })

    def _preferred_pack(self, plan: PlanRow) -> ActivityPack | None:
        builders = {
            "001": _pack_001,
            "002": _pack_002,
            "003": _pack_003,
        }
        builder = builders.get(plan.chapter_no.strip().zfill(3))
        return builder(plan) if builder else None

    def _llm_pack(self, plan: PlanRow, story_text: str, history: list[dict[str, str]]) -> ActivityPack | None:
        if not self.settings or not getattr(self.settings, "openai_text_enabled", False):
            return None
        if not getattr(self.settings, "openai_api_key", ""):
            return None
        try:
            from ..prompts_loader import load_master_section, load_project_text

            section = load_master_section(self.settings.project_root, "ADAPTIVE_ACTIVITY_PLANNER")
            bank = load_project_text(self.settings.project_root, "prompts/activity_bank/01_ACTIVITY_PACK_PLANNER.md")
            recent = [f"{r.get('activity_type')} ({r.get('activity_title')})" for r in history[-6:]]
            prompt = (
                f"{section}\n\n{bank}\n\n"
                f"QUEUE ROW: chapter={plan.chapter_no} title={plan.title}\n"
                f"SOURCE: {plan.source_reference}\n"
                f"SEED: {plan.summary_seed}\n"
                f"MUST INCLUDE: {getattr(plan, 'must_include', '')}\n"
                f"MUST AVOID: {getattr(plan, 'must_avoid', '')}\n"
                f"RECENT ACTIVITY HISTORY: {recent}\n\n"
                f"STORY.MD:\n{story_text[:8000]}\n\n"
                "Return only valid ActivityPack JSON with pages[]."
            )
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.responses.create(model=self.settings.openai_text_model, input=prompt)
            raw = getattr(response, "output_text", "") or ""
            try:
                data = _parse_json(raw)
            except Exception:
                repair = load_project_text(self.settings.project_root, "prompts/activity_bank/08_ACTIVITY_REPAIR.md")
                repair_prompt = f"{repair}\n\nBroken response:\n{raw[:6000]}\n\nReturn only valid ActivityPack JSON."
                repaired = client.responses.create(model=self.settings.openai_text_model, input=repair_prompt)
                data = _parse_json(getattr(repaired, "output_text", "") or "")
            pack = pack_from_dict(data)
            pack.validate()
            return pack
        except Exception as exc:
            logger.warning("LLM activity pack failed (%s); using deterministic pack.", type(exc).__name__)
            return None

    def _dynamic_pack(self, plan: PlanRow, story_text: str, history: list[dict[str, str]]) -> ActivityPack:
        kind = self._choose_type(history)
        title = plan.title
        connection = f"Every printable piece comes from the turning point of {title}."
        seed = (plan.summary_seed or title).strip()
        if kind == "STORY_SEQUENCE":
            events = _extract_event_labels(story_text, seed)
            return ActivityPack(
                activity_title=f"Put {title} in Order",
                activity_type=kind,
                send_mode="SEND_NOW",
                estimated_minutes=15,
                parent_effort="Low",
                learning_goal="Retell the pastime in correct order and name the kind choice.",
                story_connection=connection,
                materials=["pencil", "crayons"],
                pages=[
                    ActivityPage(
                        page_title="Story sequence cards",
                        page_type="STORY_SEQUENCE_CARDS",
                        instructions=["Number the cards in story order.", "Draw one source-faithful detail on each card."],
                        components=events,
                        story_connection=connection,
                    ),
                    ActivityPage(
                        page_title="Family kindness mission",
                        page_type="FAMILY_MISSION",
                        instructions=["Choose one kind action from the story and do it today."],
                        components=["family mission card", "completion checkbox"],
                        story_connection=connection,
                    ),
                ],
                age_variants={"ages_6_8": "Use pictures.", "ages_9_13": "Write one sentence per card."},
                completion_prompt="Retell the story using your numbered cards.",
                review_questions=["What was the most important choice?"],
                answer_key=[str(i) for i in range(1, len(events) + 1)],
            )
        if kind == "MATCHING_GAME":
            return ActivityPack(
                activity_title=f"Match Clues from {title}",
                activity_type=kind,
                send_mode="SEND_NOW",
                estimated_minutes=12,
                parent_effort="Low",
                learning_goal="Match characters, actions, and meanings from the pastime.",
                story_connection=connection,
                materials=["pencil", "child-safe scissors"],
                pages=[
                    ActivityPage(
                        page_title="Matching cards",
                        page_type="MATCHING_CARDS",
                        instructions=["Cut the cards.", "Match each character or object to its story action."],
                        components=_matching_labels(plan),
                        story_connection=connection,
                    ),
                    ActivityPage(
                        page_title="Quick discussion",
                        page_type="QUICK_DISCUSSION",
                        instructions=["Answer two story questions with a parent."],
                        components=["discussion prompts"],
                        story_connection=connection,
                    ),
                ],
                safety_note="PARENT HELP: An adult should supervise child-safe scissors.",
                age_variants={"ages_6_8": "Match with pictures.", "ages_9_13": "Explain each match."},
                completion_prompt="Explain one matched pair to your family.",
            )
        if kind == "MINI_DRAMA":
            return ActivityPack(
                activity_title=f"Act the Turning Point of {title}",
                activity_type=kind,
                send_mode="PARENT_GUIDED",
                estimated_minutes=18,
                parent_effort="Low",
                learning_goal="Act the central scene with short lines and simple props.",
                story_connection=connection,
                materials=["pencil", "scarf or cloth (optional)"],
                pages=[
                    ActivityPage(
                        page_title="Role-play cards",
                        page_type="ROLE_PLAY_CARDS",
                        instructions=["Choose a role.", "Read the short line.", "Act the scene in order."],
                        components=_role_labels(plan),
                        story_connection=connection,
                    ),
                    ActivityPage(
                        page_title="Draw and reflect",
                        page_type="DRAW_AND_REFLECT",
                        instructions=["Draw the turning point.", "Write one sentence about the kind choice."],
                        components=["drawing box", "reflection line"],
                        story_connection=connection,
                    ),
                ],
                age_variants={"ages_6_8": "Use short lines.", "ages_9_13": "Add one narrator sentence."},
                completion_prompt="Perform the scene once for your family.",
            )
        if kind == "MAZE_OR_PATH":
            return ActivityPack(
                activity_title=f"Path Through {title}",
                activity_type=kind,
                send_mode="SEND_NOW",
                estimated_minutes=12,
                parent_effort="Low",
                learning_goal="Follow the story path and name the helpful choice.",
                story_connection=connection,
                materials=["pencil"],
                pages=[
                    ActivityPage(
                        page_title="Story path",
                        page_type="MAZE_OR_PATH",
                        instructions=["Trace the path through each story checkpoint.", "Circle the helpful choice."],
                        components=["start", "checkpoint 1", "checkpoint 2", "turning point", "kind choice", "finish"],
                        story_connection=connection,
                    ),
                    ActivityPage(
                        page_title="Family mission",
                        page_type="FAMILY_MISSION",
                        instructions=["Do one story-connected kindness today."],
                        components=["mission card"],
                        story_connection=connection,
                    ),
                ],
                age_variants={"ages_6_8": "Trace with a finger first.", "ages_9_13": "Label each checkpoint."},
                completion_prompt="Tell someone what the kind choice was.",
            )
        if kind == "WORD_SEARCH":
            words = _word_bank(plan)
            return ActivityPack(
                activity_title=f"Words from {title}",
                activity_type=kind,
                send_mode="OPTIONAL",
                estimated_minutes=12,
                parent_effort="Low",
                learning_goal="Find story words and recall their meaning.",
                story_connection=connection,
                materials=["pencil"],
                pages=[
                    ActivityPage(
                        page_title="Story word search",
                        page_type="WORD_SEARCH",
                        instructions=["Find each word.", "Circle one word and tell why it matters."],
                        components=words,
                        story_connection=connection,
                    ),
                    ActivityPage(
                        page_title="Draw the meaning",
                        page_type="DRAW_AND_REFLECT",
                        instructions=["Draw the scene for one found word."],
                        components=["drawing box"],
                        story_connection=connection,
                    ),
                ],
                age_variants={"ages_6_8": "Find four words.", "ages_9_13": "Find all words and explain one."},
                completion_prompt="Share the most important word with your family.",
            )
        # FAMILY_MISSION default
        return ActivityPack(
            activity_title=f"Family Mission from {title}",
            activity_type="FAMILY_MISSION",
            send_mode="SEND_NOW",
            estimated_minutes=15,
            parent_effort="Low",
            learning_goal="Practice one story lesson as a family kindness.",
            story_connection=connection,
            materials=["pencil"],
            pages=[
                ActivityPage(
                    page_title="Story map",
                    page_type="STORY_MAP",
                    instructions=["Fill the three story boxes: beginning, turning point, lesson."],
                    components=["beginning box", "turning point box", "lesson box"],
                    story_connection=connection,
                ),
                ActivityPage(
                    page_title="Family mission card",
                    page_type="FAMILY_MISSION",
                    instructions=["Choose one kindness inspired by the story and complete it today."],
                    components=["mission card", "done checkbox"],
                    story_connection=connection,
                ),
            ],
            age_variants={"ages_6_8": "Draw the mission.", "ages_9_13": "Write the mission in one sentence."},
            completion_prompt="Check the box when the mission is done.",
        )

    def _choose_type(self, history: list[dict[str, str]]) -> str:
        recent = [row.get("activity_type", "") for row in history[-6:]]
        last = recent[-1] if recent else ""
        word_search_count = sum(1 for t in recent if t == "WORD_SEARCH")
        candidates = [
            "STORY_SEQUENCE", "MINI_DRAMA", "MATCHING_GAME", "FAMILY_MISSION",
            "MAZE_OR_PATH", "PRAYER_OR_GRATITUDE_CRAFT", "CUT_AND_BUILD", "WORD_SEARCH",
        ]
        for kind in candidates:
            if kind == last:
                continue
            if kind == "WORD_SEARCH" and word_search_count >= 1:
                continue
            if kind in HEAVY_CRAFTS and any(t in HEAVY_CRAFTS for t in recent[-3:]):
                continue
            if kind in WRITTEN_TYPES and any(t in WRITTEN_TYPES for t in recent[-3:]):
                continue
            return kind
        return "FAMILY_MISSION"

    def _enforce_diversity(self, pack: ActivityPack, history: list[dict[str, str]]) -> ActivityPack:
        recent = [row.get("activity_type", "") for row in history[-6:]]
        last3 = recent[-3:]
        last = recent[-1] if recent else ""
        needs_rebuild = False
        if last and pack.activity_type == last:
            needs_rebuild = True
        if pack.activity_type == "WORD_SEARCH" and sum(1 for t in recent if t == "WORD_SEARCH") >= 1:
            needs_rebuild = True
        if pack.activity_type in HEAVY_CRAFTS and any(t in HEAVY_CRAFTS for t in last3):
            needs_rebuild = True
        if pack.activity_type in WRITTEN_TYPES and any(t in WRITTEN_TYPES for t in last3):
            needs_rebuild = True
        if needs_rebuild:
            pack = self._dynamic_pack(
                PlanRow(
                    chapter_no="999", slug="diversity", title=pack.activity_title,
                    project="", library_id="", source_reference="", scripture_reference="",
                    summary_seed=pack.story_connection, age_range="6-12", package_type="",
                    send_date="", status="pending",
                ),
                pack.story_connection,
                history,
            )
        return pack


def _pack_001(plan: PlanRow) -> ActivityPack:
    connection = "Mother Earth and the demigods prayed to Lord Vishnu for help."
    return ActivityPack(
        activity_title="Prayer Petal Wheel",
        activity_type="PRAYER_OR_GRATITUDE_CRAFT",
        send_mode="OPTIONAL",
        estimated_minutes=20,
        parent_effort="Low: supervise cutting; the child can glue the pieces.",
        learning_goal="Turn Mother Earth's caring prayer into six simple acts of compassion.",
        story_connection=connection,
        materials=["pencil or crayons", "child-safe scissors", "glue"],
        pages=[
            ActivityPage(
                page_title="Prayer Petal Wheel",
                page_type="PRAYER_WHEEL",
                instructions=[
                    "Write or draw on all six petals.",
                    "Cut around each dotted petal and the center circle.",
                    "Arrange the petal tips behind the center circle.",
                    "Glue the pieces together and share one prayer.",
                ],
                components=[
                    "My Prayer for the World center",
                    "My family petal", "Animals petal", "Mother Earth petal",
                    "Someone who feels sad petal", "My community petal", "My special prayer petal",
                ],
                story_connection=connection,
                layout_hint="wheel_with_six_petals",
            ),
            ActivityPage(
                page_title="Who helped Mother Earth?",
                page_type="MATCHING_CARDS",
                instructions=["Match each helper to what they did.", "Then complete the family reflection."],
                components=["Mother Earth", "Brahma", "demigods", "Lord Vishnu", "prayed for the world", "led the prayers", "joined with faith", "promised Krishna would come"],
                story_connection=connection,
            ),
        ],
        age_variants={"ages_6_8": "Draw one caring picture on each petal.", "ages_9_13": "Write one sincere sentence on each petal."},
        safety_note="PARENT HELP: An adult should supervise child-safe scissors.",
        completion_prompt="Share one petal with your family and offer that prayer together.",
        review_questions=["How did Mother Earth's prayer show care for others?"],
        parent_note="Weekend-friendly optional craft. Keep scissors supervised.",
        qa_requirements=["six petals", "center circle", "matching helpers", "no blank page"],
    )


def _pack_002(plan: PlanRow) -> ActivityPack:
    connection = "Kamsa drove Devaki and Vasudeva when the heavenly voice changed the celebration."
    return ActivityPack(
        activity_title="Build the Wedding Chariot",
        activity_type="CUT_AND_BUILD",
        send_mode="WEEKEND_PROJECT",
        estimated_minutes=25,
        parent_effort="Medium: supervise cutting and help fold the standees.",
        learning_goal="Build the central scene, then place its four events in story order.",
        story_connection=connection,
        materials=["crayons", "child-safe scissors", "glue or tape", "one small recycled box (optional)"],
        pages=[
            ActivityPage(
                page_title="Chariot cut-and-build parts",
                page_type="CUT_AND_BUILD_PARTS",
                instructions=[
                    "Color the parts before cutting.",
                    "Cut only on dotted lines; fold on solid lines.",
                    "Attach both wheels and canopy to the chariot body.",
                ],
                components=["chariot body", "two wheels", "canopy", "flower garlands"],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Standees and sequence cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Place Kamsa at the front driving; place adult Devaki and adult Vasudeva behind him.",
                    "Order the four story cards, then act out the scene.",
                ],
                components=[
                    "Devaki standee", "Vasudeva standee", "Kamsa charioteer standee",
                    "The wedding celebration", "The chariot procession",
                    "The heavenly voice", "Vasudeva protects Devaki",
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Role-play the turning point",
                page_type="ROLE_PLAY_CARDS",
                instructions=["Choose a role and speak the short line.", "Retell how Vasudeva protected Devaki."],
                components=["Narrator card", "Kamsa line", "Devaki line", "Vasudeva line"],
                story_connection=connection,
            ),
        ],
        age_variants={"ages_6_8": "Color and assemble with adult cutting help.", "ages_9_13": "Cut, fold, assemble, and retell all four events."},
        safety_note="PARENT HELP: An adult should supervise scissors. Use glue or tape carefully.",
        completion_prompt="Retell the scene: celebration, procession, heavenly voice, protection.",
        review_questions=["How did Vasudeva protect Devaki when Kamsa became afraid?"],
        answer_key=["1", "2", "3", "4"],
        parent_note="Weekend project. No peacock feathers on any character.",
        qa_requirements=["cut lines", "fold lines", "standees", "sequence cards", "role cards"],
    )


def _pack_003(plan: PlanRow) -> ActivityPack:
    connection = "Vasudeva keeps his word after the first son's birth; Kamsa is astonished and returns the child."
    return ActivityPack(
        activity_title="Truthfulness Story Path",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: read the cards and discuss the choice.",
        learning_goal="Retell the six source-bounded events and identify Vasudeva's truthful choice.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Truthfulness story path",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the six events in story order.",
                    "Draw one source-faithful detail on each card.",
                    "Circle the card showing Vasudeva's truthful choice.",
                ],
                components=[
                    "The first son is born", "Vasudeva remembers his word",
                    "Vasudeva brings the child", "Kamsa is astonished",
                    "Kamsa returns the child", "Truthfulness shines",
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Promise and duty decision tree",
                page_type="DECISION_TREE",
                instructions=[
                    "Follow each branch: keep the word, or break the word.",
                    "Mark the path Vasudeva chose.",
                    "Complete the family promise card.",
                ],
                components=["keep the word branch", "break the word branch", "family promise card"],
                story_connection=connection,
            ),
        ],
        age_variants={"ages_6_8": "Number and draw one detail on each card.", "ages_9_13": "Number each card and explain the truthful choice."},
        completion_prompt="Retell all six events, then share one promise you can keep with care.",
        review_questions=[
            "Why was keeping his word difficult for Vasudeva?",
            "What did Kamsa do after seeing Vasudeva's honesty?",
        ],
        answer_key=["1", "2", "3", "4", "5", "6"],
        parent_note="Stay inside the Story 003 boundary: no Narada, no prison, no killing of sons.",
        qa_requirements=["six sequence cards", "decision tree", "family promise", "no blank page"],
    )


def _extract_event_labels(story_text: str, seed: str) -> list[str]:
    defaults = [
        "Story begins", "A problem appears", "A helpful choice",
        "The turning point", "The result", "The lesson",
    ]
    # Prefer short phrases from seed when available
    parts = [p.strip() for p in re.split(r"[.;]", seed) if p.strip()]
    if len(parts) >= 3:
        labels = parts[:4]
        while len(labels) < 6:
            labels.append(defaults[len(labels)])
        return labels[:6]
    return defaults


def _matching_labels(plan: PlanRow) -> list[str]:
    return [
        "Main character", "Helper", "Important object", "Kind action",
        "Turning point", "Lesson", "Before", "After",
    ]


def _role_labels(plan: PlanRow) -> list[str]:
    return ["Narrator", "Main character", "Helper", "Listener", "Scene 1", "Scene 2"]


def _word_bank(plan: PlanRow) -> list[str]:
    words = ["Krishna", "prayer", "truth", "devotee", "faith", "promise"]
    for token in re.findall(r"[A-Za-z]{4,}", plan.title):
        if token.lower() not in {w.lower() for w in words}:
            words.append(token)
        if len(words) >= 8:
            break
    return words[:8]


def _parse_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Activity planner response did not contain JSON.")
        return json.loads(match.group(0))
