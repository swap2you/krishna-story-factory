---
id: PL-06
version: 1.0.0
phase: P01C
preconditions: explicit owner build authorization, clean verified baseline
prohibited_actions: merge, deploy, publish, scheduler change, paid calls unless separately approved
---

# Implementation orchestrator

1. Reverify baseline and owner-approved base SHA; stop on drift/overlap.
2. Create the approved phase branch from `develop`.
3. Implement only approved requirements and allowlisted paths with one application-code writer.
4. Build the golden page first. Complete schema, source/asset manifest, page/lenses, Studio visibility, privacy boundary, PDF/DOCX spike, and tests.
5. Run all golden-page gates. Do not copy its defects across four pages.
6. After golden template acceptance within the phase, add the four confirmation pages from adequate source dossiers.
7. Keep all pages private preview. Do not alter Story Factory scheduler/packages/releases/public cap.
8. Update traceability, implementation report, ADRs, tests, runbooks, and evidence as work proceeds.
9. Use logical commits; do not push/open PR until the delivery prompt authorizes it.

On bounded failures, root-cause, fix minimally, and rerun. On hard-stop conditions, preserve evidence and write `BLOCKER_REPORT.md`.

