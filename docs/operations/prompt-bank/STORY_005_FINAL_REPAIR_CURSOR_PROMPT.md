# Story 005 Final Repair — Cursor Autonomous Prompt

Repository:
`C:\Development\Workspace\DevotionalRepo\krishna-story-factory`

Branch:
`fix/daily-idempotency-and-6am-scheduler`

PR:
`https://github.com/swap2you/krishna-story-factory/pull/3`

Goal:
Fix all verified Story 005, activity, Drive consistency, audio-validation, Git hygiene, and PR defects in one autonomous pass. Do not ask the user to run commands. Do not broadly redesign approved systems. Do not send WhatsApp or Telegram. Do not generate Story 006.

Locked:
- seven-file package contract
- runtime queue architecture
- same-day production guard design
- 6:00 AM scheduler design
- Google Drive folder-per-story architecture
- coloring-page architecture unless QA finds a hard mismatch
- 93-episode master plan
- WhatsApp/Telegram disabled

Verified defects:
1. PR #3 is open; branch is not merged.
2. Untracked prompt-bank ZIP/folder dirties the worktree.
3. Story 005 activity PDF is generic and sparse despite QA 91.
4. Drive copies of manifest/caption contain stale parent-folder links/PENDING state.
5. Story includes “the palace guards dozed off,” which belongs to the birth-night episode.
6. Prayer section is repetitive.
7. Sarasvati is named without clear support in the selected source scene.
8. Poster can imply a visible sky manifestation of Krishna/Vishnu although Krishna remains unseen within Devaki.
9. Audio lacks portable waveform silence/clipping validation.
10. Activity QA does not reject generic placeholders or retain evidence.

Canonical Story 005 source:
- Krishna Book Chapter 2
- Srimad-Bhagavatam 10.2.25–42
- Brahma and Shiva lead.
- Narada and other sages/demigods accompany them.
- Indra is explicitly supported by SB 10.2.25; Candra and Varuna are also named.
- Do not name Sarasvati unless the selected source brief explicitly supports her.
- They invisibly approach Devaki and offer prayers.
- Krishna remains unseen within Devaki.
- The prayers acclaim the Lord as true to His vow, the Supreme Truth, protector of devotees, and one who descends to reduce the burden of the world.
- They reassure Devaki not to fear Kamsa.
- They return to their heavenly homes.
- Do not include Krishna’s birth, sleeping guards, prison doors opening, four-armed appearance, Yamuna crossing, or Vasudeva carrying Krishna.

## A. Git/preflight

- Inspect `git status`, recent commits, `git diff main...HEAD`, and PR #3.
- Keep work on `fix/daily-idempotency-and-6am-scheduler`.
- Move useful prompt-bank Markdown files to `docs/operations/prompt-bank/` or move them outside the repo.
- Remove the ZIP from the repo working tree.
- Never commit output, runtime CSV rows, logs, `.env`, credentials, OAuth tokens, or `.work`.
- Run all tests through `.\.venv\Scripts\python.exe`.

## B. Repair Story 005

Repair only Story 005:
- remove the sleeping-guards line;
- replace unsupported Sarasvati naming with “other demigods”;
- keep Indra only when grounded in SB 10.2.25;
- reduce four repetitive prayer paragraphs to one or two progressive paragraphs;
- preserve truth, surrender, protection, descent, and reassurance;
- keep 700–1000 main-story words;
- explain “Supreme Personality of Godhead” once in child-friendly language;
- retain a non-empty bedtime reflection question;
- do not invent direct scripture quotations.

Regenerate:
- `story.md`
- `narration.mp3`
- `manifest.json`
- `whatsapp_caption.txt` when needed

## C. Correct poster iconography

Regenerate only `story_poster.png`.

Required:
- Devaki with sacred effulgence centered around her womb/heart;
- Brahma clearly four-headed;
- Shiva recognizable;
- Narada may carry vina;
- other demigods remain supporting;
- Krishna is not shown as a separate visible sky figure;
- no central young crowned sky deity emitting the main light;
- no birth scene or sleeping guards;
- devotional, cinematic, child-safe;
- QA >= 90;
- source/iconography QA explicitly passes.

Keep `coloring_page.png` if it remains source-faithful. Regenerate it only if vision QA finds a hard mismatch.

## D. Replace the activity with a true 3-page Story 005 ActivityPack

Title:
`The Secret Prayer Gathering`

Page 1 — Who Came to Pray?
- matching cards:
  - Brahma — leads the demigods
  - Shiva — joins the prayers
  - Narada — great sage and devotee
  - other demigods — offer respectful prayers
  - Devaki — carries Krishna within her
- younger path: draw lines/cut-and-match
- older path: write one reason each figure came

Page 2 — Put the Prayer Scene in Order
Print six actual shuffled cards:
1. Krishna remains unseen within Devaki.
2. Brahma, Shiva, Narada, and the demigods arrive invisibly.
3. They offer obeisances to the Lord.
4. They praise Him as true to His vow and the Supreme Truth.
5. They ask Him to protect devotees and reassure Devaki.
6. They return to their heavenly homes.

- answer order only in manifest
- no generic labels such as “Story begins” or “A problem appears”

Page 3 — My Lotus Prayer
Five petals:
- Someone I want Krishna to protect
- A fear I can place before Krishna
- Something I am thankful for
- One kind action I will do
- A prayer for the world

- younger path: draw
- older path: write one or two sentences
- one family discussion prompt
- safety note if cutting is required

Requirements:
- 3 meaningful pages
- no page below 40% content
- no repeated boilerplate
- no raw JSON/dict text
- no embedded coloring page
- Activity QA >= 90
- semantic QA evidence retained under ignored `.work/qa/`

## E. Strengthen activity QA generally

Hard reject:
- generic labels: Story begins, A problem appears, A helpful choice, The turning point, The result, The lesson
- sequence cards without concrete events
- page under 35% meaningful content
- repeated boilerplate across pages
- activity page with no story entities/source concepts
- answer key equal to printed order
- manifest QA score without retained review evidence

Require:
- actual story entities/events on every page
- younger and older participation paths
- shuffled sequence cards
- answers hidden in manifest
- accurate send mode and parent effort

Add regression tests using Story 005.

## F. Fix Drive transaction order

Correct upload flow:
1. generate provisional package;
2. create/reuse per-story folder;
3. obtain actual folder ID/link;
4. update local manifest and caption with final link/state;
5. upload/replace final manifest and caption;
6. read them back from Drive;
7. verify both point to the containing folder and no PENDING state;
8. only then mark upload PASS and queue done.

For Story 005, reuse:
`1qqox6hHQzMR3HQU12TQv2xRb2IUlbXU3`

Replace only changed files. Confirm exactly seven Drive files remain.

## G. Add portable audio waveform validation

Add a pure-Python decoder such as `miniaudio` plus `numpy`.

Validate:
- MP3 decodes;
- duration matches;
- longest near-silence;
- peak amplitude;
- clipping ratio;
- no truncation.

Record:
- peak
- clipping_ratio
- longest_silence_seconds
- waveform_validation_status

Do not regenerate audio unless waveform checks fail.

Add Windows and Ubuntu tests.

## H. Preserve scheduler and daily guard

Keep:
- one successful normal prod story per local day;
- second same-day run returns `SKIPPED_ALREADY_COMPLETED_TODAY`;
- scheduler enabled at 6:00 AM;
- venv Python;
- `--mode prod`;
- no `--force`;
- IgnoreNew;
- timeout/retries/logging;
- messaging disabled;
- Drive enabled.

Do not trigger the scheduler manually.

## I. Validate and update PR #3

Run all local tests and Windows/Ubuntu CI.

Rebuild only Story 005 affected components.

Validate:
- source boundary PASS
- audio waveform PASS
- poster iconography PASS
- coloring PASS
- activity 3 pages and QA >= 90
- exactly seven local files
- exactly seven Drive files
- Drive manifest/caption read-back links correct
- queue remains 005 done and 006 pending
- same-day guard PASS
- scheduler Ready at 6:00 AM
- no accidental untracked files

Commit only source/tests/docs/prompts/scripts.
Push branch and update PR #3.
Do not merge yet; leave it ready for independent reviews.

Print:

STORY 005 FINAL REPAIR — CURSOR

Tests:
Windows CI:
Ubuntu CI:
Story Source:
Story Words:
Audio Duration:
Audio Waveform:
Poster QA:
Coloring QA:
Activity Title:
Activity Pages:
Activity QA:
Drive Seven Files:
Drive Manifest Link:
Drive Caption Link:
Daily Guard:
Scheduler:
Next Pending:
Git Working Tree:
PR:
Overall:
