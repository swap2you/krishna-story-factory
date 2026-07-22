# Bhāva Portal — Product Requirements (v1 Local)

## Vision

**Bhāva** (`bhava.me`) is a calm, child-first, parent- and teacher-ready devotional learning portal. v1 ships locally around locked Krishna Book bedtime Stories **001–007**, with structure ready for Śrīmad-Bhāgavatam Cantos 1–12, Rāmāyaṇa, Caitanya literature, Prabhupāda Vāṇī, lectures, ślokas, activities, and a Bhakti Blog.

## Audiences

| Audience | Needs |
| --- | --- |
| Children (≈5–13) | Listen, read, color, do activities; large targets; no ads or tracking |
| Parents | Source trust, print/download, local notes, privacy clarity |
| ISKCON teachers | Age modes, class packs, answer keys separated from child view |
| Operator (local) | Factory Studio on loopback only; never public |

## Modes

1. **Public Library** — browse, listen, read, download/print; no login.
2. **Teacher Toolkit** — age-aware recommendations, printable class packs, classroom playlist.
3. **Factory Studio** — localhost-only operator console; invokes existing factory entry points through a narrow adapter.

## Non-negotiables

1. Bona fide source boundaries and review status remain visible.
2. Exact eight-file package contract unchanged.
3. `manifest.json` is authoritative; catalog indexes, never replaces.
4. Public learning vs private operations stay strictly split.
5. No child accounts, ads, analytics-by-default, or server-side child notes.
6. No story regeneration, queue advancement, scheduler trigger, Drive upload, or paid APIs during this portal build.
7. Contact page uses configured steward links; never invent a blank email.

## Primary navigation

Home · Library · For Teachers · Prabhupāda Vāṇī · Bhakti Blog · About · Contact

Future collections show polished coming-soon shells (not dead links).

## Story experience (must)

- Audio: waveform, play/pause, seek, ±15s, speeds 0.75–2×, volume, sleep timer, bookmark, resume, Media Session, download.
- Reading: sanitized Markdown, font size, sepia/dark/dyslexia modes, print, download.
- Activities/images: PDF view with fallback, poster + coloring pages, fullscreen, download/print.
- Notes: browser localStorage only, with privacy explanation and export/print.
- Source: exact references and review state; no unlicensed full-book mirroring.
- Śloka: zero-or-more slots; placeholders marked “not yet curated” — do not invent ślokas.

## Factory protection

Locked: `krishna_story_factory/`, `scripts/`, `tracking/`, `output/`, `input/`, `credentials/`.

Portal may add adapters and tests only. Stories 001–007, queue (008 pending), `main`/`master`/tags remain untouched by portal work.

## Success for local v1

- Catalog discovers Stories 001–007 from disk manifests.
- Public routes work without factory credentials.
- Studio actions default to demo/disabled unless an explicit local env flag enables them.
- Full automated gates + headed browser inspection pass on `feature/bhava-portal-v1`.
