from __future__ import annotations

import re

from ..models import PlanRow, StoryContent

UNRELATED_PASTIMES = ("gajendra", "prahlada", "damodara", "fruit seller", "putana")


def source_fact_brief(plan: PlanRow) -> str:
    brief = (
        f"SOURCE FACT BRIEF\nSource: {plan.source_reference}\nBoundary: {plan.scripture_reference}\n"
        f"Start: {plan.start_boundary}\nEnd: {plan.end_boundary}\n"
        f"Must include: {plan.must_include}\nMust avoid: {plan.must_avoid}\n"
        "Do not invent direct quotations or cross the end boundary. Paraphrase unless a quotation is explicitly supplied."
    )
    if plan.chapter_no == "003":
        brief += (
            "\nSTORY 003 HARD BOUNDARY: Devaki and Vasudeva are not imprisoned in this episode. "
            "Do not mention a prison, cell, jail, confinement, guards, or Narada. Begin with the birth of their first son. "
            "Include these facts in both main_story and audio_script using unambiguous wording: "
            "'Vasudeva brought Kīrtimān, their first son, to Kaṁsa.' and "
            "'Kaṁsa initially returned the child, Kīrtimān, to Vasudeva.'"
        )
    if plan.chapter_no == "005":
        brief += (
            "\nSTORY 005 HARD BOUNDARY (Krishna Book Ch. 2 / SB 10.2.25–42): "
            "Devakī carries Kṛṣṇa within her womb. Invisible demigods approach, led by four-headed Brahmā and Śiva; "
            "Nārada and exalted demigods/sages may accompany. "
            "Summarize their prayers as paraphrase only—never invent verbatim quotations. "
            "Do not invent a heavenly-garden conference scene, Candra/Varuṇa/wind-god special actions, "
            "or describe prayers as a protective shield. "
            "They glorify the Lord within Devakī, reassure her, then return to their abodes. "
            "Kṛṣṇa remains unseen within Devakī. Demigods appear exalted and luminous, not ghost-like. "
            "Lord Krishna is the Supreme Protector, and the demigods offered prayers in loving surrender. "
            "FORBIDDEN in this episode: sleeping/drowsy guards, prison doors opening, Vasudeva escape, "
            "Yamunā crossing, four-armed birth appearance, Yogamāyā arriving, demigods praying to Yogamāyā, "
            "invented verbatim scripture quotations, placeholder lessons like '(3)'. "
            "Prison setting from the previous episode may be acknowledged, but do not invent guard-sleep miracles."
        )
    if plan.chapter_no == "006":
        brief += (
            "\nSTORY 006 HARD BOUNDARY (Krishna Book Ch. 3): "
            "Auspicious signs; Krishna appears in four-armed form; parents pray; He becomes an ordinary infant; "
            "chains loosen and doors open; Vasudeva prepares to carry Him. Include Chapter 3 events only. "
            "Recap Story 005 without inventing celestial gardens. "
            "Do not invent direct quotations; paraphrase prayers and speech. "
            "No peacock feather on newborn Krishna. Guards sleep when the source says they sleep. "
            "Do not show baby Krishna visible in Devakī's womb. "
            "FORBIDDEN: material from Chapter 4 (Kamsa's later persecutions), invented scripture quotations."
        )
    if plan.chapter_no == "007":
        brief += (
            "\nSTORY 007 HARD BOUNDARY (Krishna Book Ch. 4 / SB 10.4): "
            "Include in order: Yoga-māyā cries; guards tell Kaṁsa; Kaṁsa rushes; Devakī pleads; "
            "Kaṁsa attempts to destroy the child (child-safe, no gore); Yoga-māyā rises as eight-armed Durgā; "
            "she says the enemy already appeared elsewhere; Kaṁsa astonished; he releases and asks forgiveness; "
            "Vasudeva teaches bodily identification; next-day demonic ministers advise killing children born "
            "within ten days and attacking brāhmaṇas, cows, sages, Vedic culture, and Vaiṣṇavas; Kaṁsa authorizes "
            "persecution; close on offenses destroying auspiciousness. "
            "FORBIDDEN: claiming Devakī/Vasudeva remain imprisoned after release; 'every baby boy'; "
            "named demon lists not in Ch. 4; magicians/potions; invented families fleeing rivers; "
            "fabricated Kamsa dialogue quotations; absolute claims that Krishna prevents all physical suffering; "
            "Chapter 5 meeting of Nanda as main-story content."
        )
    return brief


def run_source_guard(plan: PlanRow, content: StoryContent) -> list[str]:
    errors: list[str] = []
    # Boundary checks apply to the episode narrative, not next-preview / parent notes.
    story = f"{content.recap}\n{content.main_story}\n{content.devotional_meaning}".lower()
    narration = content.audio_script.lower()
    if content.next_story_preview:
        narration = narration.replace(content.next_story_preview.lower(), " ")
    combined = f"{story}\n{narration}"
    for phrase in _items(plan.must_avoid):
        needle = phrase.lower()
        if needle in story or needle in narration:
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
        returned_terms = ("returned the child", "gave the child back", "return the child", "returned him", "returns him", "gave him back", "returned kīrtimān", "returns kīrtimān", "returned kirtiman", "returns kirtiman")
        _require(combined, returned_terms, "Story 003 must say Kaṁsa initially returns Kīrtimān.", errors)
        _require(combined, ("truthful", "truthfulness", "kept his word", "keeps his word"), "Story 003 must emphasize Vasudeva's truthfulness.", errors)
        for phrase in (
            "narada", "nārada", "imprison", "prison", "locked up", "jail", "six sons",
            "krishna was born", "krishna appeared",
        ):
            if phrase in combined:
                errors.append(f"Story 003 crosses its end boundary with later content: {phrase!r}.")
        if not any(term in narration for term in returned_terms):
            errors.append("Narration omits Story 003's ending: Kaṁsa initially returns Kīrtimān.")
        _require(combined, ("kīrtimān", "kirtiman"), "Story 003 must name the first son Kīrtimān.", errors)
        if "cousin" in combined:
            errors.append("Story 003 must call Kaṁsa Devakī's brother, not cousin.")
        if re.search(r"ka[mṁ]sa (?:was |is )?(?:also )?keeping his word", combined, re.I):
            errors.append("Story 003 must not say Kaṁsa was keeping his word.")
        if _asserts_permanent_safety(combined):
            errors.append("Story 003 must not imply the family was permanently safe.")
        if not (content.bedtime_reflection.strip().endswith("?") or any(str(q).strip().endswith("?") for q in content.think_about_it)):
            errors.append("Story 003 must include a child reflection question.")
    if plan.chapter_no == "004":
        _require(combined, ("narada", "nārada"), "Story 004 must include Nārada.", errors)
        _require(combined, ("yadu", "yadus"), "Story 004 must name the Yadu family.", errors)
        _require(combined, ("vrishni", "vṛṣṇi", "vrishnis"), "Story 004 must name the Vṛṣṇi family.", errors)
        _require(combined, ("demigods", "celestial beings"), "Story 004 must say demigods are appearing in those families.", errors)
        _require(combined, ("kālanemi", "kalanemi"), "Story 004 must identify Kaṁsa's previous identity as Kālanemi.", errors)
        _require(combined, ("imprison", "prison", "behind bars", "locked away"), "Story 004 must include the child-safe imprisonment of Devakī and Vasudeva.", errors)
        _require(combined, ("ugrasena",), "Story 004 must include Ugrasena.", errors)
        _require(combined, ("removed from the throne", "leave the throne", "removed ugrasena", "taking power from ugrasena"), "Story 004 must say Kaṁsa removes Ugrasena from power.", errors)
        _require(combined, ("remember the lord", "remembering the lord", "remember krishna", "remembering krishna", "chant krishna"), "Story 004 must show Devakī and Vasudeva remembering the Lord.", errors)
        for phrase in ("mother earth", "ocean of milk", "wedding procession", "first son", "first child", "krishna was born", "krishna's birth"):
            if phrase in combined:
                errors.append(f"Story 004 crosses its source boundary with {phrase!r}.")
        if not (content.bedtime_reflection.strip().endswith("?") or any(str(q).strip().endswith("?") for q in content.think_about_it)):
            errors.append("Story 004 must include a child reflection question.")
    if plan.chapter_no == "005":
        _require(combined, ("devaki", "devakī"), "Story 005 must center on Devakī.", errors)
        _require(combined, ("womb",), "Story 005 must keep Krishna within Devakī's womb.", errors)
        _require(combined, ("brahma", "brahmā"), "Story 005 must include Brahmā.", errors)
        _require(combined, ("shiva", "śiva", "siva"), "Story 005 must include Śiva.", errors)
        _require(combined, ("narada", "nārada"), "Story 005 must include Nārada.", errors)
        _require(combined, ("pray", "prayer", "prayers", "glorif"), "Story 005 must include demigod prayers/glorification.", errors)
        for phrase in (
            "sleeping guard",
            "drowsy guard",
            "guards dozed",
            "guards, unaware",
            "heavy-eyed",
            "prison door",
            "doors opened",
            "escape",
            "yamuna",
            "yamuṇā",
            "four-armed",
            "four armed",
            "yogamaya",
            "yogamāyā",
            "prayers to yogamaya",
            "krishna was born",
            "krishna's birth",
            "birth of lord krishna",
        ):
            if phrase in combined:
                errors.append(f"Story 005 source-boundary leakage: {phrase!r}.")
        for lesson in content.five_lessons or []:
            if re.search(r"\(\s*[345]\s*\)", str(lesson)) or "todo" in str(lesson).lower():
                errors.append(f"Story 005 has placeholder lesson text: {lesson!r}")
        if not (content.bedtime_reflection.strip().endswith("?") or any(str(q).strip().endswith("?") for q in content.think_about_it)):
            errors.append("Story 005 must include a child reflection question.")
        # Explicitly scan both main_story and audio_script for known defective phrases.
        for blob_name, blob in (("main_story", content.main_story), ("audio_script", content.audio_script)):
            low = blob.lower()
            for phrase in (
                "celestial garden",
                "heavenly garden",
                "sweet-smelling gardens",
                "shield for her and for the lord",
                "become a shield",
                "ghost-like",
                "candra",
                "varuṇa",
                "varuna",
                "wind gods",
                "moon and the wind",
                "in the of the heavenly",
                "become a , teaching",
                "the the demigods",
            ):
                if phrase in low:
                    errors.append(f"Story 005 {blob_name} contains forbidden phrase: {phrase!r}")
            if "shield" in low:
                errors.append(f"Story 005 {blob_name} must not mention a shield at all.")
            from ..content.repairs import has_invented_direct_dialogue

            if has_invented_direct_dialogue(blob, allow_heavenly_voice=False):
                # Demigod prayers must be paraphrase-only.
                if re.search(r"[\"'“].{8,160}[\"'”]", blob):
                    errors.append(f"Story 005 {blob_name} must not invent scripture-style quotations.")
        if "shield" in combined:
            errors.append("Story 005 must not use shield framing of any kind.")
    if plan.chapter_no == "006":
        _require(combined, ("four-armed", "four armed", "four arms"), "Story 006 must include Krishna's four-armed appearance.", errors)
        _require(combined, ("infant", "baby", "newborn", "child"), "Story 006 must include Krishna becoming an ordinary infant.", errors)
        _require(combined, ("chain",), "Story 006 must include chains loosening.", errors)
        lessons = [str(item).strip() for item in (content.five_lessons or []) if str(item).strip()]
        if len(lessons) != 5:
            errors.append("Story 006 must have exactly five lessons.")
        elif content.devotional_meaning.strip() and lessons and lessons[0] == content.devotional_meaning.strip():
            errors.append("Story 006 Lesson 1 must not duplicate the full Devotional Meaning.")
        if "celestial garden" in combined:
            errors.append("Story 006 recap must not invent celestial gardens from Story 005.")
        from ..content.repairs import has_invented_direct_dialogue

        for blob_name, blob in (("main_story", content.main_story), ("audio_script", content.audio_script)):
            if has_invented_direct_dialogue(blob, allow_heavenly_voice=False):
                # Allow Krishna's narrative speech paraphrase only when not quoted.
                if re.search(
                    r"\b(?:spoke|said|whispered|replied|promised|explained)\b[,:]?\s*[\"“]",
                    blob,
                    flags=re.I,
                ):
                    errors.append(f"Story 006 {blob_name} contains unsupported invented dialogue quotations.")
    if plan.chapter_no == "007":
        _require(combined, ("yoga-māyā", "yogamaya", "yoga maya", "yogamāyā"), "Story 007 must include Yoga-māyā.", errors)
        _require(combined, ("cried", "cry"), "Story 007 must include Yoga-māyā crying.", errors)
        _require(combined, ("guard",), "Story 007 must include the guards awakening/reporting.", errors)
        _require(combined, ("eight-armed", "eight armed", "eight arms"), "Story 007 must include eight-armed Durgā/Yoga-māyā.", errors)
        _require(combined, ("durgā", "durga"), "Story 007 must identify the form as Durgā.", errors)
        _require(combined, ("already", "elsewhere"), "Story 007 must say the enemy already appeared elsewhere.", errors)
        _require(combined, ("release", "released", "set free", "freed"), "Story 007 must include Kaṁsa releasing Devakī and Vasudeva.", errors)
        _require(combined, ("forgiv",), "Story 007 must include Kaṁsa asking forgiveness.", errors)
        _require(combined, ("bodily", "body", "identify"), "Story 007 must include Vasudeva's teaching on bodily identification.", errors)
        _require(combined, ("minister", "counsel", "adviser", "advisor"), "Story 007 must include Kaṁsa consulting demonic ministers.", errors)
        _require(combined, ("ten day", "ten days", "10 day", "10 days"), "Story 007 must include the ten-day newborn counsel.", errors)
        _require(combined, ("brāhmaṇa", "brahmana", "brāhmaṇas", "brahmanas"), "Story 007 must include persecution of brāhmaṇas.", errors)
        _require(combined, ("vaiṣṇava", "vaisnava", "vaiṣṇavas", "vaisnavas"), "Story 007 must include persecution of Vaiṣṇavas.", errors)
        _require(combined, ("cow",), "Story 007 must include persecution advice against cows.", errors)
        for phrase in (
            "every baby boy",
            "kill every baby",
            "remained in prison",
            "remained imprisoned",
            "still imprisoned",
            "magician",
            "potion",
            "dark chants",
            "pralamba",
            "aghasura",
            "trinavarta",
            "tṛṇāvarta",
            "mushtika",
            "dhenuka",
            "fleeing across the river",
            "fled across the river",
            "prevents all",
            "never suffer",
            "no suffering",
        ):
            if phrase in combined:
                errors.append(f"Story 007 forbidden invention or false claim: {phrase!r}.")
        # False imprisonment after release: detect "remain/stayed in prison" after release context is hard;
        # block explicit remaining-imprisoned claims.
        if re.search(r"(devak[iī].{0,40}|vasudeva.{0,40})(remain|stayed|still).{0,20}(prison|imprison)", combined):
            errors.append("Story 007 must not claim Devakī and Vasudeva remained imprisoned after release.")
        if len([x for x in (content.five_lessons or []) if str(x).strip()]) != 5:
            errors.append("Story 007 must have exactly five lessons.")
        if len([x for x in (content.think_about_it or []) if str(x).strip()]) < 5:
            errors.append("Story 007 must have exactly five reflection questions.")
        if len([x for x in (content.five_star_challenge or []) if str(x).strip()]) != 5:
            errors.append("Story 007 must have exactly five challenges.")
    return errors


def _items(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def _asserts_permanent_safety(text: str) -> bool:
    pattern = re.compile(r"(?:family|they|everyone) (?:was|were|would be) permanently safe", re.I)
    for match in pattern.finditer(text):
        clause_prefix = text[max(0, match.start() - 80):match.start()]
        if not re.search(r"\b(?:not|never|did not|didn't)\b[^.!?]{0,60}$", clause_prefix, re.I):
            return True
    return False


def _require(text: str, choices: tuple[str, ...], message: str, errors: list[str]) -> None:
    if not any(choice in text for choice in choices):
        errors.append(message)
