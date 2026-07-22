"""Locked, source-faithful Story 007 package (Krishna Book Chapter 4 / SB 10.4).

Do not treat prior failed Story 007 packages as source truth.
"""

from __future__ import annotations

from ..models import PlanRow, StoryContent

HARE_KRISHNA = (
    "Hare Krishna, Hare Krishna, Krishna Krishna, Hare Hare, "
    "Hare Rama, Hare Rama, Rama Rama, Hare Hare."
)


def build_story_007_locked(plan: PlanRow | None = None) -> StoryContent:
    title = (plan.title if plan else None) or "Kamsa Begins His Persecutions"
    source = (plan.source_reference if plan else None) or "Krishna Book Chapter 4"
    scripture = (plan.scripture_reference if plan else None) or "Śrīmad-Bhāgavatam 10.4"

    recap = (
        "Previously, in The Birth of Lord Krishna, Lord Kṛṣṇa appeared in the prison of Mathurā before "
        "Devakī and Vasudeva. Following the Lord's arrangement, Vasudeva carried baby Kṛṣṇa through the "
        "night to Gokula, left Him with Yaśodā, and brought Yoga-māyā back to the prison. The doors and "
        "chains returned to their places, and the guards did not understand what had happened. Tonight we "
        "hear the next chapter: what followed when Yoga-māyā cried and Kaṁsa rushed in."
    )

    main_story = """\
Night still rested over Mathurā when Vasudeva finished the Lord's secret arrangement. He had carried baby Kṛṣṇa to Gokula and returned with Yoga-māyā, the Lord's own internal potency appearing as a newborn girl. The prison doors closed again. The chains returned. For a moment the stone room seemed almost ordinary.

Then Yoga-māyā began to cry.

Her cry was sharp enough to wake the guards. They sat up, confused and alarmed. They had not expected another birth cry at that hour. Afraid of Kaṁsa's anger if they delayed, they hurried from the prison and reported that a child had appeared.

Kaṁsa's heart was already restless from the old prophecy about Devakī's eighth child. Hearing the guards' report, he rushed toward the prison. Torchlight shook along the walls as he came. Fear made his steps quick and hard.

Inside, Devakī held the baby girl close. Seeing Kaṁsa's face, she pleaded for mercy. She asked him to spare the child and reminded him that the baby was a girl, not the son he feared. Her voice was full of a mother's love, but Kaṁsa's fear was louder than her gentle request.

In a harsh and frightened mood, Kaṁsa took the child and tried to destroy her. The pastime is solemn, and we speak of it carefully for children: he intended a terrible act against the newborn girl. At that very moment, by the Lord's arrangement, the baby slipped from his hands. Before everyone's eyes she rose into the sky.

There Yoga-māyā revealed her glorious form, shining with divine power and appearing with eight arms like Durgā. The prison courtyard, so recently filled with fear, became filled with awe. Devakī and Vasudeva looked up with reverence. Kaṁsa stared upward, astonished.

From the sky she addressed him. In paraphrase, not as an invented quotation: she told Kaṁsa that the enemy he feared had already taken birth elsewhere, and that his attempt against her could not stop the Lord's plan. Then she disappeared from that place.

Kaṁsa stood shaken. The sight and the message struck his pride and his terror at once. For a short time his heart softened. He released Devakī and Vasudeva from the prison and asked their forgiveness for the cruel way he had treated them. In that moment it seemed he might turn toward a better path.

Vasudeva spoke with calm wisdom. He explained that people become enemies when they identify too strongly with the body and forget the eternal soul. Temporary anger, fear, and bodily pride darken the heart. When a person thinks only, "This body is me," enmity grows easily. Hearing this, Kaṁsa appeared repentant for a while.

But lasting purity needs more than a single soft feeling. The next day Kaṁsa called his demonic ministers and asked what he should do. Bad association quickly pulled his mind back toward fear and violence. Those ministers did not encourage forgiveness or remembrance of the Lord. They fed his anxiety.

They advised him to search out and kill newborn children born within the previous ten days. They also urged him to attack brāhmaṇas, cows, sages, Vedic culture, and Vaiṣṇavas, because these support the worship of Lord Viṣṇu. In their dark counsel, anything connected to the Lord's service became a target.

Listening to that wicked advice, Kaṁsa authorized the persecution. The peaceful order of Mathurā was threatened by offenses against saintly persons and devotees. What had begun as temporary regret ended again in harm, because Kaṁsa kept company with those who hated Viṣṇu and His servants.

Dear children, this chapter is sober. It does not teach that remembering Kṛṣṇa removes every difficulty at once, or that devotees never face pain in this world. It teaches that offenses against brāhmaṇas, cows, sages, and Vaiṣṇavas destroy auspiciousness. It teaches that bad association can undo a soft moment of repentance. And it teaches that Lord Kṛṣṇa remains the supreme shelter for those who remember Him with faith, even when powerful people choose fear.

So the cry of Yoga-māyā opened the next chapter of the Lord's pastimes. Kaṁsa saw Durgā's warning, released the devotee parents for a time, heard Vasudeva's wisdom, and then fell again under demonic counsel. The heart that keeps bad company loses its auspicious light. The heart that honors the Lord's devotees walks toward shelter."""

    meaning = (
        "Kaṁsa shows how fear and bodily identification can harden the heart. For a short time he felt "
        "regret and even asked forgiveness, but without purified association that softness did not last. "
        "His demonic ministers pulled him back into persecution of newborns, brāhmaṇas, cows, sages, "
        "Vedic culture, and Vaiṣṇavas. This pastime warns children and families that bad association can "
        "undo good intentions, and that offenses against devotees and saintly culture destroy auspiciousness. "
        "Lord Kṛṣṇa remains the supreme shelter. Temporary repentance is not the same as lasting purity."
    )

    lessons = [
        "Fear and bodily pride can make a person cruel.",
        "Temporary repentance is weak without good association.",
        "Bad counselors can pull the heart back into darkness.",
        "Offenses against devotees and saintly persons destroy auspiciousness.",
        "Lord Kṛṣṇa is the true shelter for those who remember Him.",
    ]

    questions = [
        "Why did the guards hurry to tell Kaṁsa after Yoga-māyā cried?",
        "What did Devakī ask Kaṁsa to do when he came to the prison?",
        "How did Yoga-māyā appear after Kaṁsa tried to harm the child?",
        "Why did Kaṁsa's soft feelings fade after he met his ministers?",
        "How can choosing good association protect a child's heart?",
    ]

    challenges = [
        "Draw Yoga-māyā as eight-armed Durgā speaking from the sky, with Kaṁsa looking astonished below.",
        "Tell a parent one way bad association can change a person's choices.",
        "Speak one soft prayer asking Kṛṣṇa to protect devotees and saintly people.",
        "Choose one kind word today instead of a harsh word when you feel afraid.",
        "Before sleep, thank Kṛṣṇa for being the shelter of His devotees.",
    ]

    prayer = (
        "Dear Lord Kṛṣṇa, please protect my heart from fear and bad advice. "
        "Help me honor devotees, brāhmaṇas, cows, and all who serve You. "
        "When I feel soft repentance, please keep me close to good association. "
        f"{HARE_KRISHNA} "
        "Please let me sleep safely under Your care. Good night, dear Lord."
    )

    next_preview = (
        "Next time: Story 008 — The Meeting of Nanda and Vasudeva. "
        "A gentle meeting of loving friends awaits in the Krishna Book."
    )

    parent = (
        f"Source: {source}; {scripture}. This episode includes Kaṁsa's attempt against the newborn girl "
        "(Yoga-māyā), her revelation as eight-armed Durgā, Kaṁsa's temporary release and apology, "
        "Vasudeva's teaching on bodily identification, and the ministers' counsel to persecute newborns "
        "born within ten days, plus brāhmaṇas, cows, sages, Vedic culture, and Vaiṣṇavas. Keep discussion "
        "child-safe: acknowledge the attempt and persecution without graphic detail. Do not teach that "
        "Devakī and Vasudeva remained imprisoned after Kaṁsa released them in this chapter. Stress bad "
        "association, offenses against devotees, and shelter in Kṛṣṇa. Avoid absolute claims that "
        "remembering Kṛṣṇa prevents all physical suffering."
    )

    audio = f"""\
Hare Kṛṣṇa, dear children and families!

Tonight is Story 007: Kamsa Begins His Persecutions.
<break time="1.0s" />
Previously, Lord Kṛṣṇa appeared in Mathurā's prison before Devakī and Vasudeva. Following the Lord's arrangement, Vasudeva carried baby Kṛṣṇa through the night to Gokula, left Him with Yaśodā, and brought Yoga-māyā back to the prison. The doors closed again. The chains returned. The guards did not understand what had happened. Tonight we hear what followed.
<break time="1.0s" />
After Vasudeva returned with the baby girl, Yoga-māyā began to cry. Her cry woke the guards. They sat up, confused and afraid. They hurried to Kaṁsa and told him that a child had appeared.
<break time="1.0s" />
Kaṁsa's heart was already restless from the prophecy about Devakī's eighth child. He rushed to the prison. Torchlight shook on the walls as he came. Devakī held the baby girl and pleaded for mercy. She asked him to spare the child and said the baby was a girl, not the son he feared. But Kaṁsa's fear was stronger than her gentle request.
<break time="1.0s" />
In a harsh and frightened mood, Kaṁsa took the child and tried to destroy her. We speak of this carefully for children, without graphic detail. At that very moment, by the Lord's arrangement, the baby slipped from his hands and rose into the sky.
<break time="1.0s" />
There Yoga-māyā revealed her glorious form, shining with divine power and appearing with eight arms like Durgā. Devakī and Vasudeva looked up with reverence. Kaṁsa stared upward, astonished. From the sky she addressed him. In paraphrase, she told Kaṁsa that the enemy he feared had already taken birth elsewhere, and that his attempt against her could not stop the Lord's plan. Then she disappeared.
<break time="1.0s" />
Kaṁsa stood shaken. For a short time his heart softened. He released Devakī and Vasudeva from the prison and asked their forgiveness for the cruel way he had treated them. Vasudeva spoke with calm wisdom. He explained that people become enemies when they identify too strongly with the body and forget the eternal soul. Temporary anger, fear, and bodily pride darken the heart. Hearing this, Kaṁsa seemed repentant for a while.
<break time="1.0s" />
But lasting purity needs more than one soft feeling. The next day Kaṁsa called his demonic ministers and asked what he should do. Bad association quickly pulled his mind back toward fear and violence. Those ministers advised him to search out and kill newborn children born within the previous ten days. They also urged him to attack brāhmaṇas, cows, sages, Vedic culture, and Vaiṣṇavas, because these support the worship of Lord Viṣṇu.
<break time="1.0s" />
Listening to that wicked counsel, Kaṁsa authorized the persecution. The peaceful order of Mathurā was threatened by offenses against saintly persons and devotees.
<break time="1.0s" />
Dear children, this chapter is sober. Temporary regret is not the same as lasting purity. Bad association can undo a soft moment of repentance. Offenses against brāhmaṇas, cows, sages, and Vaiṣṇavas destroy auspiciousness. We do not claim that remembering Kṛṣṇa removes every difficulty at once. We learn to take shelter of Him and to honor those who serve Him.
<break time="1.0s" />
Five lessons for tonight:
1. Fear and bodily pride can make a person cruel.
2. Temporary repentance is weak without good association.
3. Bad counselors can pull the heart back into darkness.
4. Offenses against devotees and saintly persons destroy auspiciousness.
5. Lord Kṛṣṇa is the true shelter for those who remember Him.
<break time="1.0s" />
{prayer}
<break time="1.0s" />
{next_preview}
"""

    poster = (
        "Child-safe ultra-realistic cinematic painting: Yoga-māyā as glorious eight-armed Durgā rising in "
        "the sky above astonished Kaṁsa in the prison courtyard; Devakī and Vasudeva stand respectfully "
        "nearby with folded hands; soft divine light; no gore, no dashed infant, no visible baby Kṛṣṇa, "
        "no peacock feather, no text or captions inside the artwork."
    )
    coloring = (
        "Cute ages 6–12 coloring page: Yoga-māyā/Durgā with eight arms in the sky; Kaṁsa looking astonished "
        "below; Devakī and Vasudeva nearby; thick clean black outlines; white background; large colorable "
        "spaces; no second baby, no baby Kṛṣṇa, no peacock feather, no graphic violence, no weapons used "
        "against an infant."
    )

    return StoryContent(
        title=title,
        recap=recap,
        main_story=main_story,
        moral=lessons[0],
        takeaway=lessons[-1],
        five_star_challenge=challenges,
        audio_script=audio,
        parent_notes=parent,
        parent_note=parent,
        parent_discussion_note=parent,
        greeting="Hare Kṛṣṇa, dear children and families!",
        series_name="Krishna Book Bedtime",
        story_number="007",
        story_format="v2",
        source_reference=source,
        scripture_reference=scripture,
        age_range="6-12",
        devotional_meaning=meaning,
        five_lessons=lessons,
        think_about_it=questions,
        bedtime_prayer=prayer,
        bedtime_reflection=questions[4],
        next_story_preview=next_preview,
        poster_visual_brief=poster,
        coloring_visual_brief=coloring,
        poster_one_liner="Yoga-māyā warns Kaṁsa; soft hearts need good association.",
        hero_image_prompt=poster,
        coloring_page_prompt=coloring,
        line_art_prompt=coloring,
        recall_questions=questions[:3],
        thinking_questions=questions[3:],
        word_search_words=["Kamsa", "Yogamaya", "Durga", "Devaki", "Vasudeva", "Mathura", "Vishnu", "devotee"],
        draw_activity="Draw eight-armed Yoga-māyā speaking from the sky while Kaṁsa looks up in astonishment.",
        family_activity="Talk together about one good friend or teacher who helps your family choose kindness over fear.",
    )
