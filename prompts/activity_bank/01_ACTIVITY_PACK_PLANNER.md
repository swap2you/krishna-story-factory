# Activity Pack Planner

Select one primary activity and one or two supporting mini-pages when useful.

Return strict ActivityPack JSON only (no markdown fences, no commentary).

Required fields:

* activity_title, activity_type, send_mode, estimated_minutes, parent_effort
* learning_goal, story_connection, materials, pages[], answer_key
* parent_note, qa_requirements

Each page requires:

* page_title, page_type, instructions[], components[], layout_hint, story_connection

Primary types:

PAPER_CRAFT, CUT_AND_BUILD, PUPPET_PLAY, MINI_DRAMA, ROLE_CARDS, STORY_SEQUENCE,
MATCHING_GAME, STORY_MAP, MAZE_OR_PATH, SORTING_GAME, PRAYER_OR_GRATITUDE_CRAFT,
FAMILY_MISSION, MEMORY_GAME, SIMPLE_BOARD_GAME, DRAW_AND_REFLECT, WORD_SEARCH,
CROSSWORD, COLORING_ONLY, QUICK_DISCUSSION

Page types:

STORY_MAP, STORY_SEQUENCE_CARDS, CUT_AND_BUILD_PARTS, ROLE_PLAY_CARDS, PUPPET_CARDS,
MAZE_OR_PATH, MATCHING_CARDS, SORTING_CARDS, MINI_BOARD_GAME, PRAYER_WHEEL,
GRATITUDE_GARLAND, DECISION_TREE, EMOTION_MAP, DRAW_AND_REFLECT, WORD_SEARCH,
CROSSWORD, FAMILY_MISSION, QUICK_DISCUSSION, ANSWER_KEY_INTERNAL_ONLY

Diversity:

* no identical primary type as the previous story
* WORD_SEARCH at most once in six stories
* heavy craft at most once in three stories
* written-only worksheet at most once in three stories
* rotate making, acting, solving, reflecting, family mission, mapping/sequencing

Favor source-specific activity hints from the master plan when present.
