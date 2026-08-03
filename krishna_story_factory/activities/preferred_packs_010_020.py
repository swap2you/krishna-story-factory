"""Preferred activity packs for Stories 010–020 (Krishna Book pastimes)."""

from __future__ import annotations

from ..models import PlanRow
from .models import ActivityPack, ActivityPage, MatchingCard, RolePlayCard, SequenceCard


def _pack_010(plan: PlanRow) -> ActivityPack:
    connection = (
        "Baby Kṛṣṇa lies under a cart; the cowherd boys and Yaśodā are nearby when He "
        "kicks and breaks the cart yoke (Krishna Book Ch.7)."
    )
    sequence = [
        SequenceCard(
            "Baby Kṛṣṇa rests under the cart after feeding.",
            "Draw baby Kṛṣṇa lying calmly under a wooden cart.",
            1,
        ),
        SequenceCard(
            "Yaśodā places Him there and turns to household work.",
            "Draw Mother Yaśodā walking toward pots, glancing back kindly.",
            2,
        ),
        SequenceCard(
            "Cowherd boys play near the cart wheels.",
            "Draw joyful boys with sticks and soft dust clouds—no harm.",
            3,
        ),
        SequenceCard(
            "Kṛṣṇa kicks upward and the cart yoke breaks.",
            "Draw the cart tipping as baby Kṛṣṇa smiles—no scary crash.",
            4,
        ),
        SequenceCard(
            "Pots and wheels tumble while Kṛṣṇa stays safe.",
            "Draw spilled pots and a safe baby glowing with soft light.",
            5,
        ),
        SequenceCard(
            "Yaśodā rushes back and lifts her child with wonder.",
            "Draw Yaśodā hugging Kṛṣṇa while neighbors gather gently.",
            6,
        ),
        SequenceCard(
            "The cowherd community praises the Lord's astonishing play.",
            "Draw villagers offering flowers and smiling faces.",
            7,
        ),
    ]
    printed = [sequence[i] for i in (3, 0, 5, 1, 6, 2, 4)]
    return ActivityPack(
        activity_title="Baby Kṛṣṇa Breaks the Cart",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: help children number cards and retell the cart pastime.",
        learning_goal="Order the Chapter 7 cart events and name how Kṛṣṇa stayed safe in play.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Put the cart pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "The seven cards are shuffled on purpose.",
                    "Number them in true story order.",
                    "Circle the card that shows the cart yoke breaking.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Cart pastime matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Draw a line from each left item to its matching meaning.",
                    "Talk about how Kṛṣṇa's play astonished Vraja.",
                ],
                components=[
                    MatchingCard("cart under the baby", "resting place after feeding", "place", pair_id="A"),
                    MatchingCard("Yaśodā's brief absence", "turns to household duties", "mother", pair_id="B"),
                    MatchingCard("cowherd boys nearby", "play beside the wheels", "friends", pair_id="C"),
                    MatchingCard("kick upward", "breaks the heavy yoke", "action", pair_id="D"),
                    MatchingCard("tumbling pots", "show the cart's fall is real", "detail", pair_id="E"),
                    MatchingCard("mother's embrace", "wonder and protective love", "result", pair_id="F"),
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Number cards and draw baby Kṛṣṇa safe under soft light.",
            "ages_9_13": "Explain why the broken cart reveals Kṛṣṇa's divine play.",
        },
        safety_note="PARENT HELP: Show a tipped cart and spilled pots only—no crushing, blood, or panic.",
        completion_prompt="Retell the seven events, then say one way Yaśodā showed loving care.",
        review_questions=[
            "Where was baby Kṛṣṇa lying when the cart broke?",
            "What did Yaśodā do when she returned?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside Krishna Book Chapter 7 cart pastime. Keep the break playful and child-safe; "
            "do not invent injuries or Sanskrit verses."
        ),
        qa_requirements=[
            "seven Chapter 7 cart sequence events",
            "cart pastime matching pairs",
            "child-safe wording",
            "shuffled print order",
            "answers only in manifest",
        ],
    )


def _pack_011(plan: PlanRow) -> ActivityPack:
    connection = (
        "The whirlwind demon Tṛṇāvarta carries baby Kṛṣṇa into the sky; Kṛṣṇa becomes "
        "impossibly heavy, the demon falls, and the Lord returns safely to Yaśodā "
        "(Krishna Book Ch.7 / Tṛṇāvarta pastime)."
    )
    sequence = [
        SequenceCard(
            "Yaśodā holds baby Kṛṣṇa outdoors in Gokula.",
            "Draw mother and baby under a calm open sky.",
            1,
        ),
        SequenceCard(
            "A dusty whirlwind rises and Tṛṇāvarta appears.",
            "Draw a swirling wind shape—no scary claws or gore.",
            2,
        ),
        SequenceCard(
            "The whirlwind lifts baby Kṛṣṇa high into the air.",
            "Draw Kṛṣṇa held in soft wind above the trees.",
            3,
        ),
        SequenceCard(
            "Yaśodā searches and calls with loving worry.",
            "Draw Yaśodā looking upward with open hands.",
            4,
        ),
        SequenceCard(
            "Kṛṣṇa becomes extremely heavy in the demon's grasp.",
            "Draw the whirlwind struggling while Kṛṣṇa stays calm.",
            5,
        ),
        SequenceCard(
            "Tṛṇāvarta falls powerless; Kṛṣṇa remains unharmed.",
            "Draw the wind settling and Kṛṣṇa glowing safely.",
            6,
        ),
        SequenceCard(
            "Villagers find Kṛṣṇa and return Him to Yaśodā.",
            "Draw joyful neighbors handing the baby to His mother.",
            7,
        ),
        SequenceCard(
            "Mother and child reunite; Gokula breathes in relief.",
            "Draw a warm embrace with flower garlands nearby.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (4, 0, 6, 2, 7, 1, 5, 3)]
    return ActivityPack(
        activity_title="Salvation of Tṛṇāvarta",
        activity_type="MINI_DRAMA",
        send_mode="PARENT_GUIDED",
        estimated_minutes=22,
        parent_effort="Low: assign roles, keep the whirlwind playful, and retell the rescue.",
        learning_goal="Act the Tṛṇāvarta scene and order how Kṛṣṇa's weight protected everyone.",
        story_connection=connection,
        materials=["pencil", "four household props"],
        pages=[
            ActivityPage(
                page_title="Whirlwind rescue role cards",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role and read the paraphrase line aloud.",
                    "Perform each action gently—no shouting or scary faces.",
                    "Retell how Kṛṣṇa became heavy and returned safely.",
                ],
                components=[
                    RolePlayCard(
                        "Narrator",
                        "A whirlwind rises in Gokula while baby Kṛṣṇa rests with Yaśodā.",
                        "Point upward then guide friends through each beat.",
                        "story cards",
                    ),
                    RolePlayCard(
                        "Yaśodā",
                        "My child is gone into the swirling dust—please help me find Him!",
                        "Cup hands to call and look toward the sky.",
                        "flower garland",
                    ),
                    RolePlayCard(
                        "Tṛṇāvarta",
                        "I try to carry the baby away, but He suddenly feels too heavy.",
                        "Spin once slowly, then sink to one knee without falling hard.",
                        "loose scarf for wind",
                    ),
                    RolePlayCard(
                        "Baby Kṛṣṇa",
                        "I remain calm and make Myself heavy so the whirlwind cannot succeed.",
                        "Sit still with a peaceful smile while others move around you.",
                        "small soft ball",
                    ),
                    RolePlayCard(
                        "Cowherd neighbor",
                        "Look—the wind has stopped and the baby is safe on the ground!",
                        "Walk in and offer Kṛṣṇa gently toward Yaśodā.",
                        "paper leaf",
                    ),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the Tṛṇāvarta pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one calm, child-safe detail on each card.",
                    "Circle the card where Kṛṣṇa becomes heavy.",
                ],
                components=printed,
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Act with short lines and soft scarf wind motions.",
            "ages_9_13": "Add one sentence about why weight stopped the demon without violence.",
        },
        safety_note="PARENT HELP: Keep the whirlwind as dust and cloth motion only—no choking, crushing, or demon gore.",
        completion_prompt="Perform the rescue, then share one way Kṛṣṇa protected His devotees.",
        review_questions=[
            "What happened when Tṛṇāvarta lifted baby Kṛṣṇa?",
            "How did Kṛṣṇa stop the whirlwind demon?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside the Tṛṇāvarta pastime. Emphasize protection and reunion; avoid graphic "
            "demon defeat language or invented ślokas."
        ),
        qa_requirements=[
            "five complete distinct role cards",
            "eight Tṛṇāvarta sequence events",
            "child-safe whirlwind wording",
            "no placeholder role lines",
            "answers only in manifest",
        ],
    )


def _pack_012(plan: PlanRow) -> ActivityPack:
    connection = (
        "While baby Kṛṣṇa yawns, Mother Yaśodā sees the universe within His mouth and "
        "her astonished love for Him increases (Krishna Book / yawning vision pastime)."
    )
    sequence = [
        SequenceCard(
            "Yaśodā sits close and watches baby Kṛṣṇa play.",
            "Draw mother and child on a quiet courtyard mat.",
            1,
        ),
        SequenceCard(
            "Baby Kṛṣṇa opens His mouth in a wide yawn.",
            "Draw a gentle yawn with soft light—no scary teeth.",
            2,
        ),
        SequenceCard(
            "Within His mouth Yaśodā glimpses sky, stars, and worlds.",
            "Draw tiny stars and planets inside a soft oval of light.",
            3,
        ),
        SequenceCard(
            "She sees oceans, mountains, and living beings in wonder.",
            "Draw small waves and hills inside the light—keep it peaceful.",
            4,
        ),
        SequenceCard(
            "Yaśodā is astonished and cannot speak at first.",
            "Draw her hands on her heart with wide, loving eyes.",
            5,
        ),
        SequenceCard(
            "The vision closes and ordinary playfulness returns.",
            "Draw baby Kṛṣṇa smiling as if nothing unusual happened.",
            6,
        ),
        SequenceCard(
            "Her maternal love grows even deeper for Kṛṣṇa.",
            "Draw Yaśodā hugging Him with a warm smile.",
            7,
        ),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 3, 6, 1, 4)]
    return ActivityPack(
        activity_title="Yaśodā Sees the Universe While Kṛṣṇa Yawns",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: help children order cards and talk about motherly wonder.",
        learning_goal="Retell the yawn vision in order and name how Yaśodā's love increased.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Put the yawn vision in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven shuffled cards in story order.",
                    "Draw one gentle detail on each card.",
                    "Circle the card that shows the universe vision.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Wonder and love matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each left item to its right meaning.",
                    "Younger path: draw lines. Older path: write one sentence per match.",
                ],
                components=[
                    MatchingCard("Kṛṣṇa's yawn", "opens the surprising vision", "moment", pair_id="A"),
                    MatchingCard("sky and stars", "appear inside His mouth", "vision", pair_id="B"),
                    MatchingCard("oceans and mountains", "fill Yaśodā with awe", "detail", pair_id="C"),
                    MatchingCard("astonished silence", "mother cannot speak at first", "feeling", pair_id="D"),
                    MatchingCard("vision closes", "ordinary playfulness returns", "turn", pair_id="E"),
                    MatchingCard("deeper maternal love", "result of the revelation", "result", pair_id="F"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Family wonder reflection",
                page_type="FAMILY_MISSION",
                instructions=[
                    "Talk about one beautiful thing in creation that fills your family with wonder.",
                    "Younger path: draw stars inside a soft oval of light.",
                    "Older path: write two sentences about Yaśodā's love increasing.",
                ],
                components=[
                    "One wonder we notice in the sky or earth",
                    "One way a parent or caregiver shows loving care",
                    "One thank-you we can offer after hearing this pastime",
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Number cards and draw soft stars in the yawn light.",
            "ages_9_13": "Explain how astonishment increased Yaśodā's affection.",
        },
        safety_note="PARENT HELP: Keep the mouth vision luminous and calm—no horror imagery.",
        completion_prompt="Retell the seven events, then share one wonder that increases your love for Kṛṣṇa.",
        review_questions=[
            "What did Yaśodā see when Kṛṣṇa yawned?",
            "How did her feelings change after the vision?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside the yawn-and-universe vision with Yaśodā. Do not merge this with the "
            "later dirt-eating mouth vision unless discussing separately. No invented verses."
        ),
        qa_requirements=[
            "seven yawn-vision sequence events",
            "wonder matching pairs",
            "family wonder reflection",
            "child-safe wording",
            "answers only in manifest",
        ],
    )


def _pack_013(plan: PlanRow) -> ActivityPack:
    connection = (
        "Garga Muni secretly performs the naming ceremony for Nanda's sons; Balarāma and "
        "Kṛṣṇa receive names whose meanings delight Nanda and Yaśodā "
        "(Krishna Book / Garga naming pastime)."
    )
    sequence = [
        SequenceCard(
            "Nanda invites Garga Muni with respect and care.",
            "Draw Nanda greeting the sage with folded hands.",
            1,
        ),
        SequenceCard(
            "The naming is kept quiet to avoid Kaṁsa's notice.",
            "Draw a private courtyard scene without royal spies.",
            2,
        ),
        SequenceCard(
            "Yaśodā brings the two boys for the sacred blessing.",
            "Draw mother presenting the infants gently.",
            3,
        ),
        SequenceCard(
            "Garga explains Balarāma's name and qualities.",
            "Draw the sage gesturing toward the elder baby.",
            4,
        ),
        SequenceCard(
            "Garga explains Kṛṣṇa's name and attractive qualities.",
            "Draw soft light around baby Kṛṣṇa as Garga speaks.",
            5,
        ),
        SequenceCard(
            "Nanda and Yaśodā listen with joyful faith.",
            "Draw parents smiling and offering flowers.",
            6,
        ),
        SequenceCard(
            "The family treasures the secret names with gratitude.",
            "Draw a peaceful family circle after the ceremony.",
            7,
        ),
    ]
    printed = [sequence[i] for i in (4, 1, 6, 0, 3, 5, 2)]
    return ActivityPack(
        activity_title="Garga Muni Names Kṛṣṇa and Balarāma",
        activity_type="MATCHING_GAME",
        send_mode="SEND_NOW",
        estimated_minutes=20,
        parent_effort="Low: help younger children match names and order the ceremony.",
        learning_goal="Match naming details and order Garga's secret ceremony with Nanda and Yaśodā.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Names and meanings matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each left item to its right meaning from the pastime.",
                    "Younger path: draw lines. Older path: write one sentence for each pair.",
                ],
                components=[
                    MatchingCard("Garga Muni", "performs the secret naming", "sage", pair_id="A"),
                    MatchingCard("Nanda Mahārāja", "hosts the quiet ceremony", "father", pair_id="B"),
                    MatchingCard("Mother Yaśodā", "brings the boys for blessing", "mother", pair_id="C"),
                    MatchingCard("Balarāma", "elder brother whose name Garga explains", "name", pair_id="D"),
                    MatchingCard("Kṛṣṇa", "younger brother praised for attracting all", "name", pair_id="E"),
                    MatchingCard("secret ceremony", "protects the family from Kaṁsa's notice", "care", pair_id="F"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the naming ceremony in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "The seven cards are shuffled on purpose.",
                    "Number them in true story order.",
                    "Circle the card where Garga explains Kṛṣṇa's name.",
                ],
                components=printed,
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Match names with pictures and number the cards.",
            "ages_9_13": "Explain why the naming was kept private.",
        },
        safety_note="PARENT HELP: Keep Kaṁsa only as a reason for secrecy—no violent scenes.",
        completion_prompt="Share one matched pair and retell why Garga named both brothers carefully.",
        review_questions=[
            "Why was the naming ceremony kept quiet?",
            "Who explained the meanings of the boys' names?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside Garga's naming for Nanda's household. Summarize name meanings in plain "
            "English paraphrase; do not invent Sanskrit verses or extra ritual details."
        ),
        qa_requirements=[
            "six naming matching pairs",
            "seven ceremony sequence events",
            "secret-naming context",
            "child-safe wording",
            "answers only in manifest",
        ],
    )


def _pack_014(plan: PlanRow) -> ActivityPack:
    connection = (
        "Toddler Kṛṣṇa crawls with ankle bells, steals butter and sweets in playful mischief, "
        "and the mothers of Vraja watch with affectionate laughter "
        "(Krishna Book / crawling adventures)."
    )
    return ActivityPack(
        activity_title="Crawling Adventures Mini-Drama",
        activity_type="MINI_DRAMA",
        send_mode="PARENT_GUIDED",
        estimated_minutes=20,
        parent_effort="Low: help children act crawling play and discuss gentle mischief.",
        learning_goal="Act crawling mischief with distinct roles and match playful details from the pastime.",
        story_connection=connection,
        materials=["pencil", "four household props"],
        pages=[
            ActivityPage(
                page_title="Crawling adventure role cards",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role and read the paraphrase line.",
                    "Use a distinct action and prop—no identical motions.",
                    "Keep mischief charming and kind, never mean.",
                ],
                components=[
                    RolePlayCard(
                        "Narrator",
                        "Toddler Kṛṣṇa crawls through Vraja with jingling bells and sparkling eyes.",
                        "Tap a steady rhythm to start each short scene.",
                        "wooden spoon as bell cue",
                    ),
                    RolePlayCard(
                        "Baby Kṛṣṇa",
                        "I crawl toward the butter pots and smile as if nothing is missing.",
                        "Crawl two steps and peek behind open hands.",
                        "small empty yogurt cup",
                    ),
                    RolePlayCard(
                        "Cowherd boy friend",
                        "Follow Him—He is heading for the sweets again!",
                        "Tip-toe behind Kṛṣṇa and point toward the pots.",
                        "paper peacock feather shape",
                    ),
                    RolePlayCard(
                        "Gopī mother",
                        "Who took a handful from my pot? Those tiny footprints give it away.",
                        "Place hands on hips, then laugh kindly.",
                        "kitchen towel",
                    ),
                    RolePlayCard(
                        "Yaśodā",
                        "Come, my restless child—wash those butter-shiny fingers.",
                        "Kneel and mime wiping little hands with care.",
                        "soft napkin",
                    ),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Crawling mischief matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each playful detail to its meaning.",
                    "Talk about affection behind the mothers' complaints.",
                ],
                components=[
                    MatchingCard("ankle bells", "announce Kṛṣṇa's crawling arrival", "sound", pair_id="A"),
                    MatchingCard("butter pots", "tempting target of toddler play", "object", pair_id="B"),
                    MatchingCard("tiny footprints", "clues left for laughing mothers", "clue", pair_id="C"),
                    MatchingCard("cowherd friends", "join the playful chase", "friends", pair_id="D"),
                    MatchingCard("Yaśodā's care", "washes hands and hugs Him", "mother", pair_id="E"),
                    MatchingCard("affectionate laughter", "love behind the scolding", "feeling", pair_id="F"),
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Act crawling and match with picture clues.",
            "ages_9_13": "Explain how playful mischief still shows loving relationships.",
        },
        safety_note="PARENT HELP: Keep theft scenes playful—no real taking of food without permission.",
        completion_prompt="Perform one crawling scene, then name one kind response from Yaśodā.",
        review_questions=[
            "What sounds announced toddler Kṛṣṇa's arrival?",
            "How did the mothers respond to His butter mischief?",
        ],
        answer_key=[
            "ankle bells — announce Kṛṣṇa's crawling arrival",
            "butter pots — tempting target of toddler play",
            "tiny footprints — clues left for laughing mothers",
            "cowherd friends — join the playful chase",
            "Yaśodā's care — washes hands and hugs Him",
            "affectionate laughter — love behind the scolding",
        ],
        parent_note=(
            "Stay inside crawling and butter-mischief play. Do not escalate into later tying "
            "or demon episodes. No invented Sanskrit verses."
        ),
        qa_requirements=[
            "five distinct role cards",
            "six crawling matching pairs",
            "playful child-safe mischief",
            "no placeholder role lines",
            "answers only in manifest",
        ],
    )


def _pack_015(plan: PlanRow) -> ActivityPack:
    connection = (
        "The gopīs complain to Yaśodā that Kṛṣṇa steals butter; their complaints reveal "
        "charm and affection for the butter thief "
        "(Krishna Book / gopīs complain about butter theft)."
    )
    sequence = [
        SequenceCard(
            "Kṛṣṇa and friends eye the hanging butter pots.",
            "Draw pots hanging high and children looking up eagerly.",
            1,
        ),
        SequenceCard(
            "They form a human tower and tip a pot.",
            "Draw friends helping carefully—no dangerous falls.",
            2,
        ),
        SequenceCard(
            "Butter is shared with monkeys and laughing friends.",
            "Draw butter on cheeks and happy monkeys nearby.",
            3,
        ),
        SequenceCard(
            "Gopīs discover empty pots and sticky footprints.",
            "Draw surprised mothers pointing at footprints.",
            4,
        ),
        SequenceCard(
            "They go to Yaśodā with lively complaints.",
            "Draw gopīs speaking animatedly at Yaśodā's door.",
            5,
        ),
        SequenceCard(
            "Yaśodā listens while Kṛṣṇa looks charmingly innocent.",
            "Draw Yaśodā listening and Kṛṣṇa with butter-shine cheeks.",
            6,
        ),
        SequenceCard(
            "Affection softens the scolding into loving laughter.",
            "Draw everyone smiling as the complaint turns tender.",
            7,
        ),
    ]
    printed = [sequence[i] for i in (5, 1, 4, 0, 6, 2, 3)]
    return ActivityPack(
        activity_title="Gopīs Complain About Butter Theft",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=20,
        parent_effort="Low: help order cards and act the cheerful complaint scene.",
        learning_goal="Order the butter-theft complaint and act how charm meets motherly love.",
        story_connection=connection,
        materials=["pencil", "crayons", "three household props"],
        pages=[
            ActivityPage(
                page_title="Put the butter complaint in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the seven shuffled cards in story order.",
                    "Draw one playful detail on each card.",
                    "Circle the card where the gopīs complain to Yaśodā.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Butter complaint role cards",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role and speak the paraphrase line.",
                    "Keep complaints cheerful—never harsh or mean.",
                    "End with affectionate laughter together.",
                ],
                components=[
                    RolePlayCard(
                        "Narrator",
                        "The gopīs arrive with lively news about missing butter pots.",
                        "Invite each speaker forward in turn.",
                        "story cards",
                    ),
                    RolePlayCard(
                        "Gopī neighbor",
                        "Mother Yaśodā, your son climbed for our hanging pots again!",
                        "Point upward then show empty hands.",
                        "empty paper cup",
                    ),
                    RolePlayCard(
                        "Second gopī",
                        "He left sticky footprints and shared butter with the monkeys.",
                        "Trace imaginary footprints on the floor.",
                        "crayon",
                    ),
                    RolePlayCard(
                        "Yaśodā",
                        "Tell me gently—what did my restless boy do this time?",
                        "Sit tall and listen with a half-smile.",
                        "folding fan or napkin",
                    ),
                    RolePlayCard(
                        "Kṛṣṇa",
                        "I only wanted to taste a little and make My friends happy.",
                        "Wipe cheeks with a shy, charming grin.",
                        "yellow paper circle as butter",
                    ),
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Number cards and act the complaint with laughter.",
            "ages_9_13": "Explain how love softens the gopīs' complaints.",
        },
        safety_note="PARENT HELP: No real climbing on furniture for pots; mime the tower safely on the floor.",
        completion_prompt="Retell the seven events, then share one kind way to handle a playful mistake.",
        review_questions=[
            "What evidence did the gopīs bring to Yaśodā?",
            "How did affection change the mood of the complaint?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside butter theft and gopī complaints to Yaśodā. Keep charm central; "
            "do not invent punishments or Sanskrit verses."
        ),
        qa_requirements=[
            "seven butter-complaint sequence events",
            "five distinct role cards",
            "affectionate child-safe tone",
            "shuffled print order",
            "answers only in manifest",
        ],
    )


def _pack_016(plan: PlanRow) -> ActivityPack:
    connection = (
        "Kṛṣṇa eats clay; friends tell Yaśodā; when she asks Him to open His mouth she "
        "sees the universe and stands amazed "
        "(Krishna Book / Kṛṣṇa eats dirt pastime)."
    )
    sequence = [
        SequenceCard(
            "Kṛṣṇa plays outside and tastes a bit of clay.",
            "Draw toddler Kṛṣṇa near soft earth—no muddy mess fright.",
            1,
        ),
        SequenceCard(
            "Cowherd friends hurry to tell Mother Yaśodā.",
            "Draw friends running with concerned but kind faces.",
            2,
        ),
        SequenceCard(
            "Yaśodā asks whether He really ate dirt.",
            "Draw mother kneeling and speaking gently.",
            3,
        ),
        SequenceCard(
            "Kṛṣṇa first denies it with a playful look.",
            "Draw a charming shake of the head—no stubborn meanness.",
            4,
        ),
        SequenceCard(
            "She asks Him to open His mouth so she can see.",
            "Draw Yaśodā pointing kindly toward His mouth.",
            5,
        ),
        SequenceCard(
            "Inside His mouth she beholds the entire universe.",
            "Draw soft stars and worlds in luminous light.",
            6,
        ),
        SequenceCard(
            "Yaśodā stands amazed; her love deepens in wonder.",
            "Draw mother astonished yet embracing her child.",
            7,
        ),
        SequenceCard(
            "Ordinary village life continues with renewed affection.",
            "Draw a peaceful courtyard after the vision closes.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (5, 0, 7, 2, 4, 1, 6, 3)]
    return ActivityPack(
        activity_title="Kṛṣṇa Eats Dirt",
        activity_type="MATCHING_GAME",
        send_mode="PARENT_GUIDED",
        estimated_minutes=18,
        parent_effort="Low: help match details and number the mouth-vision cards.",
        learning_goal="Match dirt-eating details and order how Yaśodā's amazement arose.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Dirt-eating pastime matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each left item to its right meaning.",
                    "Talk about truthfulness and motherly care.",
                ],
                components=[
                    MatchingCard("tasting clay", "friends notice Kṛṣṇa's play", "action", pair_id="A"),
                    MatchingCard("friends report", "they tell Yaśodā with concern", "friends", pair_id="B"),
                    MatchingCard("gentle question", "mother asks what happened", "mother", pair_id="C"),
                    MatchingCard("open mouth request", "Yaśodā wants to see inside", "request", pair_id="D"),
                    MatchingCard("universe vision", "worlds appear within His mouth", "vision", pair_id="E"),
                    MatchingCard("amazed love", "wonder increases her affection", "result", pair_id="F"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the dirt-eating pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one calm detail on each card.",
                    "Circle the card that shows the universe in His mouth.",
                ],
                components=printed,
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Match with pictures and number cards carefully.",
            "ages_9_13": "Explain how the mouth vision changed Yaśodā's understanding.",
        },
        safety_note="PARENT HELP: Remind children never to eat dirt or clay in real life.",
        completion_prompt="Retell the eight events, then say why Yaśodā was amazed.",
        review_questions=[
            "Who told Yaśodā that Kṛṣṇa ate dirt?",
            "What did she see when He opened His mouth?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside the dirt-eating and mouth-universe vision. Distinguish from the earlier "
            "yawn vision if children ask. No invented verses; keep imagery luminous."
        ),
        qa_requirements=[
            "six dirt-eating matching pairs",
            "eight sequence events",
            "real-life safety note about not eating dirt",
            "child-safe vision wording",
            "answers only in manifest",
        ],
    )


def _pack_017(plan: PlanRow) -> ActivityPack:
    connection = (
        "While Yaśodā churns butter, restless Kṛṣṇa overturns the pot; she tries to bind "
        "Him, but every rope is too short until He allows Himself to be bound as Dāmodara "
        "(Krishna Book / Mother Yaśodā binds Lord Kṛṣṇa)."
    )
    sequence = [
        SequenceCard(
            "Yaśodā churns butter with loving concentration.",
            "Draw mother at the churning pot with a peaceful face.",
            1,
        ),
        SequenceCard(
            "Hungry Kṛṣṇa asks for milk and becomes restless.",
            "Draw toddler Kṛṣṇa tugging her cloth gently.",
            2,
        ),
        SequenceCard(
            "He overturns a pot of yogurt in playful anger.",
            "Draw spilled yogurt—no broken glass or sharp mess.",
            3,
        ),
        SequenceCard(
            "Yaśodā decides to bind Him with a rope.",
            "Draw a soft rope coil in her hands.",
            4,
        ),
        SequenceCard(
            "Each rope she joins is still two fingers too short.",
            "Draw ropes end to end with a small gap remaining.",
            5,
        ),
        SequenceCard(
            "Seeing her effort, Kṛṣṇa allows Himself to be bound.",
            "Draw baby Kṛṣṇa standing still as the knot closes.",
            6,
        ),
        SequenceCard(
            "He stands as Dāmodara, bound at the waist in love.",
            "Draw a gentle waist-rope and a soft smile—no pain.",
            7,
        ),
        SequenceCard(
            "The pastime teaches that the Lord yields to pure devotion.",
            "Draw Yaśodā wiping tears of love, not fear.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (4, 0, 6, 2, 7, 1, 5, 3)]
    return ActivityPack(
        activity_title="Mother Yaśodā Binds Lord Kṛṣṇa",
        activity_type="MINI_DRAMA",
        send_mode="PARENT_GUIDED",
        estimated_minutes=22,
        parent_effort="Low: help act churning and rope scenes without real tight binding.",
        learning_goal="Act the Dāmodara pastime and order how love succeeded where force could not.",
        story_connection=connection,
        materials=["pencil", "soft scarf or yarn (loose only)", "story cards"],
        pages=[
            ActivityPage(
                page_title="Dāmodara role cards",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role and read the paraphrase line.",
                    "Use only a loose scarf—never tighten a rope on anyone.",
                    "Show that Kṛṣṇa allows binding out of love.",
                ],
                components=[
                    RolePlayCard(
                        "Narrator",
                        "Mother Yaśodā churns butter while restless Kṛṣṇa wants her attention.",
                        "Mime churning, then point to each next beat.",
                        "story cards",
                    ),
                    RolePlayCard(
                        "Yaśodā",
                        "Wait, my child—let me finish churning, then I will feed you.",
                        "Stir an imaginary pot with steady circles.",
                        "wooden spoon",
                    ),
                    RolePlayCard(
                        "Kṛṣṇa",
                        "I tip the yogurt pot, then stand still when Mother tries the rope.",
                        "Tip an empty cup sideways, then freeze with a soft smile.",
                        "empty yogurt cup",
                    ),
                    RolePlayCard(
                        "Neighbor gopī",
                        "The ropes keep coming up short—how is that possible?",
                        "Hold two yarn ends apart to show a small gap.",
                        "two yarn pieces",
                    ),
                    RolePlayCard(
                        "Cowherd child",
                        "Look—He let Himself be bound! Love is stronger than the rope.",
                        "Clap once softly and bow toward Yaśodā and Kṛṣṇa.",
                        "flower",
                    ),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the Dāmodara pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one gentle detail on each card.",
                    "Circle the card where Kṛṣṇa allows the binding.",
                ],
                components=printed,
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Act with a loose scarf and number the cards.",
            "ages_9_13": "Explain why devotion succeeded when the rope kept failing.",
        },
        safety_note="PARENT HELP: Never tighten rope or yarn around a child; use a loose scarf only for pretend.",
        completion_prompt="Perform the binding scene gently, then say what Dāmodara teaches about love.",
        review_questions=[
            "Why did the ropes keep coming up short?",
            "What changed when Kṛṣṇa allowed Himself to be bound?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside the churning and Dāmodara binding pastime. Emphasize consent of the Lord "
            "to devotion; avoid any real restraint. No invented Sanskrit verses."
        ),
        qa_requirements=[
            "five distinct Damodara role cards",
            "eight sequence events",
            "loose-scarf safety note",
            "love-over-force theme",
            "answers only in manifest",
        ],
    )


def _pack_018(plan: PlanRow) -> ActivityPack:
    connection = (
        "Bound as Dāmodara, Kṛṣṇa uproots the twin Yamala-arjuna trees; Nārada's curse on "
        "Nalakūvara and Maṇigrīva ends as the princes are liberated "
        "(Krishna Book / Nalakūvara and Maṇigrīva pastime)."
    )
    sequence = [
        SequenceCard(
            "Kṛṣṇa crawls between the twin Yamala-arjuna trees.",
            "Draw two tall trees with baby Kṛṣṇa between them.",
            1,
        ),
        SequenceCard(
            "The mortar and rope catch between the trunks.",
            "Draw a wooden mortar wedged gently—no snapping panic.",
            2,
        ),
        SequenceCard(
            "Kṛṣṇa pulls and the twin trees begin to fall.",
            "Draw trees leaning with soft dust—no crushing people.",
            3,
        ),
        SequenceCard(
            "From the fallen trees, two radiant princes appear.",
            "Draw two peaceful princes rising from soft light.",
            4,
        ),
        SequenceCard(
            "They remember Nārada's curse and their prideful past.",
            "Draw the princes with humble, grateful faces.",
            5,
        ),
        SequenceCard(
            "They offer prayers of thanks to child Kṛṣṇa.",
            "Draw folded hands and flower offerings.",
            6,
        ),
        SequenceCard(
            "Kṛṣṇa blesses them; they return toward their rightful place.",
            "Draw the princes departing upward in calm light.",
            7,
        ),
        SequenceCard(
            "Vraja gathers in wonder at the fallen twin trees.",
            "Draw villagers looking at stumps with amazement.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (3, 0, 6, 1, 7, 2, 5, 4)]
    return ActivityPack(
        activity_title="Nalakūvara and Maṇigrīva Liberated",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=20,
        parent_effort="Low: help order cards and discuss pride versus humility.",
        learning_goal="Order the Yamala-arjuna liberation and match curse-to-mercy details.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Put the twin-tree pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one calm detail on each card.",
                    "Circle the card where the princes appear.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Curse and liberation matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each left item to its right meaning.",
                    "Talk about how mercy follows humble remembrance.",
                ],
                components=[
                    MatchingCard("Yamala-arjuna trees", "forms holding the cursed princes", "place", pair_id="A"),
                    MatchingCard("Nārada's curse", "result of pride and disrespect", "cause", pair_id="B"),
                    MatchingCard("mortar and rope", "catch between the twin trunks", "detail", pair_id="C"),
                    MatchingCard("trees falling", "release the waiting princes", "event", pair_id="D"),
                    MatchingCard("Nalakūvara and Maṇigrīva", "liberated brothers who offer thanks", "who", pair_id="E"),
                    MatchingCard("child Kṛṣṇa's blessing", "restores them with mercy", "result", pair_id="F"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Humility family talk",
                page_type="FAMILY_MISSION",
                instructions=[
                    "Discuss one way pride can hurt friendship.",
                    "Younger path: draw two trees and soft light between them.",
                    "Older path: write two sentences about humility and mercy.",
                ],
                components=[
                    "One proud habit we want to soften",
                    "One respectful way to treat a guest or sage",
                    "One thank-you we can offer for mercy received",
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Number cards and draw peaceful princes in soft light.",
            "ages_9_13": "Explain how Nārada's curse became a path to liberation.",
        },
        safety_note="PARENT HELP: Show falling trees without people underneath or crushing injuries.",
        completion_prompt="Retell the eight events, then share one lesson about pride and mercy.",
        review_questions=[
            "What caught between the twin trees?",
            "Who were liberated when the trees fell?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside Yamala-arjuna and Nalakūvara–Maṇigrīva liberation. Keep prior pride "
            "child-safe (no intoxication details). No invented Sanskrit verses."
        ),
        qa_requirements=[
            "eight twin-tree sequence events",
            "six curse-mercy matching pairs",
            "humility family reflection",
            "child-safe falling-tree wording",
            "answers only in manifest",
        ],
    )


def _pack_019(plan: PlanRow) -> ActivityPack:
    connection = (
        "Among the calves, Kṛṣṇa protects His friends from Vatsāsura the calf demon and "
        "Bakāsura the crane demon "
        "(Krishna Book / Vatsāsura and Bakāsura pastimes)."
    )
    sequence = [
        SequenceCard(
            "Kṛṣṇa and friends take the calves out to graze.",
            "Draw happy boys and calves in a green field.",
            1,
        ),
        SequenceCard(
            "A dangerous calf form—Vatsāsura—moves among them.",
            "Draw one calf standing apart with a shadowed outline—no gore.",
            2,
        ),
        SequenceCard(
            "Kṛṣṇa seizes and whirls the calf demon away safely.",
            "Draw a swift spin with soft dust; friends step back calmly.",
            3,
        ),
        SequenceCard(
            "Later a huge crane—Bakāsura—appears near the water.",
            "Draw a large bird shape with a long beak—not bloody.",
            4,
        ),
        SequenceCard(
            "The crane catches Kṛṣṇa; friends cry out in fear.",
            "Draw friends calling while Kṛṣṇa stays composed inside.",
            5,
        ),
        SequenceCard(
            "Kṛṣṇa becomes hot like fire; the crane releases Him.",
            "Draw warm light around Kṛṣṇa as the beak opens.",
            6,
        ),
        SequenceCard(
            "He tears the crane's beak apart and ends the threat.",
            "Draw a clean break of the beak with no graphic detail.",
            7,
        ),
        SequenceCard(
            "Friends and calves rejoice; Kṛṣṇa leads them home safely.",
            "Draw a joyful return path with calves and garlands.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (2, 5, 0, 6, 1, 7, 3, 4)]
    return ActivityPack(
        activity_title="Vatsāsura and Bakāsura",
        activity_type="MINI_DRAMA",
        send_mode="PARENT_GUIDED",
        estimated_minutes=22,
        parent_effort="Low: keep demon play symbolic and celebrate protection.",
        learning_goal="Act how Kṛṣṇa protects friends from calf and crane threats, then order the events.",
        story_connection=connection,
        materials=["pencil", "four household props"],
        pages=[
            ActivityPage(
                page_title="Protector role cards",
                page_type="ROLE_PLAY_CARDS",
                instructions=[
                    "Choose a role and speak the paraphrase line.",
                    "Keep demon roles symbolic—no scary chasing of younger children.",
                    "End every scene with friends safe beside Kṛṣṇa.",
                ],
                components=[
                    RolePlayCard(
                        "Narrator",
                        "In the pastures, Kṛṣṇa watches both calves and friends with care.",
                        "Sweep an arm across the play space to set the field.",
                        "story cards",
                    ),
                    RolePlayCard(
                        "Kṛṣṇa",
                        "I protect My friends from the false calf and the crane.",
                        "Step between friends and danger with calm hands raised.",
                        "paper flute",
                    ),
                    RolePlayCard(
                        "Cowherd friend",
                        "Stay close—something strange is moving among the calves!",
                        "Gather other children behind Kṛṣṇa.",
                        "small stick as herding staff",
                    ),
                    RolePlayCard(
                        "Vatsāsura",
                        "I hide in a calf form, but I cannot overcome Kṛṣṇa.",
                        "Crouch once, then freeze when Kṛṣṇa turns toward you.",
                        "brown paper calf mask shape",
                    ),
                    RolePlayCard(
                        "Bakāsura",
                        "My long beak cannot hold the Lord when He blazes with power.",
                        "Open arms wide like a beak, then open them fully to release.",
                        "two paper plates as beak halves",
                    ),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Put the pasture protections in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one child-safe detail on each card.",
                    "Circle the card that shows friends rejoicing safely.",
                ],
                components=printed,
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Act protection with calm motions and number cards.",
            "ages_9_13": "Compare how Kṛṣṇa handled the calf threat and the crane threat.",
        },
        safety_note="PARENT HELP: No choking games, no real beak traps, no graphic tearing—keep symbolic.",
        completion_prompt="Perform both protections, then name one way friends stayed close to Kṛṣṇa.",
        review_questions=[
            "How did Kṛṣṇa stop Vatsāsura among the calves?",
            "What happened when Bakāsura caught Kṛṣṇa?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Combine Vatsāsura then Bakāsura in child-safe form. Soften violent verbs; focus on "
            "protection and reunion. No invented Sanskrit verses."
        ),
        qa_requirements=[
            "five distinct protector role cards",
            "eight pasture sequence events",
            "child-safe demon wording",
            "no placeholder role lines",
            "answers only in manifest",
        ],
    )


def _pack_020(plan: PlanRow) -> ActivityPack:
    connection = (
        "Aghāsura appears as a huge snake; the cowherd boys enter his mouth thinking it a cave; "
        "Kṛṣṇa enters and saves all His friends "
        "(Krishna Book / Aghāsura pastime)."
    )
    sequence = [
        SequenceCard(
            "Kṛṣṇa and friends wander near the forest path.",
            "Draw boys with calves on a bright path.",
            1,
        ),
        SequenceCard(
            "Aghāsura stretches as a mountain-like snake.",
            "Draw a long cave-shaped mouth—no dripping gore.",
            2,
        ),
        SequenceCard(
            "Friends think the open mouth is a wonderful cave.",
            "Draw curious boys pointing toward the dark opening.",
            3,
        ),
        SequenceCard(
            "They enter with the calves while Kṛṣṇa watches carefully.",
            "Draw friends walking in; Kṛṣṇa pauses outside thoughtfully.",
            4,
        ),
        SequenceCard(
            "Kṛṣṇa enters to rescue everyone inside.",
            "Draw Kṛṣṇa stepping into soft shadow with determined calm.",
            5,
        ),
        SequenceCard(
            "He expands and ends the snake demon's power.",
            "Draw warm light filling the cave—no graphic injury.",
            6,
        ),
        SequenceCard(
            "All friends and calves come out safe and joyful.",
            "Draw a stream of smiling boys and calves exiting.",
            7,
        ),
        SequenceCard(
            "They praise Kṛṣṇa's protection and continue their play.",
            "Draw a thankful circle around Kṛṣṇa with garlands.",
            8,
        ),
    ]
    printed = [sequence[i] for i in (4, 1, 7, 0, 5, 2, 6, 3)]
    return ActivityPack(
        activity_title="Aghāsura — Kṛṣṇa Saves All",
        activity_type="STORY_SEQUENCE",
        send_mode="PARENT_GUIDED",
        estimated_minutes=20,
        parent_effort="Low: help order cards and discuss staying close to protection.",
        learning_goal="Order the Aghāsura rescue and match how Kṛṣṇa saved every friend.",
        story_connection=connection,
        materials=["pencil", "crayons"],
        pages=[
            ActivityPage(
                page_title="Put the Aghāsura pastime in order",
                page_type="STORY_SEQUENCE_CARDS",
                instructions=[
                    "Number the eight shuffled cards in story order.",
                    "Draw one calm rescue detail on each card.",
                    "Circle the card where everyone exits safely.",
                ],
                components=printed,
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Rescue matching",
                page_type="MATCHING_CARDS",
                instructions=[
                    "Match each left item to its right meaning.",
                    "Talk about friendship, caution, and Kṛṣṇa's care.",
                ],
                components=[
                    MatchingCard("mountain-like snake", "Aghāsura's huge form", "demon", pair_id="A"),
                    MatchingCard("cave-like mouth", "mistaken path the friends enter", "mistake", pair_id="B"),
                    MatchingCard("calves and boys inside", "friends needing rescue", "friends", pair_id="C"),
                    MatchingCard("Kṛṣṇa enters", "He goes in to save them", "action", pair_id="D"),
                    MatchingCard("expanding light", "ends the demon's power safely", "rescue", pair_id="E"),
                    MatchingCard("joyful exit", "everyone returns unharmed", "result", pair_id="F"),
                ],
                story_connection=connection,
            ),
            ActivityPage(
                page_title="Stay close reflection",
                page_type="FAMILY_MISSION",
                instructions=[
                    "Discuss one way your family stays close when exploring somewhere new.",
                    "Younger path: draw friends walking out of a soft cave of light.",
                    "Older path: write two sentences about Kṛṣṇa's protective friendship.",
                ],
                components=[
                    "One place we explore only with a trusted adult",
                    "One friend we look after carefully",
                    "One thank-you for protection we received",
                ],
                story_connection=connection,
            ),
        ],
        age_variants={
            "ages_6_8": "Number cards and draw friends exiting safely.",
            "ages_9_13": "Explain why Kṛṣṇa entered after His friends and how all were saved.",
        },
        safety_note="PARENT HELP: No real hiding in enclosed dark spaces; keep the cave symbolic on paper.",
        completion_prompt="Retell the eight events, then share one way Kṛṣṇa protects His friends.",
        review_questions=[
            "Why did the friends enter Aghāsura's mouth?",
            "How did the pastime end for the cowherd boys?",
        ],
        answer_key=[card.event for card in sequence],
        parent_note=(
            "Stay inside Aghāsura rescue. Soften swallowing language; emphasize entrance-as-cave "
            "mistake and complete rescue. No invented Sanskrit verses."
        ),
        qa_requirements=[
            "eight Aghasura sequence events",
            "six rescue matching pairs",
            "family stay-close reflection",
            "child-safe cave wording",
            "answers only in manifest",
        ],
    )


PREFERRED_PACKS_010_020 = {
    "010": _pack_010,
    "011": _pack_011,
    "012": _pack_012,
    "013": _pack_013,
    "014": _pack_014,
    "015": _pack_015,
    "016": _pack_016,
    "017": _pack_017,
    "018": _pack_018,
    "019": _pack_019,
    "020": _pack_020,
}
