from __future__ import annotations

import re

from ..models import PlanRow, StoryContent

UNRELATED_PASTIMES = ("gajendra", "prahlada", "damodara", "fruit seller", "putana")


def source_fact_brief(plan: PlanRow) -> str:
    return (
        f"SOURCE FACT BRIEF\nSource: {plan.source_reference}\nBoundary: {plan.scripture_reference}\n"
        f"Start: {plan.start_boundary}\nEnd: {plan.end_boundary}\n"
        f"Must include: {plan.must_include}\nMust avoid: {plan.must_avoid}\n"
        "Do not invent direct quotations or cross the end boundary. Paraphrase unless a quotation is explicitly supplied."
    )


def run_source_guard(plan: PlanRow, content: StoryContent) -> list[str]:
    errors: list[str] = []
    story = f"{content.recap}\n{content.main_story}".lower()
    narration = content.audio_script.lower()
    combined = f"{story}\n{narration}"
    for phrase in _items(plan.must_avoid):
        if phrase.lower() in combined:
            errors.append(f"Source boundary violation: forbidden later/unrelated event {phrase!r}.")
    for pastime in UNRELATED_PASTIMES:
        if pastime in combined and pastime not in plan.summary_seed.lower() and pastime not in plan.must_include.lower():
            errors.append(f"Unrelated pastime appears outside the selected source boundary: {pastime}.")
    if plan.chapter_no == "001":
        _require(combined, ("earth", "bhumi", "bhūmi"), "Story 001 must identify Bhumi/Mother Earth.", errors)
        _require(combined, ("cow",), "Story 001 must say Bhumi assumes the form of a cow.", errors)
        _require(combined, ("brahma", "brahmā"), "Story 001 must include Lord Brahma.", errors)
        _require(combined, ("ocean of milk", "milk ocean"), "Story 001 must include the Ocean of Milk.", errors)
        _require(combined, ("within brahma's heart", "within his heart", "in brahma's heart"), "Story 001 must say Brahma receives the message within his heart.", errors)
        _require(combined, ("son of vasudeva", "vasudeva's son"), "Story 001 must say the Lord will appear as the son of Vasudeva.", errors)
        if re.search(r"[\"'“].{0,120}(born|birth).{0,40}(vrindavan|vṛndāvana)", combined, re.I | re.S):
            errors.append("Story 001 must not invent a direct quotation promising birth in Vrindavana.")
    if plan.chapter_no == "002":
        _require(combined, ("devaki's brother", "brother kamsa", "her brother"), "Story 002 must call Kamsa Devaki's brother.", errors)
        _require(combined, ("son of ugrasena", "son of king ugrasena", "ugrasena's son"), "Story 002 must identify Kamsa as the son of Ugrasena.", errors)
        _require(combined, ("drove the chariot", "took the reins", "personally drive", "personally drove"), "Story 002 must say Kamsa personally drives the chariot.", errors)
        _require(combined, ("eighth child", "eighth son"), "Story 002 must mention Devaki's eighth child.", errors)
        if "cousin" in combined:
            errors.append("Story 002 must call Kamsa Devaki's brother, not cousin.")
    if plan.chapter_no == "003":
        _require(combined, ("first son", "first child"), "Story 003 must include the birth of the first son.", errors)
        _require(combined, ("brought", "bring"), "Story 003 must show Vasudeva bringing the child to Kamsa.", errors)
        _require(combined, ("returned the child", "gave the child back", "return the child", "returned him", "returns him", "gave him back"), "Story 003 must say Kamsa initially returns the child.", errors)
        _require(combined, ("truthful", "truthfulness", "kept his word", "keeps his word"), "Story 003 must emphasize Vasudeva's truthfulness.", errors)
        for phrase in ("narada", "nārada", "imprison", "six sons", "krishna was born", "krishna appeared"):
            if phrase in combined:
                errors.append(f"Story 003 crosses its end boundary with later content: {phrase!r}.")
        if not any(term in narration for term in ("returned the child", "gave the child back", "return the child", "returned him", "returns him", "gave him back")):
            errors.append("Narration omits Story 003's ending: Kamsa initially returns the child.")
    return errors


def _items(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def _require(text: str, choices: tuple[str, ...], message: str, errors: list[str]) -> None:
    if not any(choice in text for choice in choices):
        errors.append(message)
