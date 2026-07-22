# Implementation Phases

## Phase 0 — Safety and foundation
- Create a long-lived feature branch.
- Record current main/master/tags.
- Add architecture decisions.
- Add portal workspace without modifying factory logic.
- Add golden compatibility tests.
- Add an asset/catalog adapter around the eight-file packages.

## Phase 1 — Bhāva design system and public shell
- Responsive shell
- navigation
- home
- library
- collection page
- about/contact
- accessibility baseline
- public footer and copyright/source notices

## Phase 2 — Story experience
- auto-discover stories from manifests
- story detail
- waveform audio player
- speed, seek and playlist
- markdown reader
- PDF viewer/print/download
- coloring gallery
- source panel
- device-local notes/bookmarks/progress

## Phase 3 — Teacher toolkit
- age-specific views
- activity selection
- teacher notes
- answer-key protection
- printable class-pack design
- śloka-learning component and data model

## Phase 4 — Local Factory Studio
- status
- queue
- preflight
- generate-next
- review studio
- package explorer
- Drive readback
- scheduler state and controls
- streaming logs
- strict loopback-only boundary

## Phase 5 — Quality hardening
- full unit/integration/E2E coverage
- Playwright browser verification
- accessibility
- visual regression
- error states
- loading states
- offline/read-only resilience
- performance budgets

## Phase 6 — Public deployment readiness
- PWA manifest and service worker
- production environment model
- public/private route split
- privacy and permissions
- `bhava.me` deployment guide
- do not change IONOS DNS in this implementation
