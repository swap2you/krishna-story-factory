# Krishna Story Portal — Product, UX and Architecture Blueprint

## 1. Product vision

Build a public, devotional digital-learning library for children, parents and ISKCON teachers. The first collection is **Krishna Book Bedtime Stories**. The long-term library expands to Śrīmad-Bhāgavatam Cantos 1–12, Rāmāyaṇa, Śrī Caitanya-caritāmṛta, Caitanya-bhāgavata, Śrīla Prabhupāda’s life and teachings, lectures, ślokas, worksheets and teacher resources.

The product must preserve the already-working Krishna Story Factory. The new application is a separate presentation and operations layer. It reads the existing eight-file packages and invokes the existing production command through a narrow, safe interface. It does not rewrite the generation engine.

## 2. Non-negotiable principles

1. **Bona fide first:** Every story must retain source boundaries, references, reviewer status and correction history.
2. **Children first:** Simple navigation, large targets, calm motion, no ads, no social feed and no manipulative rewards.
3. **Parent and teacher visibility:** Activities, answers, source references, print controls and age guidance are always easy to find.
4. **Public learning, private operations:** Public content needs no login. Story generation, queue editing, Drive synchronization and scheduler controls stay local/private.
5. **Exact-package compatibility:** The existing eight-file contract remains unchanged.
6. **Progressive scale:** Local filesystem and SQLite first; PostgreSQL and object storage later through adapters.
7. **No source mirroring without permission:** Show references, approved excerpts and links. Do not republish substantial BBT text or artwork without written permission.

## 3. Product modes

### A. Public Library
For children, parents and teachers. Read, listen, view, print and download.

### B. Teacher Toolkit
Lesson planning, age filters, answer keys, activity bundles, print packs and classroom playlists.

### C. Local Factory Studio
Private localhost-only operator console. Run one story, inspect queue, validate packages, upload to Drive, view logs and control the scheduler. This must never be exposed publicly without authentication and authorization.

## 4. Information architecture

- Home
- Library
  - Krishna Book
  - Śrīmad-Bhāgavatam
    - Canto 1 … Canto 12
  - Rāmāyaṇa
  - Śrī Caitanya-caritāmṛta
  - Caitanya-bhāgavata
  - Śrīla Prabhupāda
  - Lectures
- Story
  - Listen
  - Read
  - Activities
  - Coloring
  - Ślokas
  - Source
  - Teacher Notes
- Playlists / Bookmarks
- Teacher Toolkit
- Downloads / Print Center
- About and Review Standards
- Local Factory Studio
  - Dashboard
  - Generate Story
  - Queue
  - QA Review
  - Package Explorer
  - Drive Sync
  - Scheduler
  - Logs and Health

## 5. Core screens

### 5.1 Home / Divine Library
Hero artwork, continue-listening card, current collection progress, latest story, featured activities, scripture collections and “coming next.”

### 5.2 Krishna Book Collection
Chapter timeline, story cards, filters by age/activity/status, progress through the book and a source-boundary map.

### 5.3 Story Detail
Persistent audio player plus tabs for Read, Activities, Coloring, Ślokas, Source and Teacher Notes. Every asset has view, download and print actions.

### 5.4 Full-screen Listening
Large artwork, waveform, scrubber, ±15 seconds, 0.75–2× speed, sleep timer, queue, bookmark and next story. No autoplay into unrelated content.

### 5.5 Reading Mode
Beautiful markdown rendering, adjustable font size, dyslexia-friendly mode, dark/sepia themes, section navigation and print.

### 5.6 Activity Workspace
Embedded PDF, page thumbnails, print all, download, simple/detailed age pathways and parent answer key.

### 5.7 Śloka Learning
Sanskrit, transliteration, word-for-word meaning, translation, audio repetition, hide/reveal memorization and printable cards.

### 5.8 Source Reader
Exact source title, chapter, start/end boundary, approved excerpt if permission permits, and “Open in Vedabase.” Never silently copy an entire copyrighted book.

### 5.9 Teacher Toolkit
Build a class pack from stories, audio, coloring, activities and ślokas. Export one printable PDF bundle later.

### 5.10 Local Factory Dashboard
Next pending story, recent runs, scheduler state, Drive state, provider health, queue progress and validation alerts.

### 5.11 Generate Story Wizard
Preflight → source boundary → cost/provider preview → generate → QA → human review → Drive upload → queue advancement. Each stage is explicit and resumable.

### 5.12 Review Studio
Side-by-side story, source checklist, audio player, visual gallery, PDF, manifest and reviewer decisions. No publish button until all release gates pass.

## 6. Recommended architecture

### Existing locked core
- `krishna_story_factory/`
- current scripts, queue, scheduler and exact eight-file packages
- current provider, validation, Drive and atomic-swap logic

### New web layer
- `apps/web`: Next.js App Router, TypeScript, responsive PWA
- `apps/api`: FastAPI gateway around the existing Python package
- `packages/ui`: devotional design system
- `packages/contracts`: generated TypeScript/Python schemas
- `data/catalog`: indexed read model
- `infra`: local and cloud adapters

### Local deployment
- Web: `localhost:3000`
- API: `localhost:8000`
- SQLite catalog
- local filesystem asset adapter
- Drive adapter for canonical published packages
- factory actions restricted to loopback interface

### Public deployment
- Next.js public web app
- FastAPI service
- PostgreSQL
- S3-compatible object storage or approved Drive publication adapter
- CDN for media
- no public operator endpoints
- read-only public API

## 7. Data model

- `Collection`
- `Work`
- `Volume`
- `Chapter`
- `PassageBoundary`
- `Story`
- `StoryVersion`
- `Asset`
- `Activity`
- `Shloka`
- `SourceReference`
- `ReviewDecision`
- `Publication`
- `Playlist`
- `QueueItem`
- `JobRun`
- `ProviderUsage`
- `DrivePublication`

The manifest remains authoritative for package facts. The catalog indexes manifests; it does not replace them.

## 8. Design system

- Primary: midnight blue
- Accent: warm gold
- Supporting: saffron, cream, lotus pink, tulasī green
- Body type: highly readable humanist sans-serif
- Display type: restrained devotional serif
- 8-point spacing grid
- 44-pixel minimum touch targets
- reduced-motion support
- WCAG 2.2 AA
- no flashing, cluttered gamification or advertisement surfaces

## 9. Safety and privacy

For the public children’s site, collect no child names, photos, audio, email, precise location, chat messages or behavioral advertising data in the first release. Bookmarks and progress should be device-local. Parent-submitted work belongs in the existing parent-managed WhatsApp workflow, not the public site.

## 10. Source and permissions policy

- Link to Vedabase for the complete source.
- Store exact chapter and passage boundaries.
- Use only brief approved excerpts until BBT permission is documented.
- Store permission records and copyright notices.
- Never scrape or mirror the complete Vedabase library.
- Treat embeddings as optional; many sites restrict framing and copyright permission is separate from technical embeddability.

## 11. Delivery phases

### Phase 0 — Protection
Freeze core contracts, add architecture decision records, establish adapter boundaries and create golden end-to-end tests.

### Phase 1 — Read-only local portal
Home, collection, story page, audio, markdown, PDF, images, downloads, source references and local catalog indexing.

### Phase 2 — Local Factory Studio
Queue, run one story, log streaming, package explorer, Drive readback and scheduler status. No arbitrary shell commands.

### Phase 3 — Review and teacher workflows
Review Studio, source checklists, ślokas, answer keys, class packs and content approval states.

### Phase 4 — Public PWA
Public deployment, offline story packages, CDN, accessibility, SEO, privacy and performance hardening.

### Phase 5 — Multi-scripture platform
Generic collection model, Cantos 1–12, Rāmāyaṇa, Caitanya literature, Prabhupāda resources and lectures.

### Phase 6 — Optional accounts
Only after privacy/legal review. Parent and teacher accounts, cross-device progress and approved classroom spaces.

## 12. Testing strategy

- Contract tests for the exact eight-file package
- manifest-schema tests
- source-boundary regression tests
- unit tests for adapters
- API integration tests
- Playwright end-to-end tests
- visual regression screenshots
- axe accessibility tests
- audio controls and download tests
- PDF view/print tests
- Drive readback tests
- scheduler and idempotency tests
- security tests ensuring public routes cannot invoke factory commands
- performance budgets for mobile and slow networks

## 13. Definition of done for the first build

1. Existing story generation tests remain unchanged and green.
2. The portal discovers Stories 001–007 from manifests.
3. Story pages render audio, markdown, images and PDF.
4. Every asset downloads; PDF prints.
5. Source boundaries and review status are visible.
6. The local studio can safely launch the existing one-story workflow.
7. Public routes cannot alter queue, scheduler or Drive.
8. Mobile, tablet and desktop layouts pass.
9. WCAG 2.2 AA automated checks pass.
10. No child personal data is collected.

## 14. First implementation recommendation

Build Phase 1 as a separate application inside the repository. Do not convert the current Streamlit dashboard into the public product. Retain Streamlit temporarily as an engineering utility, and replace it gradually with the new local Factory Studio after the read-only portal is stable.
