# Activity Engine V2

Krishna Story Factory builds an `ActivityPack` for every episode, then renders a local
black-and-white `activity_sheet.pdf`. The coloring page stays a separate PNG.

## What an ActivityPack is

An internal JSON model with:

* `activity_title`, `activity_type`, `send_mode`
* `estimated_minutes` (10–30), `parent_effort`, `learning_goal`
* `story_connection`, `materials`, `pages[]`, `answer_key`
* `parent_note`, `qa_requirements`

Each page has `page_title`, `page_type`, `instructions`, `components`, `layout_hint`,
and a story-specific `story_connection`.

## Activity types

Primary types include crafts, cut-and-build, puppets/drama, sequence/map/matching,
mazes, family missions, reflection, word search/crossword, and quick discussion.

Simple types (`COLORING_ONLY`, `QUICK_DISCUSSION`) may be 1 page. Normal packs are 2–4 pages
(never more than 5).

## Page types

`STORY_MAP`, `STORY_SEQUENCE_CARDS`, `CUT_AND_BUILD_PARTS`, `ROLE_PLAY_CARDS`,
`PUPPET_CARDS`, `MAZE_OR_PATH`, `MATCHING_CARDS`, `SORTING_CARDS`, `MINI_BOARD_GAME`,
`PRAYER_WHEEL`, `GRATITUDE_GARLAND`, `DECISION_TREE`, `EMOTION_MAP`, `DRAW_AND_REFLECT`,
`WORD_SEARCH`, `CROSSWORD`, `FAMILY_MISSION`, `QUICK_DISCUSSION`,
`ANSWER_KEY_INTERNAL_ONLY` (never printed).

## Diversity rules

Tracked in `tracking/activity_history.csv` (runtime, gitignored):

* no identical primary type on consecutive stories
* `WORD_SEARCH` at most once in six stories
* heavy craft at most once in three stories
* written-only worksheet at most once in three stories
* rotate making / acting / solving / reflecting / family mission / mapping

Stories 001–003 use preferred source packs (prayer wheel, chariot build, truthfulness path).
Those preferred packs are source overrides and are not diversified away.

## QA rejects generic worksheets

Vision QA scores the rendered pages. Score must be ≥ 88. Failures for generic worksheets,
blank pages, missing cut lines, visible answer keys, or weak story connection trigger one
repair + PDF regenerate cycle.

Prompt bank: `prompts/activity_bank/00`–`08`.

## Rebuild only activity sheets

```powershell
python run_daily_story.py --mode prod --chapter 003 --rebuild-components activity --debug
```

Locked files (story, narration, poster, caption) stay unchanged.

## Tune page counts

* Prefer 2–4 pages for normal packs
* Keep crafts printable; split support activities onto extra pages instead of crowding
* Never exceed 5 pages

## Why coloring is separate

`coloring_page.png` is a poster-referenced line-art asset. Activity PDFs must not embed it.
Parents get coloring as its own printable.

## Parent send wording

Caption uses `send_mode`:

* `OPTIONAL` — optional family activity
* `WEEKEND_PROJECT` — weekend project
* `PARENT_GUIDED` — parent-guided activity
* `SEND_NOW` — ready to use today
