# Bhava Cursor Release Factory V1

Purpose: run the next five Bhava releases sequentially through one repeatable loop on `develop`, with one promotion PR to `main` per completed major release.

## Use

1. Copy `BHAVA_CURSOR_RELEASE_FACTORY_V1.zip` to:
   `C:\Development\Workspace\DevotionalRepo\krishna-story-factory\MyPilotDropbox\BHAVA\`
2. Open the authoritative local `krishna-story-factory` checkout in Cursor.
3. Paste the complete contents of `00_CURSOR_BOOTSTRAP_PROMPT.txt` into Cursor.
4. Let Cursor extract and validate the package, then execute `01_MASTER_CURSOR_PROMPT.md`.
5. Do not paste separate defect prompts while the release controller is active. Add genuine new scope only to the next release backlog.

## Active release train

| Order | Release | Outcome |
|---:|---|---|
| 0 | `R00-STORY-001-025-CLOSURE` | Reconcile and publish the already-reviewed contiguous Stories 001-025 release if exact artifacts pass all gates. |
| 1 | `R01-KNOWLEDGE-GOLDEN-PAGE` | Replace the synthetic-only state with one dossier-ready real golden Knowledge page and freeze its design direction. |
| 2 | `R02-KNOWLEDGE-FIVE-PAGE-PILOT` | Complete the five-page Phase 1 pilot and freeze Page Template V1. |
| 3 | `R03-KNOWLEDGE-25-PAGE-BATCH` | Prove repeatable production and review across 25 controlled records. |
| 4 | `R04-KNOWLEDGE-50-ITEM-FACTORY` | Build resumable private-draft batch infrastructure and prove two dry/private runs. |

Later releases remain planned: Learning resources, Publications, Audio/Podcast, controlled Scheduler, and 3D/motion research.

## Operating decision

- Work directly on local `develop`; push only tested release checkpoints to remote `develop`.
- Do not create feature, fix, documentation, sync, or release branches.
- Do not open PRs to `develop`.
- Use one `develop -> main` promotion PR per completed major release.
- Keep `main` protected. Remove only rules that prevent the owner from directly pushing to `develop`; do not change repository-wide rules until their `main` coverage is preserved separately.
- Never force-push or delete history.
- Ordinary defects stay inside the automated repair loop. Only a real hard blocker stops the train.

## Files to return after each release

Cursor creates one compact local review ZIP and returns its path plus the complete final summary. Send ChatGPT and CoWork:

1. the release review ZIP;
2. the complete Cursor final response;
3. the promotion PR and CI/deployment URLs;
4. the exact staging and production URLs/build identifiers.

