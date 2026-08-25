"""Preferred story-specific activity packs for Stories 026–035."""

from __future__ import annotations

from ..models import PlanRow
from .models import ActivityPack, ActivityPage, MatchingCard, SequenceCard


def _pack_026(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.18: Balarāma's party won the game; Krishna's party carried the winners; "
        "Pralambāsura disguised as a boy carried Balarāma away and was killed by Balarāma's fist."
    )
    sequence = [
        SequenceCard("Krishna and Balarāma divided the boys into two teams for a playful game.", "Draw two teams with Krishna and Balarāma as captains.", 1),
        SequenceCard("Balarāma's party, with Śrīdāmā and Vṛṣabha, won the match.", "Draw Balarāma's team celebrating victory.", 2),
        SequenceCard("Krishna's party carried the winners on their backs—Krishna carried Śrīdāmā.", "Draw Krishna giving Śrīdāmā a piggyback ride.", 3),
        SequenceCard("Bhadrasena carried Vṛṣabha on his shoulders.", "Draw Bhadrasena carrying Vṛṣabha.", 4),
        SequenceCard("Pralambāsura, disguised as a cowherd boy, offered to carry Balarāma.", "Draw the disguised demon smiling beside Balarāma.", 5),
        SequenceCard("Pralambāsura ran deep into the forest carrying Balarāma on his shoulders.", "Draw them moving away from the other boys.", 6),
        SequenceCard("Pralambāsura revealed his terrible demon form.", "Draw the demon form—child-safe, not gory.", 7),
        SequenceCard("Balarāma struck Pralambāsura on the head with His fist and protected His friends.", "Draw Balarāma standing calmly after protecting everyone.", 8),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 6, 3, 1, 7, 4)]
    return ActivityPack(
        activity_title="Order the Pralambāsura Pastime",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: help children number cards and discuss true friendship vs disguise.",
        learning_goal="Recall the source-correct game outcome and Balarāma's protection.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Put Chapter 18 events in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Cards are shuffled on purpose.",
                    "Number them 1–8 in true story order.",
                    "Circle the card where Balarāma's fist protects everyone.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="True friend or disguise?",
                page_type="MATCHING_CARDS",
                instructions=["Match each moment to what it teaches about friendship and protection."],
                components=[
                    MatchingCard("Pralambāsura looked like a playmate", "Appearances can hide danger—stay close to Krishna and Balarāma", "disguise"),
                    MatchingCard("Balarāma's party won fairly", "Truthful play and teamwork matter", "win"),
                    MatchingCard("Krishna carried Śrīdāmā", "The Lord honors friendship even when His team loses", "carry"),
                    MatchingCard("Balarāma struck the demon", "The Lord protects His devotees", "protect"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Number the picture cards with help; talk about Balarāma's protection.",
            "ages_9_13": "Write the order numbers and explain why disguise is dangerous without Krishna.",
        },
    )


def _pack_027(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.19: Missing cows/goats wandered into Īṣīkāṭavī; the boys followed hoofprints; "
        "Krishna called the cows by name; Krishna swallowed the forest fire; they awoke in Bhāṇḍīra forest."
    )
    sequence = [
        SequenceCard("The unattended calves, cows, and buffalo wandered into Īṣīkāṭavī for fresh grass.", "Draw animals grazing in the forest.", 1),
        SequenceCard("The animals cried when they saw the forest fire.", "Draw worried cows among smoke—no horror.", 2),
        SequenceCard("Krishna, Balarāma, and the boys noticed the herd was missing.", "Draw the boys searching.", 3),
        SequenceCard("They followed hoofprints and signs of eaten grass.", "Draw hoofprints on the path.", 4),
        SequenceCard("Krishna called each cow by name, and the cows answered Him.", "Draw Krishna calling and cows responding.", 5),
        SequenceCard("Fire surrounded the boys and animals; they appealed to Krishna and Balarāma.", "Draw boys praying with hands folded.", 6),
        SequenceCard("Krishna swallowed the blazing forest fire.", "Draw flames flowing inward toward Krishna's mouth.", 7),
        SequenceCard("When they opened their eyes, they were again in Bhāṇḍīra forest and returned home at evening.", "Draw peaceful Bhāṇḍīra trees at sunset.", 8),
    ]
    printed = [sequence[i] for i in (3, 0, 6, 2, 7, 1, 5, 4)]
    return ActivityPack(
        activity_title="Trace the Cows and the Forest Fire Rescue",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: discuss real fire safety separately from the scripture miracle.",
        learning_goal="Order the rescue sequence and remember Krishna's inward swallowing of the fire.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        safety_note="PARENT HELP: Real fire safety—never play with fire; this page is about the scripture pastime only.",
        pages=[
            ActivityPage(
                page_title="Rescue sequence cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=["Number the eight cards in true order.", "Underline the card where Krishna swallows the fire inward."],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Match the rescue clues",
                page_type="MATCHING_CARDS",
                instructions=["Draw lines matching each clue to its role in the pastime."],
                components=[
                    MatchingCard("Hoofprints in the forest", "Showed where the cows had gone", "hoof"),
                    MatchingCard("Eaten grass", "Showed the animals had wandered ahead", "grass"),
                    MatchingCard("Krishna calling cows by name", "The Lord knows and calls each devotee", "call"),
                    MatchingCard("Flames drawn inward", "Krishna devoured the fire to protect everyone", "swallow"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Trace the rescue path with a finger; parent explains real fire safety separately.",
            "ages_9_13": "Order the cards and write how Krishna swallowed the fire inward.",
        },
    )


def _pack_028(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.20 compares the end of the rainy season to autumn—clear lakes, blooming lotuses, "
        "and minds fixed on Krishna like rivers meeting the ocean."
    )
    return ActivityPack(
        activity_title="Rainy Season to Autumn Observations",
        activity_type="DRAW_AND_REFLECT",
        send_mode="PARENT_GUIDED",
        estimated_minutes=15,
        parent_effort="Low: help children connect nature observations to remembering Krishna.",
        learning_goal="Notice how autumn clarity in Vṛndāvana reflects devotional remembrance.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Compare rainy season and autumn",
                page_type="MATCHING_CARDS",
                instructions=["Match each source observation to its autumn meaning."],
                components=[
                    MatchingCard("Muddy ponds become clear", "A peaceful mind becomes clear when fixed on Krishna", "clear"),
                    MatchingCard("Lotuses bloom after rain", "Devotees blossom in remembrance of the Lord", "lotus"),
                    MatchingCard("Waters grow calm", "Disturbances settle when we chant and remember", "calm"),
                    MatchingCard("Cool breezes in Vṛndāvana", "Krishna and Balarāma lead the cows in gentle autumn", "breeze"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Draw one autumn sign of Krishna's shelter",
                page_type="DRAW_AND_REFLECT",
                instructions=[
                    "Draw one scene from Vṛndāvana in autumn (clear lake, lotus, cows, or Krishna with flute).",
                    "Write one sentence: how does nature remind you to remember Krishna?",
                ],
                components=[],
                story_connection=connection,
            ),
        ],
        answer_key=["clear", "lotus", "calm", "breeze"],
        age_variants={
            "ages_6_8": "Match the autumn signs with help; draw one peaceful lake or lotus.",
            "ages_9_13": "Match comparisons and write how autumn clarity reminds you of Krishna.",
        },
    )


def _pack_029(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.21: In autumn Krishna plays His flute in the forest; the gopīs remain in Vraja "
        "and discuss among themselves how peacocks, deer, cows, Yamunā, and clouds respond—absorbed remembrance, not a night meeting."
    )
    return ActivityPack(
        activity_title="Match the Flute's Effects in Vraja",
        activity_type="MATCHING",
        send_mode="PARENT_GUIDED",
        estimated_minutes=15,
        parent_effort="Low: keep the mood daytime remembrance in Vraja—no night rendezvous.",
        learning_goal="Match how living beings respond to Krishna's flute while the gopīs stay in Vraja discussing Him.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Who hears the flute?",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each listener to how Krishna's flute touches them.",
                    "Remember: the gopīs stay in Vraja and talk about Krishna—they do not leave for a night meeting.",
                ],
                components=[
                    MatchingCard("Peacocks in the forest", "Dance with joy when they hear Krishna's flute", "peacock"),
                    MatchingCard("Deer in the woods", "Stand still, enchanted by the sweet song", "deer"),
                    MatchingCard("Cows and calves", "Gather closer, forgetting even fresh grass", "cows"),
                    MatchingCard("Yamunā's waters", "Pause and listen as if the river itself is absorbed", "yamuna"),
                    MatchingCard("Clouds overhead", "Gather like a canopy above Krishna and the boys", "clouds"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Draw remembrance in Vraja",
                page_type="DRAW_AND_REFLECT",
                instructions=[
                    "Draw the gopīs in Vraja talking about Krishna's flute (daytime village scene).",
                    "Write one sentence: why is remembering Krishna while staying in one's place an example of Krishna consciousness?",
                ],
                components=[],
                story_connection=connection,
            ),
        ],
        answer_key=["peacock", "deer", "cows", "yamuna", "clouds"],
        age_variants={
            "ages_6_8": "Match peacocks, deer, cows, Yamunā, and clouds with picture help.",
            "ages_9_13": "Match all flute effects and explain why the gopīs' discussion in Vraja is the example—not a night meeting.",
        },
    )


def _pack_030(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.22: Month-long Kātyāyanī vow by the Yamunā; garments taken and returned respectfully; "
        "Krishna's autumn promise; praise of charitable trees. Child-safe wording only—no naked or exposed bodies."
    )
    sequence = [
        SequenceCard("The unmarried gopī girls keep a month-long vow to Goddess Kātyāyanī.", "Draw girls offering flowers at a simple altar.", 1),
        SequenceCard("Each morning they go to the Yamunā for worship and prayer.", "Draw Yamunā waters with lotuses—modest, distant figures.", 2),
        SequenceCard("Krishna understands their hearts and gathers their garments from the bank.", "Draw folded cloths held respectfully—no bodies shown.", 3),
        SequenceCard("The girls appeal politely for their clothes to be returned.", "Draw hands raised in respectful request behind reeds.", 4),
        SequenceCard("Krishna returns the garments with care and dignity.", "Draw cloths being handed back; foliage frames the scene.", 5),
        SequenceCard("He promises they will meet Him again in the next autumn season.", "Draw a calm promise gesture beside the river.", 6),
        SequenceCard("Later Krishna praises the charitable trees that give shade and fruit to others.", "Draw trees sheltering birds and travelers.", 7),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 6, 3, 1, 4)]
    return ActivityPack(
        activity_title="Order the Kātyāyanī Vow Pastime",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: keep labels modest; talk about vows, respect, and service—never body exposure.",
        learning_goal="Order the vow, Yamunā, garments, appeal, return, promise, and charitable trees sequence.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        safety_note="PARENT HELP: Keep drawings modest (waterline, reeds, distance). Never draw or say 'naked.'",
        pages=[
            ActivityPage(
                page_title="Kātyāyanī vow sequence cards",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Cards are shuffled on purpose.",
                    "Number them 1–7 in true story order.",
                    "Circle the card where Krishna returns the garments respectfully.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Match respectful lessons",
                page_type="MATCHING_CARDS",
                instructions=["Match each moment to its child-safe lesson."],
                components=[
                    MatchingCard("Month-long Kātyāyanī vow", "Steady prayer and dedication please the Lord", "vow"),
                    MatchingCard("Appeal for the garments", "Ask politely and trust Krishna's care", "appeal"),
                    MatchingCard("Garments returned with dignity", "The Lord honors respect and modesty", "return"),
                    MatchingCard("Charitable trees", "Serve others with shade, fruit, and shelter", "trees"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Number the cards with help; keep drawings behind reeds and water.",
            "ages_9_13": "Order the vow sequence and explain why charitable trees teach service.",
        },
    )


def _pack_031(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.23: Hungry cowherd boys; brāhmaṇas refuse the first request; devoted wives bring food; "
        "Krishna sends them home; boys eat; brāhmaṇas later repent. Contrast sincere devotion with ritual pride—respectfully."
    )
    sequence = [
        SequenceCard("The cowherd boys grow hungry in the forest and ask Krishna for help.", "Draw hungry boys near Krishna and Balarāma.", 1),
        SequenceCard("Krishna sends them to ask the sacrificing brāhmaṇas for food.", "Draw boys approaching a sacrificial fire respectfully.", 2),
        SequenceCard("The brāhmaṇas refuse and give no reply—busy with ritual.", "Draw silent priests at the fire—no mocking faces.", 3),
        SequenceCard("The brāhmaṇas' wives joyfully bring food despite relatives' resistance.", "Draw wives carrying pots of offerings.", 4),
        SequenceCard("Krishna meets them kindly and sends them home to their duties.", "Draw Krishna gesturing gently toward the path home.", 5),
        SequenceCard("The boys happily eat the food offered in devotion.", "Draw cowherd boys sharing prasadam.", 6),
        SequenceCard("Later the brāhmaṇas repent for missing the chance to serve Krishna.", "Draw brāhmaṇas with folded hands—humble, not ridiculed.", 7),
    ]
    printed = [sequence[i] for i in (3, 0, 5, 2, 6, 1, 4)]
    return ActivityPack(
        activity_title="Order the Brāhmaṇas' Wives Pastime",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: speak respectfully of brāhmaṇas; praise the wives' devotion without mocking ritual.",
        learning_goal="Order the hunger-to-repentance sequence and match devotion versus ritual pride respectfully.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Food and devotion sequence",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven cards in true order.",
                    "Underline where the wives bring food in devotion.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Devotion or ritual pride?",
                page_type="MATCHING_CARDS",
                instructions=["Match each side to what the pastime teaches—respectfully, without ridicule."],
                components=[
                    MatchingCard("Wives bring food at once", "Sincere devotion recognizes Krishna immediately", "devotion"),
                    MatchingCard("Brāhmaṇas busy with sacrifice alone", "Ritual knowledge without love can miss the Lord", "ritual"),
                    MatchingCard("Krishna sends the wives home", "Duty and devotion can walk together", "home"),
                    MatchingCard("Brāhmaṇas later repent", "Humility restores the chance to serve", "repent"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Number the cards; talk about sharing food with love.",
            "ages_9_13": "Order the sequence and explain devotion vs ritual pride without disrespecting brāhmaṇas.",
        },
    )


def _pack_032(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.24: Nanda's planned Indra sacrifice; Krishna teaches cow protection and Vraja's duty; "
        "Annakūṭa worship of Govardhana; offerings accepted—no storm or hill-lifting (that is Ch.25)."
    )
    sequence = [
        SequenceCard("Nanda prepares the customary sacrifice for Indra.", "Draw preparations for Indra-yajña.", 1),
        SequenceCard("Krishna asks why and teaches that Vraja should honor cows and Govardhana.", "Draw Krishna speaking kindly to Nanda.", 2),
        SequenceCard("The community gathers Annakūṭa foods and offerings for Govardhana.", "Draw heaps of festive prasadam.", 3),
        SequenceCard("They honor brāhmaṇas, cows, animals, and people with the feast.", "Draw decorated cows and shared plates.", 4),
        SequenceCard("Villagers decorate the cows and circumambulate Govardhana Hill.", "Draw a joyful walk around the hill.", 5),
        SequenceCard("Krishna assumes a great Govardhana form and accepts the offerings.", "Draw a majestic hill-form receiving the feast—no rain.", 6),
        SequenceCard("The worship finishes in joy; everyone is satisfied.", "Draw smiling families after the Annakūṭa.", 7),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 6, 3, 1, 4)]
    return ActivityPack(
        activity_title="Order the Annakūṭa Govardhana Worship",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: celebrate the feast and teaching only—do not add the storm yet.",
        learning_goal="Order Annakūṭa worship and match Krishna's cow-protection teaching versus Indra sacrifice.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Govardhana worship sequence",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven cards in true Ch.24 order.",
                    "Do not add rain or hill-lifting—those belong to the next chapter.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Cow protection vs Indra sacrifice",
                page_type="MATCHING_CARDS",
                instructions=["Match Krishna's teaching to what Vraja should honor."],
                components=[
                    MatchingCard("Indra sacrifice alone", "Looks upward but can forget local duty", "indra"),
                    MatchingCard("Protecting cows and calves", "Vraja's real work and affection", "cows"),
                    MatchingCard("Worshiping Govardhana", "Honor the hill that shelters and feeds", "hill"),
                    MatchingCard("Annakūṭa feast shared", "Offer and distribute food with love", "feast"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Order the feast cards; draw decorated cows—no storm.",
            "ages_9_13": "Order Annakūṭa and explain cow protection vs Indra-yajña in Krishna's words.",
        },
    )


def _pack_033(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.25: Indra's pride; Sāṁvartaka clouds; Krishna lifts Govardhana on His left little finger; "
        "seven days of shelter; clouds stop; hill replaced; affectionate embraces. No Surabhi or milk abhiṣeka."
    )
    sequence = [
        SequenceCard("Indra becomes proud and angry that his sacrifice was stopped.", "Draw Indra looking stern in the heavens—child-safe.", 1),
        SequenceCard("He sends the fierce Sāṁvartaka clouds to flood Vṛndāvana.", "Draw dark storm clouds and rain—no gore.", 2),
        SequenceCard("Cows shield their calves; the residents pray to Krishna for protection.", "Draw cows arched over calves; families praying.", 3),
        SequenceCard("Krishna lifts Govardhana on the little finger of His left hand.", "Draw the hill held aloft on one small finger.", 4),
        SequenceCard("Everyone with animals and belongings shelters safely for seven days.", "Draw families and cows under the hill-umbrella.", 5),
        SequenceCard("Indra orders the Sāṁvartaka clouds to stop; the sky clears.", "Draw clouds pulling back and sunlight returning.", 6),
        SequenceCard("Krishna replaces the hill in its place; residents embrace Him with blessings.", "Draw the hill set down and joyful embraces—no Surabhi.", 7),
    ]
    printed = [sequence[i] for i in (3, 0, 5, 2, 6, 1, 4)]
    return ActivityPack(
        activity_title="Order the Govardhana Storm Protection",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: emphasize Krishna's protection; keep storm child-safe; skip Surabhi (next chapter).",
        learning_goal="Order Indra's pride through embraces after the seven-day shelter.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Storm protection sequence",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven cards in true Ch.25 order.",
                    "Circle the card where Krishna lifts the hill on His left little finger.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Match protection moments",
                page_type="MATCHING_CARDS",
                instructions=["Match each storm moment to its meaning."],
                components=[
                    MatchingCard("Indra's pride", "False prestige brings unnecessary trouble", "pride"),
                    MatchingCard("Sāṁvartaka clouds", "A devastating storm sent in anger", "clouds"),
                    MatchingCard("Left little finger lift", "The Lord protects easily and completely", "lift"),
                    MatchingCard("Seven days under the hill", "Safe shelter until the danger ends", "seven"),
                    MatchingCard("Hill replaced; embraces", "Joy and gratitude after protection", "embrace"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Number the protection cards; draw Krishna holding the hill gently.",
            "ages_9_13": "Order the storm sequence and note that Surabhi belongs to a later chapter.",
        },
    )


def _pack_034(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.26: After the rescue, cowherd men recall Krishna's wonders (Pūtanā, cart, Tṛṇāvarta, and more); "
        "Nanda shares Garga Muni's words. Reflection and naming—not life continuing under the lifted hill."
    )
    return ActivityPack(
        activity_title="Match Wonderful Krishna's Pastimes",
        activity_type="MATCHING",
        send_mode="PARENT_GUIDED",
        estimated_minutes=16,
        parent_effort="Low: this is a discussion after the rescue—not storm action under the hill.",
        learning_goal="Match wonders to names and recall Nanda's Garga Muni reflection.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Match the wonder to the name",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Draw lines from each wonder to the correct name.",
                    "This chapter is friends talking with Nanda—not living under the lifted hill.",
                ],
                components=[
                    MatchingCard("Demoness who tried to harm infants", "Pūtanā", "putana"),
                    MatchingCard("Hand-driven cart overturned by the baby", "The cart pastime", "cart"),
                    MatchingCard("Whirlwind demon", "Tṛṇāvarta", "trinavarta"),
                    MatchingCard("Twin arjuna trees pulled down", "Yamala-Arjuna trees", "trees"),
                    MatchingCard("Crane demon defeated", "Bakāsura", "baka"),
                    MatchingCard("Hill held as an umbrella", "Govardhana protection", "govardhana"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Nanda and Garga Muni reflection",
                page_type="DRAW_AND_REFLECT",
                instructions=[
                    "Draw Nanda speaking with the cowherd men after the wonders.",
                    "Write one sentence Garga Muni taught about Krishna (colors, names, or likeness to Viṣṇu/Nārāyaṇa).",
                ],
                components=[],
                story_connection=connection,
            ),
        ],
        answer_key=["putana", "cart", "trinavarta", "trees", "baka", "govardhana"],
        age_variants={
            "ages_6_8": "Match Pūtanā, cart, and Tṛṇāvarta with help; draw Nanda talking.",
            "ages_9_13": "Match all wonders and write Garga Muni's teaching from Nanda's memory.",
        },
    )


def _pack_035(plan: PlanRow) -> ActivityPack:
    connection = (
        "Krishna Book Ch.27: After the rescue, Indra approaches privately, admits pride, hears Krishna's instruction; "
        "Surabhi; milk abhiṣeka; Govinda name; Indra returns with permission. Clouds already stopped in Ch.25."
    )
    sequence = [
        SequenceCard("Indra approaches Krishna privately in a secluded place and bows.", "Draw Indra bowing respectfully—alone with Krishna.", 1),
        SequenceCard("Indra admits his pride and offense before the Lord.", "Draw Indra with folded hands, humble.", 2),
        SequenceCard("Krishna instructs him: opulence is delegated; return to duty without false prestige.", "Draw Krishna speaking calmly to Indra.", 3),
        SequenceCard("Surabhi the celestial cow arrives with prayers of devotion.", "Draw Surabhi beside Indra and Krishna.", 4),
        SequenceCard("They bathe Krishna in a milk abhiṣeka, with celestial waters through Airāvata.", "Draw milk and gentle water poured in honor—festive, not stormy.", 5),
        SequenceCard("Krishna is honored with the name Govinda amid flower showers.", "Draw flower petals and the name Govinda celebrated.", 6),
        SequenceCard("With permission, Indra returns to his heavenly duty, free of pride.", "Draw Indra departing respectfully toward the heavens.", 7),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 6, 3, 1, 4)]
    return ActivityPack(
        activity_title="Order Indra's Prayers and the Govinda Abhiṣeka",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: begin after the rescue; do not reopen the storm as Ch.27 action.",
        learning_goal="Order Indra's private approach through Surabhi, milk abhiṣeka, Govinda naming, and permitted return.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Indra and Surabhi sequence",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven cards in true Ch.27 order.",
                    "Circle where Krishna receives the name Govinda.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Match humility lessons",
                page_type="MATCHING_CARDS",
                instructions=["Match each moment to what it teaches about pride and mercy."],
                components=[
                    MatchingCard("Private approach and bow", "True repentance seeks the Lord quietly", "private"),
                    MatchingCard("Admission of pride", "Honest confession opens the heart", "pride"),
                    MatchingCard("Krishna's instruction", "Mercy can remove false prestige", "instruction"),
                    MatchingCard("Milk abhiṣeka and Govinda name", "Honor the Lord who protects the cows", "govinda"),
                    MatchingCard("Return with permission", "Resume duty without arrogance", "return"),
                ],
                story_connection=connection,
            ),
        ],
        answer_key=[c.event for c in sorted(sequence, key=lambda x: x.source_order)],
        age_variants={
            "ages_6_8": "Number the abhiṣeka cards; celebrate the name Govinda.",
            "ages_9_13": "Order Indra's humility sequence and explain why Surabhi belongs here, not in the storm chapter.",
        },
    )


PREFERRED_PACKS_026_035: dict[str, object] = {
    "026": _pack_026,
    "027": _pack_027,
    "028": _pack_028,
    "029": _pack_029,
    "030": _pack_030,
    "031": _pack_031,
    "032": _pack_032,
    "033": _pack_033,
    "034": _pack_034,
    "035": _pack_035,
}
