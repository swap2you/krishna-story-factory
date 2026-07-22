"""Deterministic source-text repairs for known defective packages.

Repairs use Unicode-normalized matching. They do not call paid APIs.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import replace

from ..models import StoryContent

_INVENTED_DIALOGUE_VERBS = (
    "spoke",
    "said",
    "whispered",
    "replied",
    "promised",
    "explained",
    "declared",
    "muttered",
    "called",
    "told",
)


def normalize_story_text(text: str) -> str:
    """NFKC normalize and unify curly quotes/apostrophes for robust matching."""
    cleaned = unicodedata.normalize("NFKC", text or "")
    trans = str.maketrans(
        {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u00a0": " ",
        }
    )
    return cleaned.translate(trans)


def _strip_comment_markers(value: str) -> str:
    text = (value or "").replace("<!--", "").replace("-->", "").strip()
    return text


def sanitize_content_fields(content: StoryContent) -> StoryContent:
    """Remove accidental HTML comment markers and leaked section headings from fields."""

    def _clean_block(value: str) -> str:
        text = _strip_comment_markers(value or "")
        text = re.split(r"(?im)^##\s+(?:Audio Narration|Poster Visual Brief|Coloring Visual Brief|Activity Data|Parent/Teacher Note|Next Story Preview)\s*$", text, maxsplit=1)[0]
        return text.strip()

    think = [_strip_comment_markers(q) for q in (content.think_about_it or []) if _strip_comment_markers(q)]
    challenge = [_strip_comment_markers(q) for q in (content.five_star_challenge or []) if _strip_comment_markers(q)]
    lessons = [_strip_comment_markers(q) for q in (content.five_lessons or []) if _strip_comment_markers(q)]
    return replace(
        content,
        think_about_it=think,
        five_star_challenge=challenge,
        five_lessons=lessons,
        next_story_preview=_clean_block(content.next_story_preview),
        parent_note=_clean_block(content.parent_note or content.parent_notes),
        bedtime_prayer=_clean_block(content.bedtime_prayer),
        bedtime_reflection=_clean_block(content.bedtime_reflection),
        poster_visual_brief=_clean_block(content.poster_visual_brief),
        coloring_visual_brief=_clean_block(content.coloring_visual_brief),
        audio_script=_strip_comment_markers(content.audio_script),
        main_story=_strip_comment_markers(content.main_story),
    )


def has_invented_direct_dialogue(text: str, *, allow_heavenly_voice: bool = False) -> bool:
    """True when unsupported spoken dialogue appears as quotation."""
    normalized = normalize_story_text(text)
    if allow_heavenly_voice:
        # Strip the known heavenly-voice prophecy pattern before scanning.
        normalized = re.sub(
            r'"Kamsa[^"]{0,160}eighth[^"]{0,80}"',
            " ",
            normalized,
            flags=re.I,
        )
    for verb in _INVENTED_DIALOGUE_VERBS:
        if re.search(rf'\b{verb}\b[,:]?\s*"', normalized, flags=re.I):
            return True
        if re.search(rf'"[^"]{{8,160}}"\s*,?\s*(?:{verb}|he|she)\b', normalized, flags=re.I):
            # quotation before speech attribution still counts as dialogue
            if verb in {"said", "whispered", "muttered", "declared", "replied", "promised", "explained", "called"}:
                return True
    # Direct sentimental gratitude / trust lines regardless of attribution.
    forbidden = (
        r"thank you for (?:saving|protecting) my life",
        r"we must trust in krishna.?s plan",
        r"we will trust krishna.?s plan",
        r"trust in krishna.?s plan, even when it is hard to see",
    )
    low = normalized.lower()
    return any(re.search(pat, low) for pat in forbidden)


def assert_story_002_audio_clean(audio: str) -> list[str]:
    """Post-repair assertions for Story 002 audio narration."""
    errors: list[str] = []
    text = normalize_story_text(audio or "")
    low = text.lower()
    if re.search(r"1\.0s\"\s*/>", text) or re.search(r"(?<!<break time=\")1\.0s\"\s*/>", text):
        errors.append("broken break fragment")
    if "1.0s\" />" in text or '1.0s" />' in text:
        errors.append("orphaned break remnant")
    if re.search(r"\b(?:he muttered|she whispered)\b", low):
        errors.append("dangling speech attribution")
    if "he smiled and told her, in paraphrase" in low:
        errors.append("incomplete attribution clause")
    if has_invented_direct_dialogue(text, allow_heavenly_voice=True):
        # Heavenly voice prophecy may remain quoted; human sentimental dialogue must not.
        if re.search(r"thank you for (?:saving|protecting)", low) or re.search(
            r"we (?:must|will) trust(?: in)? krishna", low
        ):
            errors.append("forbidden sentimental quotation")
    for frag in ("he muttered", "she whispered", "told her, in paraphrase"):
        if frag in low:
            errors.append(f"incomplete fragment: {frag}")
    # Rough incomplete sentence: trailing attribution without period before next break.
    if re.search(r"in paraphrase,[^.<\n]{0,80}\b(?:he|she)\s+(?:muttered|whispered)\b", low):
        errors.append("incomplete paraphrase sentence")
    return errors


_STORY_002_AUDIO = """Hare Kṛṣṇa, dear children and families! Tonight is Story 002: The Wedding and the Heavenly Voice.

In the ancient city of Mathurā, there was once a celebration more joyful than any before. Lanterns glowed at every doorway, marigold garlands hung from the palace, and sweet music floated through the evening air. Why all this happiness? Because it was the wedding of Princess Devakī and the noble Prince Vasudeva!

Children tossed fragrant flower petals in front of the happy couple. Devakī sparkled in her silk sari, and Vasudeva greeted everyone with kindness and calm. Families gave their blessings as cheerful dancers twirled. Sweets were shared, making the festival even brighter.

Devakī's brother Kaṁsa, the powerful son of King Ugrasena, personally drove the gleaming royal chariot, wanting everyone to see how much he cared for his sister. As the newlyweds rode through the city, everyone clapped and rang bells, sending the couple off with wishes for happiness.

But just then, a strange stillness settled over the road. Suddenly, a deep and powerful voice thundered from the sky. No person was speaking; it was as though the heavens themselves had come alive. In paraphrase of the heavenly warning: Kaṁsa was told that Devakī's eighth child would bring his destruction.

People gasped. Kaṁsa's hands shook. His happiness vanished in an instant, replaced by fear. He looked at Devakī and forgot his affection as a loving brother. Kaṁsa reached for his sword, and some in the crowd watched in disbelief and worry.

But Vasudeva was brave and loving. He stepped between Devakī and Kaṁsa. In paraphrase: Vasudeva calmly asked Kaṁsa not to harm his sister on their wedding day, reminding him that the warning spoke of a future eighth child, not of Devakī herself.

Still, Kaṁsa was afraid. In paraphrase: he worried about what might happen later if he let them go.

Vasudeva took a deep breath. In paraphrase: he promised to bring every child born to them and asked Kaṁsa to trust his truthfulness and spare Devakī.

For a long moment, Kaṁsa was silent. He saw Vasudeva's honesty and finally put away his sword. The chariot moved on, and though the city cheered again, the joy felt softer now. Devakī held Vasudeva's hand with quiet gratitude. In paraphrase: she thanked him for protecting her, and he gently reminded her to trust Krishna's plan even when the path was hard to see.

As the sun set and the city shimmered with tiny lamps, the couple remembered the heavenly voice and prayed quietly for courage. Inside, they knew Krishna was already watching over them.

So, as you snuggle under your covers, remember—when something scary happens, you can be brave and truthful, just like Devakī and Vasudeva. Krishna will always help you through every challenge, just as He watched over them in Mathurā.

Dear Kṛṣṇa, please keep us close to You. We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night.

Next time: Story 003 — Vasudeva Keeps His Word. We will see how truthfulness guides a difficult promise."""


def repair_story_002_dialogue(content: StoryContent) -> StoryContent:
    """Repair Story 002 main and fully rewrite audio from the approved source boundary."""
    content = sanitize_content_fields(content)
    main = normalize_story_text(content.main_story)

    # Structural main-story paraphrase cleanup (Unicode-normalized; idempotent).
    main = re.sub(
        r"Devaki squeezed Vasudeva'?s hand\.\s*"
        r'"Thank you for (?:saving|protecting) my life,"\s*she whispered[^.]{0,80}\.\s*'
        r"Vasudeva comforted her, whispering,\s*"
        r"\"We (?:must|will) trust(?: in)? Krishna'?s plan[^\"]*\"",
        "Devaki held Vasudeva's hand with quiet gratitude. "
        "In paraphrase: she thanked him for protecting her, and he gently reminded her to trust Krishna's plan "
        "even when the path was hard to see.",
        main,
        flags=re.I | re.S,
    )
    main = re.sub(
        r'"Thank you for (?:saving|protecting) my life,"[^.]{0,120}\.',
        "In paraphrase: Devaki thanked Vasudeva for protecting her.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"\"We (?:must|will) trust(?: in)? Krishna'?s plan[^\"]*\"",
        "In paraphrase: Vasudeva reminded her to trust Krishna's plan even when it is hard to see.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r'He said, with calm strength,\s*"[^"]+"',
        "Vasudeva spoke with calm strength. In paraphrase: he asked Kamsa not to harm his sister on their wedding day, "
        "reminding him that the warning spoke of Devaki's eighth child, not of Devaki herself.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r'Vasudeva, full of faith, made a solemn promise:\s*"[^"]+"',
        "Vasudeva, full of faith, made a solemn promise. In paraphrase: he vowed to bring every child born to them, "
        "asking Kamsa to trust his truthfulness and spare Devaki.",
        main,
        flags=re.I,
    )

    audio = _STORY_002_AUDIO.strip()
    audio_errors = assert_story_002_audio_clean(audio)
    if audio_errors:
        raise ValueError("Story 002 audio rewrite failed validation: " + "; ".join(audio_errors))

    prayer = (content.bedtime_prayer or content.bedtime_reflection or "").strip()
    if "hare k" not in prayer.lower():
        prayer = (
            "Dear Kṛṣṇa, please keep us close to You. We chant: "
            "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
            "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. "
            "Good night, and may Your protection rest gently on our hearts."
        )
    lessons = list(content.five_lessons or [])
    if len(lessons) < 5:
        lessons = [
            "Celebrate family with gratitude and respect.",
            "Listen carefully when a warning arrives.",
            "Truthfulness can protect those we love.",
            "Courage means staying calm in sudden fear.",
            "Trust Krishna's plan even when it is hard to see.",
        ]
    think = [q for q in (content.think_about_it or []) if q and "<!--" not in q][:5]
    if len(think) < 3:
        think = [
            "Who drove the chariot for Devaki and Vasudeva?",
            "What did the heavenly voice warn Kamsa about?",
            "How did Vasudeva protect Devaki?",
            "When you feel afraid, how can calm words and prayer help you?",
            "What does truthfulness look like in your family?",
        ]
    challenge = [q for q in (content.five_star_challenge or []) if q and "<!--" not in q][:5]
    if len(challenge) < 5:
        challenge = [
            "Think of a time you felt worried—talk to a parent or friend about it calmly.",
            "Try to listen carefully to someone's feelings, just like Vasudeva listened to Kamsa.",
            "Make a simple flower garland at home and imagine you're decorating for a wedding.",
            "Draw what you think a heavenly voice might look or sound like.",
            "Say a prayer for courage before bedtime, asking Krishna for help with any fears.",
        ]
    poster = content.poster_visual_brief.strip() or (
        "Wedding chariot scene: adult Devaki and Vasudeva seated behind Kamsa the charioteer, "
        "flower garlands, soft evening light, no peacock feathers, no frightening violence."
    )
    coloring = content.coloring_visual_brief.strip() or (
        "Devotional Krishna coloring page from The Wedding and the Heavenly Voice. "
        "Devaki and Vasudeva in a decorated chariot, Kamsa driving, simple Mathura arch, "
        "large colorable spaces, thick outlines, no weapons."
    )
    preview = content.next_story_preview.strip() or (
        "Next time: Story 003 — Vasudeva Keeps His Word. We will see how truthfulness guides a difficult promise."
    )
    parent = content.parent_note.strip() or (
        "Source: Krishna Book Chapter 1. Discuss why people sometimes act from fear, and how honesty and calm faith "
        "help families respond wisely. Keep the mood gentle and age-appropriate."
    )
    return replace(
        content,
        main_story=main,
        audio_script=audio,
        bedtime_prayer=prayer,
        bedtime_reflection=content.bedtime_reflection or "What helps you stay truthful when you feel afraid?",
        five_lessons=lessons[:5],
        think_about_it=think[:5],
        five_star_challenge=challenge[:5],
        next_story_preview=preview,
        parent_note=parent,
        poster_visual_brief=poster,
        coloring_visual_brief=coloring,
        greeting=content.greeting or "Hare Kṛṣṇa, dear children and families!",
        story_number=content.story_number or "002",
        story_format="v2",
    )


_STORY_005_MAIN = """In the deep silence of the royal prison, where lamps flickered through dark shadows, Devakī sat quietly. Within her heart, she felt a gentle warmth. Lord Krishna Himself had entered her womb, filling her with a peaceful light that no guard or wall could ever hide.

The secret grew and grew. News of this marvelous event spread not from person to person, but through the hearts of those who could see beyond the material world. Far above the earth, four-headed Lord Brahmā and Lord Śiva gathered with exalted demigods and sages in a solemn assembly of devotion.

Four-headed Brahmā, seated in serene majesty upon his lotus seat, led the demigods to approach the earth unseen. In paraphrase: he invited the exalted assembly to offer prayers to the Lord who had chosen to appear within Devakī.

Some softly whispered holy mantras. Indra and other exalted demigods came with them, shining with luminous dignity. The wise Nārada was already there, carrying sweet music on his vina and the news in his heart.

Without being seen or heard by anyone in Mathurā, the demigods descended. Their gentle feet did not stir the dust nor cause any rustle. Inside the small cell, the air shimmered for an instant as the heavenly hosts arrived, hidden from human eyes.

Devakī could sense something extraordinary. Her heart beat gently as if cradled by a quiet blessing. The demigods gazed with deep love and gratitude toward the Lord residing in her womb.

Although cramped and dark, the prison cell was suddenly filled with a delicate fragrance. In their subtle forms, the demigods bowed down and the sages folded their hands in prayer.

One by one, the demigods silently glorified Lord Krishna. In paraphrase: they praised Him as the supreme protector who stays within Devakī's womb to delight His devotees and remove fear, while remaining the Lord of all worlds.

Four-headed Brahmā offered respects, remembering that the Lord is the source of his power. In paraphrase: Brahmā praised the Lord who is untouched by suffering yet kindly comes for His devotees. Śiva, with his matted hair and gentle smile, offered praise from his heart, marveling at Kṛṣṇa's mercy.

Nārada played a soft melody on his vina. In paraphrase: he praised the Lord as the shelter of everyone who remembers His name with love.

The demigods prayed humbly for Devakī's courage and for the Lord's appearance in His own time. Their glory was simply sincere devotion before the Lord, not invented miracles of moon-gods or wind-gods.

Their praises were soft but filled the room. Even Devakī, her head bowed, felt her worries melt away. The prison cell seemed less damp and tight; a gentle light seemed to shine within her mind.

After praying, the heavenly beings encouraged Devakī. Though words could not be heard, a message of reassurance touched her heart. In paraphrase: she felt blessed and understood that the worlds rejoiced because the Supreme Lord would soon appear from her.

Brahmā, Śiva, Nārada, and the other demigods offered one last respectful bow. Their exalted forms shone with gentle, luminous dignity, and soon they disappeared from the cell, returning to their heavenly homes above. The prayers hung in the air, soft as silk, and Devakī felt surrounded by hope, though bars and stone still held her in prison.

Within Devakī's gentle heart, Lord Krishna, unseen and glowing, listened to the prayers meant for Him. Though all was still outside, inside her womb the source of all joy and love was waiting for His perfect moment to appear.

The prison returned to its nightly silence, but the cell now felt like a temple. Devakī and Vasudeva quietly remembered the wondrous prayers, their hearts full of faith. They did not invent miracles or try to leave the cell. They simply stayed close to Krishna in remembrance.

The prayers of the demigods and the silent courage of Devakī glowed in the night, showing how, even in the darkest times, Krishna's loving protection and wisdom are always near. Throughout this quiet visit, Krishna remained unseen within Devakī. The demigods never claimed to protect the Lord Himself, because the Lord is the supreme protector. Their prayers comforted Devakī, strengthened her faith, and filled the prison cell with hope until they returned to their own abodes."""


_STORY_005_AUDIO = """Hare Kṛṣṇa, dear children and families! Tonight is Story 005: Prayers by the Demigods for Lord Krishna in the Womb.

Last time, we heard how Nārada Muni warned the cruel king Kaṁsa that a special child would appear to end his wickedness. Kaṁsa imprisoned Devakī and Vasudeva, yet they kept remembering the Lord. Now, in that lonely prison cell, something wonderful happens in secret.

Lord Krishna had entered Devakī's womb, filling her with peaceful light. Far above the earth, four-headed Lord Brahmā and Lord Śiva gathered with exalted demigods and sages. In paraphrase, Brahmā led them to approach the earth unseen and offer prayers to the Lord within Devakī.

Indra and other luminous demigods came with them. Nārada was already there with his vina. Unseen by anyone in Mathurā, they entered the prison cell. The demigods bowed and silently glorified Lord Krishna. In paraphrase, they praised Him as the supreme protector who remains the Lord of all worlds even while staying within Devakī.

Four-headed Brahmā remembered that the Lord is the source of his power. Śiva offered praise from the heart. Nārada praised the Lord as the shelter of those who remember His name. They prayed for Devakī's courage and for the Lord's appearance in His own time.

A message of reassurance touched Devakī's heart. In paraphrase, she felt blessed because the worlds rejoiced that the Supreme Lord would soon appear. Then the demigods returned to their homes. Krishna remained unseen within Devakī. The demigods never claimed to protect the Lord Himself, for the Lord is the supreme protector. Their prayers comforted Devakī and filled the night with hope.

Five lessons for tonight: 1. Even in darkness, remembering Krishna brings hope and light. 2. Great souls always praise the Lord and seek His blessings. 3. Offering humble prayers strengthens faith and courage. 4. Faith and courage can grow stronger when we trust Krishna. 5. Krishna hears all prayers, even those spoken softly in the heart.

Dear Krishna, thank You for tonight's secret prayers with Brahmā, Śiva, Nārada, and the demigods. Please protect Devakī's courage in our hearts and keep our family close to You. We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night, dear Krishna.

Next time: Story 006. On a sacred night filled with wonder and quiet faith, the Supreme Lord appears in Mathurā."""


def repair_story_005_philosophy(content: StoryContent) -> StoryContent:
    """Rewrite Story 005 main and audio from the approved source boundary."""
    content = sanitize_content_fields(content)
    meaning = (
        "This story reveals how even when all seems lost, the Lord and His loving helpers are always near. "
        "The demigods, though great and powerful, are humble before Krishna and offer praise. "
        "Devakī teaches courage and trust. The prayers comfort Devakī and teach sincere devotion. "
        "Lord Krishna is the Supreme Protector, and the demigods offered prayers in loving surrender."
    )
    poster = (
        "Four-headed Brahmā leads luminous exalted demigods in prayer around Devakī in prison; "
        "Krishna remains unseen within Devakī; no ghost-like figures; no open doors; no sleeping-guard miracles."
    )
    coloring = (
        "Simple Bal Gopal-friendly coloring: Devakī seated peacefully in a soft prison cell while "
        "four-headed Brahmā and gentle demigods offer prayers; large open spaces; no baby visible in the womb; "
        "luminous not ghost-like faces; thick outlines."
    )
    return replace(
        content,
        main_story=_STORY_005_MAIN.strip(),
        audio_script=_STORY_005_AUDIO.strip(),
        recap=re.sub(
            r"(?i)celestial gardens|heavenly gardens|sweet-smelling gardens",
            "a solemn heavenly assembly",
            content.recap or (
                "Last time, Nārada warned Kaṁsa, and Devakī and Vasudeva were imprisoned. "
                "Now demigods come unseen to offer prayers while Krishna remains within Devakī."
            ),
        ),
        next_story_preview=(
            content.next_story_preview.strip()
            if content.next_story_preview.strip()
            and "birth of lord krishna" not in content.next_story_preview.lower()
            else "Next time: Story 006 — on a sacred night filled with wonder, the Supreme Lord appears in Mathurā."
        ),
        bedtime_prayer=(
            content.bedtime_prayer.strip()
            or (
                "Dear Krishna, thank You for tonight's secret prayers with Brahmā, Śiva, Nārada, and the demigods. "
                "Please protect Devakī's courage in our hearts and keep our family close to You. We chant: "
                "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare. "
                "Good night, dear Krishna."
            )
        ),
        think_about_it=[
            q
            for q in (content.think_about_it or [])
            if q and "<!--" not in q and "birth of lord krishna" not in q.lower()
        ]
        or [
            "Why did the demigods come to offer prayers while Krishna was within Devakī?",
            "How can quiet prayer help when a place feels dark or frightening?",
            "What does it mean that Krishna is the supreme protector?",
            "How did Devakī show courage and trust?",
            "What prayer will your family offer tonight?",
        ],
        parent_note=(
            content.parent_note.strip()
            or (
                "Source: Krishna Book Chapter 2. Emphasize paraphrase-only demigod prayers, "
                "Krishna as supreme protector, and a calm prison setting without birth-night miracles."
            )
        ),
        poster_visual_brief=poster,
        coloring_visual_brief=coloring,
        five_lessons=[
            "Even in darkness, remembering Krishna brings hope and light.",
            "Great souls always praise the Lord and seek His blessings.",
            "Offering humble prayers strengthens faith and courage.",
            "Faith and courage can grow stronger when we trust Krishna.",
            "Krishna hears all prayers, even those spoken softly in the heart.",
        ],
        story_number=content.story_number or "005",
        story_format="v2",
        greeting=content.greeting or "Hare Kṛṣṇa, dear children and families!",
        devotional_meaning=meaning,
    )


def repair_story_006_content(content: StoryContent) -> StoryContent:
    """Fix recap, duplicated lesson, invented quotation, and concise lessons."""
    content = sanitize_content_fields(content)
    recap = re.sub(
        r"(?i)gathered in celestial gardens to offer their prayers",
        "came unseen to offer their prayers",
        content.recap or "",
    )
    main = normalize_story_text(content.main_story)
    # Generic invented dialogue patterns for human speakers (keep narrative paraphrase).
    main = re.sub(
        r'\b(?:Vasudeva|Devaki|Devakī)\b[^.!?]{0,40}\b(?:spoke|said|whispered|replied|promised|explained)\b[,:]?\s*"[^"]+"',
        "In paraphrase, the devotees offered loving prayers and received the Lord's arrangement with faith.",
        main,
        flags=re.I,
    )
    lessons = [
        "Even in dark places, Krishna's love can shine.",
        "Faithful parents remember the Lord with courage.",
        "Divine arrangements open paths when Krishna wills.",
        "Trust Krishna when the next step feels uncertain.",
        "Remember the Lord's appearance with a grateful heart.",
    ]
    audio = normalize_story_text(content.audio_script)
    audio = re.sub(
        r"(?i)gathered in celestial gardens to offer their prayers",
        "came unseen to offer their prayers",
        audio,
    )
    audio = re.sub(
        r'Vasudeva softly spoke,\s*"[^"]+"',
        "Vasudeva offered soft paraphrased prayers of gratitude.",
        audio,
        flags=re.I,
    )
    if "Five lessons for tonight" in audio or "Five lessons for tonight:" in audio:
        lesson_block = 'Five lessons for tonight: <break time="1.0s" />\n' + "\n".join(
            f'{idx}. {lesson} <break time="1.0s" />' for idx, lesson in enumerate(lessons, start=1)
        )
        audio = re.sub(
            r"Five lessons for tonight:.*?(?=Dear Lord Krishna|Next time:)",
            lesson_block + "\n\n",
            audio,
            flags=re.I | re.S,
        )
    poster = content.poster_visual_brief.strip() or (
        "Midnight prison: Krishna appears in four-armed form with conch, disc, club, and lotus before Devakī and Vasudeva; "
        "guards asleep or absent; no peacock feather on newborn; soft golden light."
    )
    coloring = content.coloring_visual_brief.strip() or (
        "Simple ages 4–8 coloring of Krishna's birth night: gentle four-armed form or soft infant without peacock feather; "
        "asleep guards or none; large open spaces; thick outlines; birth-specific prison scene."
    )
    return replace(
        content,
        recap=recap,
        main_story=main,
        audio_script=audio,
        five_lessons=lessons,
        poster_visual_brief=poster,
        coloring_visual_brief=coloring,
        story_number=content.story_number or "006",
        story_format="v2",
    )


# Story 003 closing-fact signatures (semantic dedup; Unicode-normalized matching).
SIG_VASUDEVA_TRUTHFUL_DELIVERY = "VASUDEVA_TRUTHFUL_DELIVERY"
SIG_KAMSA_ASTONISHED_HONESTY = "KAMSA_ASTONISHED_HONESTY"
SIG_WARNING_EIGHTH_CHILD = "WARNING_EIGHTH_CHILD"
SIG_KAMSA_RETURNS_CHILD = "KAMSA_RETURNS_CHILD"

_STORY_003_SIGNATURES = (
    SIG_VASUDEVA_TRUTHFUL_DELIVERY,
    SIG_KAMSA_ASTONISHED_HONESTY,
    SIG_WARNING_EIGHTH_CHILD,
    SIG_KAMSA_RETURNS_CHILD,
)

# Natural bedtime coda — closing-fact summary sentences after this are bolted on.
_STORY_003_CODA_RE = re.compile(
    r"trusted in Krishna|steady,?\s+honest love|practice when a promise is hard|"
    r"never assuming they were safe|watched and waited",
    re.I,
)


def _normalize_sentence_for_classify(text: str) -> str:
    cleaned = normalize_story_text(text)
    cleaned = re.sub(r"<break\s+time=\"[^\"]+\"\s*/>", " ", cleaned, flags=re.I)
    cleaned = cleaned.lower()
    cleaned = cleaned.replace("ī", "i").replace("ṁ", "m").replace("ā", "a")
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def classify_story_003_fact_sentence(sentence: str) -> set[str]:
    """Classify didactic closing-fact summary sentences (not mid-story narration)."""
    norm = _normalize_sentence_for_classify(sentence)
    if not norm:
        return set()
    found: set[str] = set()

    # Closing delivery restatement: brought Kirtiman to Kamsa because of truthfulness/duty.
    if re.search(
        r"\bbrought\b.*\bkirtiman\b.*\bkamsa\b.*\b(?:truthfulness|duty)\b",
        norm,
    ) or re.search(
        r"\bcommitted to truthfulness and duty\b",
        norm,
    ):
        found.add(SIG_VASUDEVA_TRUTHFUL_DELIVERY)

    if re.search(r"\bastonish\w*\b.*\b(?:honesty|honest)\b", norm) or re.search(
        r"\b(?:honesty|honest)\b.*\bastonish\w*\b",
        norm,
    ):
        found.add(SIG_KAMSA_ASTONISHED_HONESTY)

    if re.search(r"\b(?:warning|prophecy)\b.*\bconcern\w*\b.*\beighth\b", norm) or re.search(
        r"\bbecause the warning concerned the eighth\b",
        norm,
    ):
        found.add(SIG_WARNING_EIGHTH_CHILD)

    if re.search(r"\b(?:initially\s+)?returned\b.*\b(?:the\s+)?(?:child|kirtiman)\b", norm) or re.search(
        r"\breturned kirtiman\b",
        norm,
    ):
        # Only count return when this is a closing restatement (often with astonish/warning).
        if found or re.search(r"\b(?:astonish|honesty|warning|at least for now)\b", norm):
            found.add(SIG_KAMSA_RETURNS_CHILD)

    return found


def count_story_003_fact_signatures(text: str) -> dict[str, int]:
    """Count closing-fact signature occurrences across sentences."""
    counts = {sig: 0 for sig in _STORY_003_SIGNATURES}
    for sentence in _split_story_sentences(text):
        for sig in classify_story_003_fact_sentence(sentence):
            counts[sig] += 1
    return counts


def _split_story_sentences(text: str) -> list[str]:
    blob = normalize_story_text(text or "").strip()
    if not blob:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=(?:<break\b|[A-Z\"“‘]|$))", blob)
    return [p.strip() for p in parts if p.strip()]


def dedupe_story_003_fact_sentences(text: str) -> str:
    """Keep the first closing-fact summary for each signature; drop later duplicates and post-coda bolts."""
    sentences = _split_story_sentences(text)
    coda_idx: int | None = None
    for index, sentence in enumerate(sentences):
        if _STORY_003_CODA_RE.search(sentence):
            coda_idx = index
            break

    seen: set[str] = set()
    kept: list[str] = []
    for index, sentence in enumerate(sentences):
        sigs = classify_story_003_fact_sentence(sentence)
        if sigs:
            # Bolted summary after the natural bedtime coda — remove.
            if coda_idx is not None and index > coda_idx:
                continue
            # Later duplicate of already-stated closing facts.
            if sigs <= seen:
                continue
            seen |= sigs
        kept.append(sentence)

    result = " ".join(kept)
    result = re.sub(r" {2,}", " ", result).strip()
    return result


def _replace_placeholder_lessons(lessons: list[str], replacements: list[str]) -> list[str]:
    """Replace Remember Krishna (N) placeholders while keeping real lessons."""
    out: list[str] = []
    rep_idx = 0
    for lesson in lessons or []:
        text = (lesson or "").strip()
        if re.search(r"remember k[rṛ][sṣ][nṇ]a with love\s*\(\s*[345]\s*\)", text, flags=re.I) or re.search(
            r"\(\s*[345]\s*\)\s*$", text
        ):
            if rep_idx < len(replacements):
                out.append(replacements[rep_idx])
                rep_idx += 1
            continue
        if text:
            out.append(text)
    while len(out) < 5 and rep_idx < len(replacements):
        out.append(replacements[rep_idx])
        rep_idx += 1
    return out[:5]


def repair_story_001_lessons(content: StoryContent) -> StoryContent:
    content = sanitize_content_fields(content)
    lessons = _replace_placeholder_lessons(
        list(content.five_lessons or []),
        [
            "Brahma carries the Earth's prayer to the Lord with humility and care.",
            "Hope grows when we remember Krishna even before we see the answer.",
            "Caring for others is a prayer that Krishna gladly hears.",
        ],
    )
    prayer = (content.bedtime_prayer or content.bedtime_reflection or "").strip()
    if "hare k" not in prayer.lower():
        prayer = (
            "Dear Krishna, thank You for hearing Mother Earth's prayer. "
            "Please help our family pray with hope and care for others. "
            "We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
            "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night."
        )
    return replace(
        content,
        five_lessons=lessons,
        bedtime_prayer=prayer,
        bedtime_reflection=prayer,
        story_number=content.story_number or "001",
    )


def repair_story_004_lessons(content: StoryContent) -> StoryContent:
    content = sanitize_content_fields(content)
    lessons = _replace_placeholder_lessons(
        list(content.five_lessons or []),
        [
            "Fear can push harsh choices, but faith keeps hearts steady.",
            "Remembering Krishna gives courage when surroundings feel dark.",
            "Devotees stay composed by keeping the Lord in their hearts.",
        ],
    )
    prayer = (content.bedtime_prayer or content.bedtime_reflection or "").strip()
    if "hare k" not in prayer.lower():
        prayer = (
            "Dear Krishna, thank You for Nārada's warning and for the faith of Devakī and Vasudeva. "
            "Please keep our family calm and close to You when fear feels strong. "
            "We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
            "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night."
        )
    return replace(
        content,
        five_lessons=lessons,
        bedtime_prayer=prayer,
        bedtime_reflection=prayer,
        story_number=content.story_number or "004",
    )


def repair_story_003_dedup(content: StoryContent) -> StoryContent:
    """Remove duplicated closing fact blocks while keeping required Story 003 events."""
    content = sanitize_content_fields(content)
    main = dedupe_story_003_fact_sentences(normalize_story_text(content.main_story))
    audio = dedupe_story_003_fact_sentences(normalize_story_text(content.audio_script))
    # Idempotent guarantee for callers.
    main = dedupe_story_003_fact_sentences(main)
    audio = dedupe_story_003_fact_sentences(audio)
    prayer = (content.bedtime_prayer or content.bedtime_reflection or "").strip()
    if "hare k" not in prayer.lower():
        prayer = (
            "Dear Krishna, thank You for Vasudeva's truthful courage with baby Kīrtimān. "
            "Please help our family keep honest promises and stay close to You. "
            "We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
            "Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night."
        )
    lessons = _replace_placeholder_lessons(
        list(content.five_lessons or []),
        [
            "Truthfulness is practiced most clearly when a promise is hard.",
            "Stay careful and wise even after a moment of relief.",
            "Trust Krishna while keeping your word with courage.",
        ],
    )
    return replace(
        content,
        main_story=main,
        audio_script=audio,
        bedtime_prayer=prayer,
        bedtime_reflection=prayer,
        five_lessons=lessons,
        story_number=content.story_number or "003",
    )


def apply_known_story_repairs(chapter_no: str, content: StoryContent) -> StoryContent:
    chapter = (chapter_no or "").strip().zfill(3)
    content = sanitize_content_fields(content)
    if chapter == "001":
        return repair_story_001_lessons(content)
    if chapter == "002":
        return repair_story_002_dialogue(content)
    if chapter == "003":
        return repair_story_003_dedup(content)
    if chapter == "004":
        return repair_story_004_lessons(content)
    if chapter == "005":
        return repair_story_005_philosophy(content)
    if chapter == "006":
        return repair_story_006_content(content)
    if chapter == "007":
        return repair_story_007_chapter4(content)
    return content


def repair_story_007_chapter4(content: StoryContent) -> StoryContent:
    """Replace failed Story 007 packages with locked Krishna Book Chapter 4 content."""
    from .story_007_locked import build_story_007_locked

    locked = build_story_007_locked()
    return replace(
        locked,
        title=content.title or locked.title,
        source_reference=content.source_reference or locked.source_reference,
        scripture_reference=content.scripture_reference or locked.scripture_reference,
        age_range=content.age_range or locked.age_range,
    )


__all__ = [
    "SIG_KAMSA_ASTONISHED_HONESTY",
    "SIG_KAMSA_RETURNS_CHILD",
    "SIG_VASUDEVA_TRUTHFUL_DELIVERY",
    "SIG_WARNING_EIGHTH_CHILD",
    "apply_known_story_repairs",
    "assert_story_002_audio_clean",
    "classify_story_003_fact_sentence",
    "count_story_003_fact_signatures",
    "dedupe_story_003_fact_sentences",
    "has_invented_direct_dialogue",
    "normalize_story_text",
    "repair_story_001_lessons",
    "repair_story_002_dialogue",
    "repair_story_003_dedup",
    "repair_story_004_lessons",
    "repair_story_005_philosophy",
    "repair_story_006_content",
    "repair_story_007_chapter4",
    "sanitize_content_fields",
]
