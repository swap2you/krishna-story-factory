"""Deterministic source-text repairs for known defective packages.

These repairs are applied during manual rebuild staging. They do not call paid APIs.
"""
from __future__ import annotations

import re
from dataclasses import replace

from ..models import StoryContent


def repair_story_002_dialogue(content: StoryContent) -> StoryContent:
    """Replace invented sentimental dialogue with clearly marked paraphrase."""
    main = content.main_story
    main = main.replace(
        'Devaki squeezed Vasudeva\'s hand. "Thank you for saving my life," she whispered, her voice trembling but grateful. '
        'Vasudeva comforted her, whispering, "We must trust in Krishna\'s plan, even when it is hard to see."',
        "Devaki held Vasudeva's hand with quiet gratitude. "
        "In paraphrase: she thanked him for protecting her, and he gently reminded her to trust Krishna's plan "
        "even when the path was hard to see.",
    )
    main = re.sub(
        r'He said, with calm strength, ["“]Dear Kamsa, today is a day of blessings and family\. Please, do not bring harm to your sister\. The voice said your danger is from her eighth child, not from Devaki herself\. You have nothing to fear from her at this moment\.["”]',
        "Vasudeva spoke with calm strength. In paraphrase: he asked Kamsa not to harm his sister on their wedding day, "
        "reminding him that the warning spoke of Devaki's eighth child, not of Devaki herself.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r'Vasudeva, full of faith, made a solemn promise: ["“]Have no fear\. I will give you every child born to us\. If you trust my word, you need not harm Devaki\. My honesty has never failed you\.["”]',
        "Vasudeva, full of faith, made a solemn promise. In paraphrase: he vowed to bring every child born to them, "
        "asking Kamsa to trust his truthfulness and spare Devaki.",
        main,
        flags=re.I,
    )
    audio = content.audio_script
    for old, new in (
        (
            '"Thank you for saving my life,"',
            "(paraphrase) thanking him for protecting her,",
        ),
        (
            '"We must trust in Krishna\'s plan, even when it is hard to see."',
            "(paraphrase) trusting Krishna's plan even when it is hard to see.",
        ),
    ):
        audio = audio.replace(old, new)
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
    return replace(
        content,
        main_story=main,
        audio_script=audio,
        bedtime_prayer=prayer,
        bedtime_reflection=content.bedtime_reflection or "What helps you stay truthful when you feel afraid?",
        five_lessons=lessons[:5],
        think_about_it=list(content.think_about_it or content.recall_questions or [])[:5]
        or [
            "Who drove the chariot for Devaki and Vasudeva?",
            "What did the heavenly voice warn Kamsa about?",
            "How did Vasudeva protect Devaki?",
        ],
        greeting=content.greeting or "Hare Kṛṣṇa, dear children and families!",
        story_number=content.story_number or "002",
        story_format="v2",
    )


def repair_story_005_philosophy(content: StoryContent) -> StoryContent:
    """Remove invented garden conference, quotations, and 'shield for the Lord' wording."""
    main = content.main_story
    main = re.sub(
        r"Far above the earth, in the sweet-smelling gardens of the heavenly planets, a meeting was called by Lord Brahmā,[^.]*\.",
        "Far above the earth, four-headed Lord Brahmā and Lord Śiva gathered with exalted demigods and sages in a solemn assembly of devotion.",
        main,
        flags=re.I,
    )
    main = main.replace(
        "Brahmā’s lotus-seated throne floated among clouds. He called to others, “Come, let us go to the earth. It is time to offer our prayers to the Lord, who has chosen to appear.” Great demigods and sages gathered.",
        "Four-headed Brahmā, seated in serene majesty upon his lotus seat, led the demigods to approach the earth unseen. "
        "In paraphrase: he invited the exalted assembly to offer prayers to the Lord who had chosen to appear within Devakī.",
    )
    main = re.sub(
        r"Even Indra, king of rain, came, as well as Candra, the Moon-god, and Varuṇa, ruler of the cosmic waters\.\s*",
        "Indra and other exalted demigods came with them, shining with dignity rather than any ghost-like appearance. ",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"One by one, the demigods began to glorify Lord Krishna\. ['‘]You are the supreme protector,['’] they prayed silently\. ['‘]Though You are everywhere, You now stay within the womb to delight Your dear devotees and destroy all fear\.['’]",
        "One by one, the demigods silently glorified Lord Krishna. In paraphrase: they praised Him as the supreme protector "
        "who stays within Devakī's womb to delight His devotees and remove fear, while remaining the Lord of all worlds.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"Brahmā offered his respects, reflecting how the Lord was the source of his own power\. ['‘]You are never touched by suffering or fear, yet You kindly come for us,['’] Brahmā prayed\.",
        "Four-headed Brahmā offered respects, remembering that the Lord is the source of his power. "
        "In paraphrase: Brahmā praised the Lord who is untouched by suffering yet kindly comes for His devotees.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"Nārada played a soft melody, his fingers gently strumming the strings\. He smiled, remembering all the ways the Lord cared for everyone, calling, ['‘]You are the shelter for all who take Your name!['’]",
        "Nārada played a soft melody on his vina. In paraphrase: he praised the Lord as the shelter of everyone who remembers His name with love.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"Indra asked for forgiveness for any mistakes and begged for the Lord’s protection\. The Moon and the wind gods brought sweetness and soothing air\. All prayed that Devakī would be protected, so that Lord Krishna could appear safely in the world\.",
        "The demigods prayed humbly for Devakī's courage and for the Lord's appearance in His own time. "
        "They did not invent special moon-god or wind-god miracles; their glory was simply sincere devotion before the Lord.",
        main,
        flags=re.I,
    )
    main = re.sub(
        r"Though words could not be heard, a message of reassurance touched her heart\. ['‘]Do not be afraid\.\s*You are blessed\. All the worlds rejoice, for soon the Supreme Lord will take birth from you\.['’]",
        "Though words could not be heard, a message of reassurance touched her heart. "
        "In paraphrase: she felt blessed and understood that the worlds rejoiced because the Supreme Lord would soon appear from her.",
        main,
        flags=re.I | re.S,
    )
    main = main.replace(
        "Their bodies glimmered like little flashes of moonlight",
        "Their exalted forms shone with gentle, luminous dignity",
    )
    # Keep Format V2 length after surgical edits.
    if len(main.split()) < 700:
        main = (
            f"{main.strip()}\n\n"
            "Throughout this quiet visit, Krishna remained unseen within Devakī. "
            "The demigods never claimed to protect the Lord Himself, because the Lord is the supreme protector. "
            "Their prayers comforted Devakī, strengthened her faith, and filled the prison cell with hope until they returned to their own abodes."
        )
    meaning = content.devotional_meaning.replace(
        "The loving prayers of the demigods become a shield for her and for the Lord, teaching us that sincere devotion can bring protection and peace, no matter our situation.",
        "The loving prayers of the demigods comfort Devakī and teach us that sincere devotion brings peace, "
        "while the Lord Himself remains the supreme protector who needs no shield.",
    )
    audio = content.audio_script
    for phrase in (
        "celestial gardens",
        "heavenly gardens",
        "sweet-smelling gardens",
        "shield for her and for the Lord",
    ):
        audio = re.sub(re.escape(phrase), "", audio, flags=re.I)
    audio = re.sub(r"\bCandra\b|\bVaruṇa\b|\bVaruna\b|wind gods", "the demigods", audio, flags=re.I)
    audio = re.sub(r"\s{2,}", " ", audio)
    return replace(content, main_story=main, audio_script=audio, devotional_meaning=meaning)


def repair_story_006_content(content: StoryContent) -> StoryContent:
    """Fix recap, duplicated lesson, invented quotation, and regenerate concise lessons."""
    recap = content.recap
    recap = re.sub(
        r"gathered in celestial gardens to offer their prayers",
        "came unseen to offer their prayers",
        recap,
        flags=re.I,
    )
    main = content.main_story
    main = re.sub(
        r'Vasudeva softly spoke,\s*["“][^"”]+["”]',
        "Vasudeva offered soft prayers. In paraphrase: he thanked the Supreme Lord for appearing and asked for protection from fear and sadness.",
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
    if content.devotional_meaning.strip() and content.five_lessons and content.five_lessons[0].strip() == content.devotional_meaning.strip():
        pass
    audio = content.audio_script
    audio = re.sub(
        r"gathered in celestial gardens to offer their prayers",
        "came unseen to offer their prayers",
        audio,
        flags=re.I,
    )
    audio = re.sub(
        r'Vasudeva softly spoke,\s*["“][^"”]+["”]',
        "Vasudeva offered soft paraphrased prayers of gratitude.",
        audio,
        flags=re.I,
    )
    # Align audio lesson list with concise repaired lessons when the duplicated block is present.
    if "Five lessons for tonight" in audio or "Five lessons for tonight:" in audio:
        lesson_block = "Five lessons for tonight: <break time=\"1.0s\" />\n" + "\n".join(
            f"{idx}. {lesson} <break time=\"1.0s\" />" for idx, lesson in enumerate(lessons, start=1)
        )
        audio = re.sub(
            r"Five lessons for tonight:.*?(?=Dear Lord Krishna|Next time:)",
            lesson_block + "\n\n",
            audio,
            flags=re.I | re.S,
        )
    return replace(
        content,
        recap=recap,
        main_story=main,
        audio_script=audio,
        five_lessons=lessons,
    )


def apply_known_story_repairs(chapter_no: str, content: StoryContent) -> StoryContent:
    chapter = (chapter_no or "").strip().zfill(3)
    if chapter == "002":
        return repair_story_002_dialogue(content)
    if chapter == "005":
        return repair_story_005_philosophy(content)
    if chapter == "006":
        return repair_story_006_content(content)
    return content


__all__ = [
    "apply_known_story_repairs",
    "repair_story_002_dialogue",
    "repair_story_005_philosophy",
    "repair_story_006_content",
]
