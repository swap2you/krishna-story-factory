# Bhāva Stories 001–020 — Source / Śloka Evidence (V3)

Reviewer: Svarna Gauranga Das  
Evidence date: 2026-08-01  
Branch: `fix/bhava-001-020-v3-final-uat`

## Verification sources (in order)

1. `input/series_plan.csv` (`source_reference`, `scripture_reference`)
2. `docs/editorial/KRISHNA_BOOK_CHAPTERS_7_8_EVENT_BOUNDARY_REVIEW.md`
3. `docs/editorial/BHAVA_V1_1_SHLOKA_CANDIDATE_REPORT.md`
4. `apps/api/bhava_api/web_assets/reviewed_sources.py` / `reviewed_shlokas.py`
5. Vedabase chapter URLs for KB / SB companion verification (no invented verse text)

Rules applied:

- Exact SB verse start/end only when bona fide from `series_plan.csv` or editorial docs.
- Never invent Sanskrit, transliteration, translation, or purport.
- Stories 001 / 005 / 006 Śloka rows remain `review_status=not_applicable` (no separate verse selected).
- Chapter-framed rows carry an explicit reviewed deferral note.

## Evidence table

| Story | KB chapter | SB chapter | Verse start | Verse end | Vedabase URL | Verification source | Review status | Deferral reason |
|---|---|---|---|---|---|---|---|---|
| 001 | 1 | 10.1 | — | — | https://vedabase.io/en/library/sb/10/1/ | series_plan KB Ch.1; KB↔SB advent map | reviewed (Source); śloka `not_applicable` | No exact verse pin in series_plan for Story 001; chapter companion only |
| 002 | 1 | 10.1 | 27 | 55 | https://vedabase.io/en/library/sb/10/1/ | series_plan `SB 10.1.27-55` | reviewed | — (range bona fide; chapter URL for openable study link) |
| 003 | 1 | 10.1 | 56 | 61 | https://vedabase.io/en/library/sb/10/1/ | series_plan `SB 10.1.56-61` | reviewed | — |
| 004 | 1 | 10.1 | 62 | 69 | https://vedabase.io/en/library/sb/10/1/ | series_plan `SB 10.1.62-69` | reviewed | — |
| 005 | 2 | 10.2 | — | — | https://vedabase.io/en/library/sb/10/2/ | series_plan KB Ch.2 complete; KB↔SB map | reviewed (Source); śloka `not_applicable` | Complete-chapter story; no verse pin in series_plan |
| 006 | 3 | 10.3 | — | — | https://vedabase.io/en/library/sb/10/3/ | series_plan KB Ch.3 complete; KB↔SB map | reviewed (Source); śloka `not_applicable` | Complete-chapter story; no verse pin in series_plan |
| 007 | 4 | 10.4 | — | — | https://vedabase.io/en/library/sb/10/4/ | series_plan `SB 10.4 / Complete KB Ch.4` | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 008 | 5 | 10.5 | — | — | https://vedabase.io/en/library/sb/10/5/ | series_plan Complete KB Ch.5 | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 009 | 6 | 10.6 | — | — | https://vedabase.io/en/library/sb/10/6/ | series_plan `SB 10.6 / Complete KB Ch.6` | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 010 | 7 | 10.7 | — | — | https://vedabase.io/en/library/sb/10/7/ | series_plan event split + Ch.7–8 editorial review | reviewed | Event-framed (cart-breaking); verse numbers not pinned |
| 011 | 7 | 10.7 | — | — | https://vedabase.io/en/library/sb/10/7/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (Tṛṇāvarta); verse numbers not pinned |
| 012 | 7 | 10.7 | — | — | https://vedabase.io/en/library/sb/10/7/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (yawn / first mouth vision); verse numbers not pinned |
| 013 | 8 | 10.8 | — | — | https://vedabase.io/en/library/sb/10/8/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (Garga name-giving); verse numbers not pinned |
| 014 | 8 | 10.8 | — | — | https://vedabase.io/en/library/sb/10/8/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (crawling); verse numbers not pinned |
| 015 | 8 | 10.8 | — | — | https://vedabase.io/en/library/sb/10/8/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (butter complaints); verse numbers not pinned |
| 016 | 8 | 10.8 | — | — | https://vedabase.io/en/library/sb/10/8/ | series_plan + Ch.7–8 editorial review | reviewed | Event-framed (dirt-eating / 2nd vision); verse numbers not pinned |
| 017 | 9 | 10.9 | — | — | https://vedabase.io/en/library/sb/10/9/ | series_plan Complete KB Ch.9 | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 018 | 10 | 10.10 | — | — | https://vedabase.io/en/library/sb/10/10/ | series_plan Complete KB Ch.10 | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 019 | 11 | 10.11 | — | — | https://vedabase.io/en/library/sb/10/11/ | series_plan Complete KB Ch.11 | reviewed | Chapter-level only; no exact verse numbers in plan/docs |
| 020 | 12 | 10.12 | — | — | https://vedabase.io/en/library/sb/10/12/ | series_plan Complete KB Ch.12 | reviewed | Chapter-level only; no exact verse numbers in plan/docs |

## Primary KB Vedabase URLs

| Story | KB Vedabase |
|---|---|
| 001–004 | https://vedabase.io/en/library/kb/1/ |
| 005 | https://vedabase.io/en/library/kb/2/ |
| 006 | https://vedabase.io/en/library/kb/3/ |
| 007 | https://vedabase.io/en/library/kb/4/ |
| 008 | https://vedabase.io/en/library/kb/5/ |
| 009 | https://vedabase.io/en/library/kb/6/ |
| 010–012 | https://vedabase.io/en/library/kb/7/ |
| 013–016 | https://vedabase.io/en/library/kb/8/ |
| 017 | https://vedabase.io/en/library/kb/9/ |
| 018 | https://vedabase.io/en/library/kb/10/ |
| 019 | https://vedabase.io/en/library/kb/11/ |
| 020 | https://vedabase.io/en/library/kb/12/ |

## Śloka tab summary

| Stories | Śloka posture |
|---|---|
| 001, 005, 006 | `not_applicable` — no separate verse selected; Source tab carries KB + SB companion |
| 002–004 | Reviewed chapter-framed reference citing bona fide series_plan ranges; Sanskrit null |
| 007–020 | Reviewed chapter-framed companion with explicit verse-pin deferral; Sanskrit null |
