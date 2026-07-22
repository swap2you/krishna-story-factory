# Content Standard — Krishna Book Bedtime

Audience: children **ages 6–12**. Series: sequential **Krishna Book** pastimes only (`krishna_book_bedtime`). Do not mix unrelated pastimes.

Consolidates the former numbered content guide and `input/content_quality_rules.md`.

## Source faithfulness

- Do not invent new scripture claims or verbatim quotations unless explicitly supplied.  
- Stay inside the episode `source_reference` / `scripture_reference` and `must_include` / `must_avoid` boundaries.  
- Always include source reference in Scriptural Source + manifest.  
- Explain Sanskrit names simply.  
- Moral / lessons must come from the pastime, not generic filler.

## Tone and safety (child-safe)

- Warm, devotional, simple, respectful, vivid.  
- Short paragraphs; bedtime Krishna-katha, not a school essay.  
- Sensory detail without cheap fantasy.  
- No graphic violence; gentle treatment of imprisonment, fear, or persecution.  
- No romantic detail; no adult themes.  
- Avoid clumsy generic morals and meta-defensive “we will not hear about…” language.

## Story Format V2 (required sections)

Visible parent-facing order:

1. Greeting  
2. Series — Krishna Book Bedtime  
3. Story number and title  
4. Scriptural Source  
5. Recap (previous episode only; Story 001 uses series opening)  
6. Main Story (~700–950 words prod)  
7. Devotional Meaning  
8. Five Lessons (exactly five)  
9. Think About It (3–5 child questions; no printed answers)  
10. Five-Star Challenge (exactly five practical tasks)  
11. Bedtime Prayer (include Hare Kṛṣṇa mahā-mantra; calm close)  
12. Next Story Preview (no spoiling must_avoid events)  
13. Parent/Teacher Note (source + discussion suggestion)  

Hidden: Audio Narration (~650–850 spoken words), visual briefs, activity data. No YAML frontmatter on distributed `story.md`.

## Package and activities

- Exact eight final files (see [DRIVE_AND_PACKAGE_LAYOUT.md](DRIVE_AND_PACKAGE_LAYOUT.md)).  
- Activity sheet must be story-specific; Five-Star Challenge must be practical for children.  
- Story 002: do not call Kaṁsa “king”; use Devakī’s powerful brother / son of Ugrasena as required by source guards.

## Queue source of truth

- Metadata: `input/series_plan.csv` (+ master plan).  
- Runtime status: `tracking/queue_state.csv` only.
