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
    DecisionNode,
    MatchingCard,
    PrintablePart,
    RolePlayCard,
    SequenceCard,
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
            "004": _pack_004,
            "005": _pack_005,
            "006": _pack_006,
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
        connection = f"Every printable piece comes from the central scene of {title}."
        seed = (plan.summary_seed or title).strip()
        if kind == "STORY_SEQUENCE":
            events = _extract_event_labels(story_text, seed)
            cards = [
                SequenceCard(event=label, drawing_prompt=f"Draw one detail from: {label}", source_order=index + 1)
                for index, label in enumerate(events)
            ]
            printed = _shuffled_sequence_cards(cards, seed)
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
                        components=printed,
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
                answer_key=[card.event for card in sorted(cards, key=lambda item: item.source_order)],
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
                activity_title=f"Act the Central Scene of {title}",
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
                        instructions=["Draw the central story moment.", "Write one sentence about the kind choice."],
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
                        components=["start", "checkpoint 1", "checkpoint 2", "central moment", "kind choice", "finish"],
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
                    instructions=["Fill the three story boxes: beginning, central moment, lesson."],
                    components=["beginning box", "central moment box", "lesson box"],
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
                components=[
                    "chariot body", "two wheels", "canopy", "flower garlands",
                    "Devaki standee", "Vasudeva standee", "Kamsa charioteer standee",
                ],
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
                    SequenceCard("The heavenly voice", "Draw the startling message.", 3),
                    SequenceCard("The wedding celebration", "Draw joyful garlands and music.", 1),
                    SequenceCard("Vasudeva protects Devaki", "Draw Vasudeva shielding Devaki.", 4),
                    SequenceCard("The chariot procession", "Draw the chariot on the road.", 2),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Role-play the chariot scene",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role.",
                    "Use the paraphrase lines (not invented quotations).",
                    "Retell how Vasudeva protected Devaki.",
                ],
                components=[
                    "Narrator: A heavenly voice warns Kamsa about Devaki's eighth child.",
                    "Kamsa (paraphrase): Fear rises as he hears the warning about the eighth child.",
                    "Vasudeva (paraphrase): He calmly promises to bring every child and asks Kamsa not to harm Devaki.",
                    "Devaki (paraphrase): She stays close to Vasudeva and trusts his truthful promise.",
                ],
                story_connection=connection,
            ),
        ],
        age_variants={"ages_6_8": "Color and assemble with adult cutting help.", "ages_9_13": "Cut, fold, assemble, and retell all four events."},
        safety_note="PARENT HELP: An adult should supervise scissors. Use glue or tape carefully.",
        completion_prompt="Retell the scene: celebration, procession, heavenly voice, protection.",
        review_questions=["How did Vasudeva protect Devaki when Kamsa became afraid?"],
        answer_key=[
            "The wedding celebration",
            "The chariot procession",
            "The heavenly voice",
            "Vasudeva protects Devaki",
        ],
        parent_note="Weekend project. No peacock feathers. Role lines are paraphrase only—not scripture quotations.",
        qa_requirements=["cut lines", "fold lines", "named standee characters", "sequence cards", "paraphrase role cards"],
    )


def _pack_003(plan: PlanRow) -> ActivityPack:
    connection = "Vasudeva keeps his word after Kīrtimān's birth; Kaṁsa is astonished and returns the child, but Vasudeva remains cautious."
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
                    SequenceCard("Kaṁsa says he fears the eighth child.", "Draw Kaṁsa speaking without violence.", 5),
                    SequenceCard("Kīrtimān is born.", "Draw the peaceful newborn with Devakī and Vasudeva.", 1),
                    SequenceCard("Kaṁsa returns Kīrtimān.", "Draw Vasudeva carefully receiving Kīrtimān.", 6),
                    SequenceCard("Vasudeva remembers his promise.", "Draw Vasudeva thinking carefully.", 2),
                    SequenceCard("Kaṁsa is astonished by Vasudeva’s honesty.", "Draw Kaṁsa looking surprised.", 4),
                    SequenceCard("Vasudeva brings Kīrtimān to Kaṁsa.", "Draw the careful journey to the palace.", 3),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Promise and duty decision tree",
                page_type="DECISION_TREE",
                instructions=[
                    "Follow each branch and choose truthfulness with wise help.",
                    "Mark the path Vasudeva chose, then discuss when to ask a trusted adult.",
                    "Good and safe promises should be kept. If a promise could hurt someone, asks you to hide an unsafe secret, or makes you frightened, tell a trusted adult.",
                ],
                components=[DecisionNode(
                    "Is this promise good and safe?",
                    ["Yes — keep it honestly", "No or unsure — tell a trusted adult"],
                    "Safety comes first; never hide an unsafe secret—tell a trusted adult.",
                )],
                story_connection=connection,
            ),
        ],
        age_variants={"ages_6_8": "Number and draw one detail on each card.", "ages_9_13": "Number each card and explain the truthful choice."},
        completion_prompt="Retell all six events, then share one promise you can keep with care.",
        review_questions=[
            "Why was keeping his word difficult for Vasudeva?",
            "What did Kamsa do after seeing Vasudeva's honesty?",
        ],
        answer_key=[
            "Kīrtimān is born.",
            "Vasudeva remembers his promise.",
            "Vasudeva brings Kīrtimān to Kaṁsa.",
            "Kaṁsa is astonished by Vasudeva’s honesty.",
            "Kaṁsa says he fears the eighth child.",
            "Kaṁsa returns Kīrtimān.",
        ],
        parent_note="Stay inside the Story 003 boundary: no Narada, no prison, no killing of sons.",
        qa_requirements=["six sequence cards", "decision tree", "family promise", "no blank page"],
    )


def _pack_004(plan: PlanRow) -> ActivityPack:
    connection = "Nārada warns Kaṁsa, fear drives harsh choices, and Devakī and Vasudeva remain faithful to the Lord."
    return ActivityPack(
        activity_title="Fear and Faith Mini-Drama",
        activity_type="MINI_DRAMA",
        send_mode="PARENT_GUIDED",
        estimated_minutes=22,
        parent_effort="Low: help children read the role cards and discuss strong feelings.",
        learning_goal="Retell the source-bounded turning points and compare fearful choices with faithful composure.",
        story_connection=connection,
        materials=["pencil", "five simple household props"],
        pages=[
            ActivityPage(
                "Role cards", "ROLE_PLAY_CARDS",
                ["Choose roles.", "Read each short line and perform the action gently."],
                [
                    RolePlayCard("Nārada", "The divine plan is unfolding among the Yadu and Vṛṣṇi families.", "Speak calmly to Kaṁsa.", "small scarf"),
                    RolePlayCard("Kaṁsa", "Fear is filling my mind, and I am choosing control.", "Show alarm without shouting.", "paper crown"),
                    RolePlayCard("Devakī", "We will remain composed and remember the Lord.", "Stand peacefully beside Vasudeva.", "flower"),
                    RolePlayCard("Vasudeva", "Even here, let us keep faith and act with dignity.", "Offer a reassuring gesture.", "folded cloth"),
                    RolePlayCard("Narrator", "Kaṁsa removed Ugrasena from power and imprisoned the devoted couple.", "Move the scene-order cards.", "story cards"),
                ], story_connection=connection,
            ),
            ActivityPage(
                "Scene-order cards", "STORY_SEQUENCE_CARDS",
                ["Number the shuffled cards from 1 to 6.", "Retell the episode without adding later events."],
                [
                    SequenceCard("Ugrasena is removed from rule.", "Draw an empty royal seat.", 5),
                    SequenceCard("Nārada arrives.", "Draw Nārada entering calmly.", 1),
                    SequenceCard("The devotees remain faithful.", "Draw Devakī and Vasudeva remembering the Lord.", 6),
                    SequenceCard("Kaṁsa becomes fearful.", "Draw Kaṁsa looking alarmed.", 3),
                    SequenceCard("Nārada explains the divine plan.", "Draw a respectful conversation.", 2),
                    SequenceCard("Devakī and Vasudeva are imprisoned.", "Draw them composed in a simple room.", 4),
                ], story_connection=connection,
            ),
            ActivityPage(
                "Fear versus faith emotion map", "EMOTION_MAP",
                ["Draw one sign of fear on the left and one sign of faith on the right.", "Write how Devakī and Vasudeva stayed composed.", "Name a trusted adult who helps when fear feels too large."],
                ["How can remembering the Lord and asking a trusted adult help when you feel afraid?"],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Act with short lines and simple props.",
            "ages_9_13": "Add one narrator sentence explaining fear versus faith.",
        },
        completion_prompt="Perform the three scenes, then share one faithful response to fear.",
        review_questions=["Which choices came from fear?", "How did the devotees respond differently?"],
        answer_key=[
            "Nārada arrives.",
            "Nārada explains the divine plan.",
            "Kaṁsa becomes fearful.",
            "Devakī and Vasudeva are imprisoned.",
            "Ugrasena is removed from rule.",
            "The devotees remain faithful.",
        ],
        parent_note="Keep imprisonment child-safe and stop before later sons or Krishna’s birth.",
        qa_requirements=["five complete role cards", "six shuffled scene cards", "emotion map", "no raw JSON", "no blank page"],
    )


def _pack_005(plan: PlanRow) -> ActivityPack:
    connection = (
        "Brahma, Shiva, Narada, and the demigods invisibly approach Devaki and offer prayers "
        "while Krishna remains unseen within her."
    )
    sequence = [
        SequenceCard(
            "Krishna remains unseen within Devaki.",
            "Draw soft light around Devaki without showing a separate sky form of Krishna.",
            1,
        ),
        SequenceCard(
            "Brahma, Shiva, Narada, and the demigods arrive invisibly.",
            "Draw the demigods approaching with reverence.",
            2,
        ),
        SequenceCard(
            "They offer obeisances to the Lord.",
            "Draw folded hands and bowed heads.",
            3,
        ),
        SequenceCard(
            "They praise Him as true to His vow and the Supreme Truth.",
            "Draw prayerful voices and calm faces.",
            4,
        ),
        SequenceCard(
            "They ask Him to protect devotees and reassure Devaki.",
            "Draw Devaki receiving courage.",
            5,
        ),
        SequenceCard(
            "They return to their heavenly homes.",
            "Draw the demigods departing upward in peace.",
            6,
        ),
    ]
    printed = [
        sequence[2],
        sequence[0],
        sequence[4],
        sequence[1],
        sequence[5],
        sequence[3],
    ]
    return ActivityPack(
        activity_title="The Secret Prayer Gathering",
        activity_type="MATCHING_GAME",
        send_mode="SEND_NOW",
        estimated_minutes=20,
        parent_effort="Low: help younger children match and cut if needed.",
        learning_goal="Name who came to pray, order the prayer scene, and offer a personal lotus prayer.",
        story_connection=connection,
        materials=["pencil or crayons", "child-safe scissors (optional)"],
        pages=[
            ActivityPage(
                page_title="Who Came to Pray?",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each figure to why they came.",
                    "Younger path: draw lines or cut-and-match.",
                    "Older path: write one reason each figure came.",
                ],
                components=[
                    MatchingCard("Brahma", "leads the prayer gathering", "who", pair_id="A"),
                    MatchingCard("Shiva", "joins and offers prayers", "who", pair_id="B"),
                    MatchingCard("Narada", "comes as a great sage and devotee", "who", pair_id="C"),
                    MatchingCard("other demigods", "offer respectful prayers", "who", pair_id="D"),
                    MatchingCard("Devaki", "carries Krishna unseen within her", "who", pair_id="E"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the Prayer Scene in Order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "The six cards are shuffled on purpose.",
                    "Number them in true story order.",
                    "Do not look for an answer key on the page.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="My Lotus Prayer",
                page_type="PRAYER_WHEEL",
                instructions=[
                    "Younger: draw inside each lotus petal.",
                    "Older: write one or two sentences in each petal.",
                    "Family: discuss one chosen petal together.",
                ],
                components=[
                    PrintablePart("Someone I want Krishna to protect", cut_line=True, fold_line=False, assembly_instruction="Place on a petal."),
                    PrintablePart("A fear I can place before Krishna", cut_line=True, fold_line=False, assembly_instruction="Place on a petal."),
                    PrintablePart("Something I am thankful for", cut_line=True, fold_line=False, assembly_instruction="Place on a petal."),
                    PrintablePart("One kind action I will do", cut_line=True, fold_line=False, assembly_instruction="Place on a petal."),
                    PrintablePart("A prayer for the world", cut_line=True, fold_line=False, assembly_instruction="Place on a petal."),
                ],
                story_connection=connection,
                layout_hint="five_lotus_petals",
            ),
        ],
        age_variants={
            "ages_6_8": "draw lines or cut-and-match.",
            "ages_9_13": "write one reason for each match.",
        },
        safety_note="PARENT HELP: An adult should supervise child-safe scissors if cutting.",
        completion_prompt="Share one lotus petal prayer with your family.",
        review_questions=[
            "Who led the demigods in prayer?",
            "Where did Krishna remain during the prayers?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note="Keep the scene before Krishna's birth; Krishna stays unseen within Devaki.",
        qa_requirements=[
            "three meaningful pages",
            "shuffled sequence cards",
            "no generic placeholders",
            "younger and older paths",
            "answers only in manifest",
        ],
    )


def _pack_006(plan: PlanRow) -> ActivityPack:
    connection = (
        "This activity follows Krishna Book Chapter 3: auspicious signs, Krishna's four-armed appearance, "
        "the parents' prayers, His infant form, and the prison doors opening so Vasudeva can carry Him."
    )
    sequence = [
        SequenceCard(
            "Auspicious signs appeared as the sacred night approached.",
            "Draw gentle signs of a holy night around the prison.",
            1,
        ),
        SequenceCard(
            "Krishna appeared before Devaki and Vasudeva in His four-armed form.",
            "Draw the Lord with four arms, shining with kindness.",
            2,
        ),
        SequenceCard(
            "Devaki and Vasudeva offered prayers.",
            "Draw the parents praying with folded hands.",
            3,
        ),
        SequenceCard(
            "Krishna assumed the form of an ordinary infant.",
            "Draw a soft newborn Krishna without a peacock feather.",
            4,
        ),
        SequenceCard(
            "Vasudeva's chains loosened and the prison doors opened.",
            "Draw chains falling away while guards sleep.",
            5,
        ),
        SequenceCard(
            "Vasudeva prepared to carry Krishna according to the Lord's arrangement.",
            "Draw Vasudeva gently holding baby Krishna.",
            6,
        ),
    ]
    printed = [
        sequence[3],
        sequence[0],
        sequence[4],
        sequence[1],
        sequence[5],
        sequence[2],
    ]
    return ActivityPack(
        activity_title="The Sacred Night of Krishna's Birth",
        activity_type="STORY_SEQUENCE",
        send_mode="SEND_NOW",
        estimated_minutes=18,
        parent_effort="Low: help younger children number the cards.",
        learning_goal="Put the birth-night events in true order and notice Krishna's kindness.",
        story_connection=connection,
        materials=["pencil or crayons"],
        pages=[
            ActivityPage(
                page_title="Put the Birth Night in Order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "The six cards are shuffled on purpose.",
                    "Number them in true story order.",
                    "Do not look for an answer key on the page.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Who Was There?",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each person to their part in the pastime.",
                    "Younger path: draw lines.",
                    "Older path: write one sentence for each match.",
                ],
                components=[
                    MatchingCard("Devaki", "receives Lord Krishna with love", "who", pair_id="A"),
                    MatchingCard("Vasudeva", "carries Krishna by the Lord's arrangement", "who", pair_id="B"),
                    MatchingCard("Krishna", "appears and then becomes a baby", "who", pair_id="C"),
                    MatchingCard("the prison", "opens when Krishna arranges it", "where", pair_id="D"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Family Courage Prayer",
                page_type="FAMILY_MISSION",
                instructions=[
                    "Talk about one fear your family can place before Krishna.",
                    "Younger path: draw a calm night scene.",
                    "Older path: write two sentences of gratitude.",
                ],
                components=[
                    "One fear we can give to Krishna",
                    "One way Krishna protects devotees",
                    "One kind action we will do tomorrow",
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "number cards and draw one birth-night detail.",
            "ages_9_13": "explain why Vasudeva obeyed Krishna's arrangement.",
        },
        safety_note="PARENT HELP: Keep scissors away unless an adult is supervising craft extras.",
        completion_prompt="Share one way Krishna brings light into difficult places.",
        review_questions=[
            "In what form did Krishna first appear?",
            "What happened to Vasudeva's chains?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note="Keep the scene inside Chapter 3; do not include Kamsa's later persecutions.",
        qa_requirements=[
            "three meaningful pages",
            "shuffled sequence cards",
            "no frontmatter metadata events",
            "younger and older paths",
            "answers only in manifest",
        ],
    )


def _extract_event_labels(story_text: str, seed: str) -> list[str]:
    from .qa import GENERIC_PLACEHOLDERS, is_metadata_event_label

    labels: list[str] = []
    # Prefer Main Story body so YAML frontmatter / greetings never become sequence cards.
    body = story_text or ""
    main_match = re.search(
        r"(?is)(?:^|\n)#+\s*Main Story\s*\n(.*?)(?=\n#+\s|\Z)",
        body,
    )
    if main_match:
        body = main_match.group(1)
    for chunk in re.split(r"[.!?\n]+", body):
        cleaned = " ".join(chunk.strip().split())
        if cleaned.startswith("#"):
            cleaned = cleaned.lstrip("#").strip()
        if len(cleaned) < 12:
            continue
        if is_metadata_event_label(cleaned):
            continue
        if cleaned.lower() in GENERIC_PLACEHOLDERS:
            continue
        labels.append(cleaned[:110])
        if len(labels) >= 6:
            break

    if len(labels) < 4:
        parts = [p.strip() for p in re.split(r"[.;]", seed or "") if len(p.strip()) >= 8]
        for part in parts:
            if part.lower() in GENERIC_PLACEHOLDERS:
                continue
            if part.lower() not in {item.lower() for item in labels}:
                labels.append(part[:110])
            if len(labels) >= 6:
                break

    if len(labels) < 4:
        tokens = [t for t in re.findall(r"[A-Za-z]{4,}", f"{seed} {story_text[:800]}")]
        unique: list[str] = []
        for token in tokens:
            low = token.lower()
            if low in GENERIC_PLACEHOLDERS or low in {item.lower() for item in unique}:
                continue
            unique.append(token)
        titleish = (seed or story_text or "this pastime").strip()[:60] or "this pastime"
        synthesized = [
            f"Opening moment of {titleish}",
            f"Challenge faced in {titleish}",
            f"Faithful response in {titleish}",
            f"Protective action in {titleish}",
            f"Peaceful result in {titleish}",
            f"Family takeaway from {titleish}",
        ]
        for phrase in synthesized:
            if phrase.lower() not in GENERIC_PLACEHOLDERS and phrase.lower() not in {item.lower() for item in labels}:
                labels.append(phrase)
            if len(labels) >= 6:
                break
        for index in range(0, max(0, len(unique) - 1), 2):
            phrase = f"{unique[index]} {unique[index + 1]} in the pastime"
            if phrase.lower() in GENERIC_PLACEHOLDERS:
                continue
            if phrase.lower() not in {item.lower() for item in labels}:
                labels.append(phrase)
            if len(labels) >= 6:
                break

    if len(labels) < 4:
        raise ValueError("Could not extract concrete story event labels without generic placeholders.")

    # Pad to 6 by cycling through the already-extracted labels (freeze base length;
    # len(labels) % len(labels) would always be 0 and only duplicate labels[0]).
    base_count = len(labels)
    pad_index = 0
    while len(labels) < 6:
        labels.append(f"{labels[pad_index % base_count]} continues in the pastime")
        pad_index += 1
    return labels[:6]


def _shuffled_sequence_cards(cards: list[SequenceCard], seed: str) -> list[SequenceCard]:
    import random

    ordered = list(cards)
    rng = random.Random(seed or "krishna-story")
    for _ in range(8):
        rng.shuffle(ordered)
        chronological = [card.event for card in sorted(cards, key=lambda item: item.source_order)]
        printed = [card.event for card in ordered]
        if printed != chronological:
            return ordered
    # Deterministic swap fallback
    if len(ordered) >= 2:
        ordered[0], ordered[1] = ordered[1], ordered[0]
    return ordered


def _matching_labels(plan: PlanRow) -> list[str]:
    title = plan.title or "this pastime"
    return [
        f"Lead figure in {title}",
        f"Companion in {title}",
        f"Sacred object in {title}",
        f"Courageous action in {title}",
        f"Change moment in {title}",
        f"Devotional lesson in {title}",
        f"Earlier moment in {title}",
        f"Later moment in {title}",
    ]


def _role_labels(plan: PlanRow) -> list[str]:
    title = plan.title or "this pastime"
    return [
        "Narrator",
        f"Lead from {title}",
        f"Companion from {title}",
        "Listener",
        f"First scene of {title}",
        f"Second scene of {title}",
    ]


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
