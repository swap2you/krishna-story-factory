# Prabhupāda Vāṇī — Krishna Book Dictation Archive Design

## Intent

Separate product collection for complete available Śrīla Prabhupāda Krishna Book dictation recordings. Coverage is independent of Bhāva child Stories 001–035. Prefer calm listening truth over feature density.

## Information architecture

| Route | Role |
|---|---|
| `/prabhupada-vani` | Pillar landing; elevates Krishna Book dictation collection |
| `/prabhupada-vani/krishna-book` | Ordered catalog 00 + 01–90 with search/filter/progress |
| `/prabhupada-vani/krishna-book/[trackId]` | Focused listen page |
| Sticky mini-player | Continues across Vāṇī navigation |

API:

- `GET /api/v1/vani/krishna-book`
- `GET /api/v1/vani/krishna-book/{trackId}`
- `GET|HEAD /api/v1/vani/krishna-book/{trackId}/audio` (Range/206)
- `GET /api/v1/vani/krishna-book/{trackId}/waveform`

## UX decisions

- Extend existing Bhāva warm/calm visual language; no podcast-dashboard theme.
- One audio instance; no autoplay; resume/bookmark/complete in localStorage.
- Previous/next skip unavailable gaps.
- Label derivatives “Restored listening edition,” never HD/original.
- Related child stories are optional badges only.
- Media pages `noindex` until public redistribution rights are affirmatively approved.

## Data model

Canonical track IDs `00`–`90`. Manifests under `content-local/vani/krishna-book-dictations/v1/manifests/`. Originals immutable; restored listening editions + peaks separate. Rights states: `PRIVATE_REVIEW_ALLOWED`, `PUBLIC_REDISTRIBUTION_APPROVED`, `PUBLIC_RIGHTS_UNRESOLVED`.

## Acquisition / restoration / release

1. Union inventory across approved sources; primary acquired source: ISKCON Desire Tree direct MP3s.
2. Preserve SHA-256 originals; quarantine differing retries.
3. Conservative local FFmpeg restore (highpass + light `afftdn` + two-pass loudnorm).
4. Separate immutable bundle `bhava-vani-krishna-book-dictations-complete-v1.tar.gz` outside Git.
5. Stage 1 authenticated streaming with `PRIVATE_REVIEW_ALLOWED`. Public production blocked until affirmative rights.

## Accessibility

WCAG 2.2 AA expectations: keyboard, labels, contrast, reduced motion, touch targets, truthful transcript/source links (external only unless reuse authority exists).
