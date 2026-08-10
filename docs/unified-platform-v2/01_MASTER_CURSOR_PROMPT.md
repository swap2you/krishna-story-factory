# Paste This Entire File Into Cursor

You are executing **Bhāva Unified Platform Build V2** in the authoritative checkout:

`C:\Development\Workspace\DevotionalRepo\krishna-story-factory`

The program package is:

`C:\Development\Workspace\DevotionalRepo\krishna-story-factory\MyPilotDropbox\BHAVA\BHAVA_UNIFIED_PLATFORM_BUILD_V2.zip`

Safely inspect the archive, reject path traversal/symlink hazards, verify `CHECKSUMS.sha256`, and extract to a gitignored local work area. Read every file completely before editing.

## Authorization and operating model

The owner authorizes one consolidated program, direct tested commits to `develop`, repeated local/CI/browser repair work, staging deployments, and one final cumulative `develop → main` promotion PR only after the whole program passes its gates. Do not create feature, fix, docs, sync, release, or content branches. Do not open PRs to `develop`. Do not force-push, rebase shared history, remove `main` protection, or weaken valid tests.

Do not stop after each internal milestone. Maintain the program ledger and evidence as you go. Continue through ordinary failures—lint, type, unit, integration, UI, browser, accessibility, documentation, CI, and staging defects—using root-cause fixes. Stop only for a real hard blocker defined in `specs/05_DELIVERY_AND_VALIDATION.md`.

## Required baseline

1. Fetch `origin`; record exact `main` and `develop` SHAs; confirm a clean worktree or isolate unrelated user changes without stashing/resetting them.
2. Merge `main` into `develop` normally if needed; no rebase.
3. Validate the committed `next.config.ts` development-mode guard by running the supported `next dev` path once. Verify home, `/stories/025`, `/stories/026`, Studio loopback handling, and a clean browser console. Fix the root cause if it fails.
4. Read the current app architecture, design tokens, P01C package system, Studio/private-route contracts, tests, workflows, release tooling, prior R00/R01 evidence, and all program specifications.
5. Reconcile stale historical notes: old story caps, "12 PDFs missing," P01C synthetic-only claims, and obsolete branch-per-packet instructions. Do not rewrite immutable R00 evidence; correct current documentation and templates only.

## Execute the program

Implement `specs/03_MASTER_PROGRAM_SCOPE.md` in the stated sequence. The intended outcome is a visible, polished platform—not hidden engineering alone.

Source resolution is a workstream, not an excuse to halt all implementation. First inspect the owner-supplied 12-PDF source inventory and allowed local corpus records through supported repository/library workflows. Build dossiers, provenance records, title normalization, content intake controls, and review states. For each public record, require adequate source evidence and permitted use. If TOP-0147 remains inadequate, do not fabricate it; use another approved, dossier-ready record for the golden page only if the source and review evidence meets the same bar. Otherwise complete all non-content-blocked platform work and produce one consolidated source blocker identifying the exact missing source fields.

Build only original Bhāva explanatory/learning expression unless a text is verified permitted for publication. Never publish a private original PDF, a copied PDF body, an unsupported translation, a fabricated quotation, or an invented reviewer decision. Do not use source availability as a claim of rights.

## Validation and release

Apply `specs/05_DELIVERY_AND_VALIDATION.md` to every milestone and to the cumulative program. Use production/standalone browser builds for UX evidence, not a development toolbar. Run the existing Sonar/SonarCloud gate if configured; do not add a paid service just to say "Sonar passed." Preserve privacy boundaries and test them externally.

Create `MyPilotDropbox\BHAVA\release-handoffs\BHAVA-UNIFIED-PLATFORM-BUILD-V2-<timestamp>.zip` after each milestone, plus a final ZIP containing the final program evidence index. Keep originals, private PDFs, databases, secrets, media caches, and giant build outputs out of Git and evidence ZIPs.

When all program criteria are green, stage the exact `develop` SHA; verify the intended public/private boundary, real public records, assets, exports, noindex/private behavior, accessibility, and rollback pointer. Then create the one cumulative `develop → main` promotion PR. Wait for checks and protected-environment approval; merge and deploy exactly the merged SHA only after all gates pass. Verify production again. Create tags only after production success; never move existing immutable content tags.

If the program cannot complete due to a genuine hard blocker, do not create a speculative production release. Produce one concise consolidated blocker report with exact missing item, why it blocks only the affected surface, completed work, test evidence, and safe next action.

Return the concise format in `templates/CURSOR_FINAL_RESPONSE_TEMPLATE.md`, plus the exact final ZIP paths and SHA-256 values to send to ChatGPT and CoWork.

