# Story 002 / 005 package repair backlog

Separate from the OpenAI TTS fallback pilot. Do **not** mix these repairs into the
OpenAI audio PR unless a defect directly blocks audio work.

## Current package status

| Story | Title | Eight-file contract | Production MP3 | Manifest audio_source |
|-------|-------|---------------------|----------------|------------------------|
| 002 | The Wedding and the Heavenly Voice | Present | Preserved | PRESERVED_EXISTING |
| 005 | Prayers by the Demigods for Lord Krishna in the Womb | Present | Preserved | SKIPPED_QUOTA_PRESERVE_EXISTING |

PASS scores in manifests are not independent proof of content correctness.

## Story 002 findings

1. Activity PDF page 3 contains generic template text such as
   “I will help in Narrator card's part of the story.”
2. Role-play cards are not meaningful child-ready dialogue.
3. Page 2 standees appear too placeholder-like.
4. Story contains invented dialogue/decorative content that should not be represented
   as direct scriptural quotation.
5. Poster heavenly voice uses an abstract glowing scribble; divine light without
   pseudo-writing would be cleaner (non-blocker).

## Story 005 findings

1. Poster appears to show Brahma with more than four visible heads.
2. Demigods appear ghost-like/translucent rather than exalted celestial beings.
3. Story includes unsupported invented details (heavenly garden meeting, Brahma
   calling everyone together, Narada playing a melody, Indra asking forgiveness,
   Candra/Varuna attendance as described, moon/wind gods bringing sweetness/air).
4. Invented paraphrases are enclosed in quotation marks.
5. “The prayers become a shield for her and for the Lord” is philosophically poor —
   the Supreme Lord does not require protection.
6. Sequence activity begins with a background condition rather than the first active
   scene event.

## Recommended later work

Create narrow repair PRs after the OpenAI TTS fallback is reviewed:

1. Story 002 activity dialogue / standee rewrite.
2. Story 005 poster + demigod visual fidelity repair.
3. Story 005 source-faithfulness text repair (remove invented quotations).
4. Sequence activity ordering fix for Story 005.
