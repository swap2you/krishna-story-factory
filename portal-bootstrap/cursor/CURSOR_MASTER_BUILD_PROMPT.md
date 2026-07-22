# CURSOR MASTER BUILD PROMPT — BHĀVA PORTAL V1

You are the principal product engineer, UX architect, backend architect, accessibility engineer and test lead for the Bhāva devotional-learning portal.

## Repository

```text
C:\Development\Workspace\DevotionalRepo\krishna-story-factory
```

The operator has copied this ZIP into the repository root:

```text
bhava_portal_cursor_bootstrap_v1.zip
```

## Mission

Build the complete first local release of the Bhāva portal around the existing locked Krishna Story Factory.

The product must serve children, parents and ISKCON teachers. It starts with Krishna Book Stories 001–007 and must be structurally ready for Śrīmad-Bhāgavatam Cantos 1–12, Rāmāyaṇa, Caitanya literature, Śrīla Prabhupāda Vāṇī, lectures, ślokas, activities and a Bhakti Blog.

Work autonomously through all phases. Do not pause for ordinary design or implementation questions. Make conservative, documented decisions. Stop only for a true blocker involving missing credentials, destructive data loss, or a paid/external production action.

## Mandatory Git policy

1. Start from clean, current `main`.
2. Do not change `main`, `master`, existing tags or release artifacts.
3. Create exactly one long-lived branch:

```text
feature/bhava-portal-v1
```

4. Keep that branch open until the entire portal is accepted.
5. Do not merge it.
6. Do not close it.
7. Commit each completed phase separately.
8. Push the branch after every major passing phase.
9. Do not create a PR unless explicitly requested later.

## Mandatory factory-protection policy

Do not rewrite, refactor or replace the working generation engine.

Treat these as locked:

```text
krishna_story_factory/
scripts/
tracking/
output/
input/
credentials/
```

Allowed changes to locked areas:
- additive adapter modules only when required;
- additive tests;
- minimal bug fixes only when a new portal test proves a real compatibility defect;
- no story regeneration;
- no queue advancement;
- no scheduler trigger;
- no Drive upload;
- no paid API call.

Stories 001–007, current queue state, Drive folders, `main`, `master` and existing tags must remain unchanged throughout this build.

## Step 1 — Bootstrap

From repository root:

```powershell
git switch main
git pull --ff-only origin main
git status --short
git rev-parse HEAD
git rev-parse origin/main
git tag --list
git branch -a

git switch -c feature/bhava-portal-v1

Expand-Archive -Path .\bhava_portal_cursor_bootstrap_v1.zip -DestinationPath .\portal-bootstrap -Force
```

Read every file under:

```text
portal-bootstrap/specs/
portal-bootstrap/cursor/
portal-bootstrap/config/
portal-bootstrap/ux-prototype/
```

Use the prototype as visual direction, not as production code.

Create:

```text
docs/product/BHAVA_PRODUCT_REQUIREMENTS.md
docs/architecture/BHAVA_ARCHITECTURE.md
docs/architecture/ADR-001-PORTAL-BOUNDARY.md
docs/architecture/ADR-002-PUBLIC-PRIVATE-SPLIT.md
docs/architecture/ADR-003-MANIFEST-AS-SOURCE-OF-TRUTH.md
docs/architecture/ADR-004-LOCAL-FIRST-STORAGE.md
```

Commit:

```text
docs: establish Bhava portal product and architecture
```

## Technology requirements

Use a lightweight monorepo inside the existing repository:

```text
apps/web
apps/api
packages/ui
packages/contracts
packages/content
data/catalog
```

### Frontend
- current stable Next.js App Router
- TypeScript with strict mode
- current stable React supported by Next.js
- Tailwind CSS
- accessible component primitives
- CSS-variable Bhāva design system
- PWA-ready architecture
- no large UI framework that duplicates basic components
- no vendor lock-in for data fetching

### Backend
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic
- SQLite locally
- PostgreSQL-ready repositories
- OpenAPI contract
- structured logging
- loopback-only local factory routes

### Testing
- existing Pytest suite
- new Pytest API tests
- Vitest / Testing Library
- Playwright
- axe accessibility checks
- visual screenshot tests
- strict type checks
- lint and production builds

Detect installed Node and Python versions. Use the current stable compatible versions. Record exact versions in:

```text
docs/architecture/BHAVA_TECH_BASELINE.md
```

Prefer `pnpm`. If unavailable, enable Corepack or use npm consistently. Do not mix package managers.

## Phase 0 — Protect and map the existing factory

1. Run the full existing test suite before portal work.
2. Inventory exact package paths and current manifests.
3. Create a read-only package catalog adapter.
4. Create golden tests that discover Stories 001–007 without changing them.
5. Validate the exact eight-file contract.
6. Record current story and queue hashes for comparison at the end.
7. Add a build guard that fails if portal work modifies runtime story packages or queue state.

Commit:

```text
test: protect locked factory and story package contracts
```

## Phase 1 — Bhāva foundation and design system

Implement:

- responsive application shell;
- Bhāva brand using midnight blue, warm gold, cream, saffron, lotus pink and tulasī green;
- typography tokens;
- spacing, elevation and radius tokens;
- accessible buttons, cards, tabs, dialogs, tooltips, toasts and skeletons;
- reduced-motion support;
- keyboard navigation;
- WCAG 2.2 AA contrast;
- calm devotional micro-animations;
- reusable empty, error and loading states.

Primary navigation:

- Home
- Library
- For Teachers
- Prabhupāda Vāṇī
- Bhakti Blog
- About
- Contact

The last two future collections can show polished coming-soon pages, not dead links.

Add a private/local-only route group for Factory Studio.

Implement contact details from:

```text
portal-bootstrap/config/contact.example.json
```

Do not publish a blank or invented email address.

Commit:

```text
feat(web): establish Bhava design system and application shell
```

## Phase 2 — Catalog and public library

Build a catalog indexer that reads existing story folders and manifests.

Requirements:

- manifest is authoritative;
- no duplicate metadata maintained manually;
- support local filesystem now;
- define Drive and future object-storage interfaces;
- discover available assets dynamically;
- normalize story, source, activity, audio and publication facts;
- maintain exact source references and review state;
- index into SQLite without changing source files;
- rebuildable catalog.

Implement:

- Home
- Scripture Library
- Krishna Book collection
- chapter/story timeline
- search
- filters
- story thumbnails
- latest and continue-listening sections
- future-ready collection cards for Cantos 1–12 and other works

Commit:

```text
feat(catalog): index locked story manifests and build public library
```

## Phase 3 — Story experience

Implement a production-quality story detail experience:

### Audio
- custom waveform derived from the actual MP3;
- play/pause;
- seek;
- ±15 seconds;
- 0.75×, 1×, 1.25×, 1.5× and 2×;
- elapsed/remaining time;
- volume;
- playlist;
- bookmark;
- resume position;
- sleep timer;
- keyboard shortcuts;
- accessible controls;
- media-session metadata when supported;
- download.

### Reading
- sanitized Markdown;
- beautiful section typography;
- font-size controls;
- sepia/dark modes;
- dyslexia-friendly mode;
- section navigation;
- print;
- download original Markdown.

### Activities and images
- embedded PDF with PDF.js or robust native fallback;
- page thumbnails where practical;
- print;
- open in new tab;
- download;
- poster;
- detailed coloring;
- simple coloring;
- full-screen image view;
- download arrows;
- print actions.

### Notes
- child/parent/teacher notes stored only in browser local storage;
- clear privacy explanation;
- export and print notes;
- no server collection.

### Source
- exact book/chapter/boundaries;
- review and publication status;
- approved source link;
- no unlicensed full-book mirroring;
- future slot for approved excerpt and lecture links.

### Śloka
- support zero, one or more ślokas;
- Sanskrit;
- transliteration;
- word-for-word;
- translation;
- audio repetition;
- reveal/hide;
- memorization mode;
- printable card;
- do not invent ślokas for existing stories;
- use placeholders marked “not yet curated” until content is reviewed.

Commit:

```text
feat(web): deliver complete story listening and learning experience
```

## Phase 4 — Teacher toolkit

Implement:

- Bal Gopal, Dāmodara and mixed-age modes;
- age-specific recommendations;
- teacher notes;
- parent notes;
- activity complexity indicators;
- answer-key access separated from child view;
- printable class-pack composer;
- story, coloring, activity and śloka selection;
- export plan and print preview;
- lesson timing;
- classroom playlist;
- no public child submissions.

Commit:

```text
feat(teachers): add age-aware devotional teaching toolkit
```

## Phase 5 — Local Factory Studio

Build a private localhost-only operator console.

### Security boundary
- factory routes bind only to `127.0.0.1`;
- public frontend build cannot invoke them remotely;
- explicit origin allowlist;
- CSRF protection;
- operation allowlist;
- no arbitrary shell execution;
- no user-provided executable path;
- one active production run;
- secrets redacted;
- audit log;
- safe cancellation only where the current pipeline supports it.

### Screens
- overview;
- queue;
- next-pending story;
- package explorer;
- provider health;
- preflight;
- generation wizard;
- review studio;
- Drive readback;
- scheduler view;
- recent runs;
- live structured logs;
- failure explanation.

### Existing pipeline
Invoke the existing approved production entry point. Do not reimplement generation.

For this development branch:
- production action buttons default to disabled/demo mode;
- enable real actions only behind an explicit local environment flag;
- tests must never call paid providers or Drive;
- do not trigger Story 008.

Commit:

```text
feat(studio): add safe local factory operations console
```

## Phase 6 — Blog and future-content foundations

Implement future-ready but lightweight:

- Bhakti Blog index;
- article template;
- MDX or sanitized Markdown source;
- tags and collections;
- Prabhupāda Vāṇī collection shell;
- lecture/resource asset types;
- generic collection model supporting:
  - Krishna Book
  - Śrīmad-Bhāgavatam Cantos 1–12
  - Rāmāyaṇa
  - Caitanya literature
  - Prabhupāda resources

Use coming-soon content clearly. Do not fabricate articles or quotations.

Commit:

```text
feat(content): prepare Bhava for blog and multi-scripture expansion
```

## Phase 7 — PWA, performance and public-readiness

Implement:

- web app manifest;
- installable icons derived from approved Bhāva artwork;
- offline shell;
- optional offline saved story package;
- responsive images;
- lazy loading;
- route-level code splitting;
- metadata and Open Graph;
- sitemap and robots policy;
- structured data where appropriate;
- privacy page;
- accessibility page;
- source and permissions page;
- no analytics by default;
- no advertisements;
- no child tracking.

Performance budgets:
- mobile Lighthouse performance target ≥ 90 where local assets allow;
- accessibility ≥ 95;
- no major layout shift;
- no blocking large unoptimized images;
- audio lazy-loaded.

Commit:

```text
feat(pwa): harden Bhava for accessible public delivery
```

## Phase 8 — Full testing and browser validation

Run all of the following:

- existing Python suite;
- new API suite;
- frontend type check;
- frontend lint;
- unit tests;
- production web build;
- Playwright Chromium;
- Playwright Firefox;
- Playwright WebKit;
- mobile emulation;
- axe scans;
- visual screenshots;
- secret scan;
- dependency audit;
- route and broken-link scan;
- story asset download tests;
- PDF open/print fallback tests;
- audio player tests;
- local-note persistence tests;
- public/private boundary tests;
- package hash guard.

Use Playwright `webServer` to launch the app automatically.

Open the real browser in headed mode and visually inspect:

- Home
- Library
- Krishna Book
- every available Story 001–007 page
- audio interaction
- reading modes
- PDF
- coloring
- notes
- source
- teacher toolkit
- Prabhupāda Vāṇī shell
- Bhakti Blog shell
- About
- Contact
- Factory Studio
- mobile, tablet and desktop

Fix all:
- console errors;
- failed assets;
- layout overflow;
- inaccessible controls;
- broken downloads;
- missing loading/error states;
- visual inconsistencies.

Store final screenshots under:

```text
docs/product/screenshots/
```

Commit:

```text
test: validate Bhava portal across browsers and accessibility gates
```

## Phase 9 — Local operator packaging

Create:

```text
scripts/start_bhava_local.ps1
scripts/stop_bhava_local.ps1
scripts/test_bhava.ps1
scripts/reindex_bhava_catalog.ps1
```

The start script must:
- verify prerequisites;
- start API and web processes;
- wait for health checks;
- open the default browser;
- write PID files safely;
- avoid duplicate processes;
- never invoke story generation.

Document:

```text
docs/operations/BHAVA_LOCAL_RUNBOOK.md
docs/operations/BHAVA_TROUBLESHOOTING.md
docs/deployment/BHAVA_ME_DEPLOYMENT_GUIDE.md
```

The deployment guide may explain IONOS DNS and SSL steps, but must not change DNS or deploy.

Commit:

```text
chore: package Bhava local operation and deployment guidance
```

## Phase 10 — Final independent reviews

Run three review passes locally:

1. Codex-style technical review:
   - architecture;
   - public/private security;
   - factory preservation;
   - test integrity.

2. Claude-style adversarial review:
   - invented content;
   - copyright leakage;
   - child privacy;
   - accessibility;
   - hidden coupling.

3. Parent/teacher UX review:
   - clarity for ages 5–13;
   - activity discoverability;
   - readability;
   - devotional mood;
   - no confusing operator controls in public views.

Address blocking findings on the same branch.

Create:

```text
docs/reviews/BHAVA_V1_TECHNICAL_REVIEW.md
docs/reviews/BHAVA_V1_CONTENT_PRIVACY_REVIEW.md
docs/reviews/BHAVA_V1_PARENT_TEACHER_REVIEW.md
docs/releases/BHAVA_V1_LOCAL_RELEASE.md
```

Commit:

```text
docs: record Bhava v1 local release review and evidence
```

## Final verification

Confirm:

- branch remains `feature/bhava-portal-v1`;
- branch is pushed;
- branch is not merged;
- branch is not closed;
- no PR exists unless separately requested;
- `main`, `master` and existing tags are unchanged;
- Stories 001–007 hashes are unchanged;
- queue remains Story 008 pending;
- scheduler was not triggered;
- Drive was not modified;
- no paid APIs were called;
- full tests pass;
- working tree is clean;
- local browser opens successfully.

## Final response format

Return:

```text
BHĀVA PORTAL V1 — COMPLETE LOCAL BUILD

Git
- Base main SHA
- Feature branch
- Final branch SHA
- Branch pushed
- PR created: NO
- Main modified: NO
- Master modified: NO
- Existing tags modified: NO

Factory protection
- Stories 001–007 modified: NO
- Queue modified: NO
- Scheduler triggered: NO
- Drive modified: NO
- Paid API calls: NONE

Application
- Web URL
- API URL
- Catalog stories discovered
- Routes completed
- Local Studio mode
- PWA status
- Contact page
- Notes
- Blog shell
- Prabhupāda Vāṇī shell

Testing
- Existing Python tests
- API tests
- Frontend tests
- Type check
- Lint
- Production build
- Playwright browsers
- Accessibility
- Visual regression
- Secret scan

Artifacts
- Screenshots path
- Runbook
- Architecture
- Deployment guide
- Review documents

Known non-blocking limitations

Verdict
- PASS / BLOCKED
```

Do not report PASS if the browser was not opened and inspected, if the branch is not pushed, or if the locked factory changed.
