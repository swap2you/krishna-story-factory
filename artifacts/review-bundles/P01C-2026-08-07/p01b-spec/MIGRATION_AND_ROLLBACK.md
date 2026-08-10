# Migration and Rollback Plan

## Forward (P01C)

1. Add JSON Schema for canonical package; version it.  
2. Add empty/blocked package directory structure (no unverified scripture).  
3. Wire adapters; keep public loaders unchanged.  
4. Studio pagination (behavior-only; roadmap metadata remains research).  
5. Optional FTS rebuild from packages (OD-12).  
6. After DOSSIER_READY: write approved package bytes + manifests.  
7. Export templates versioned separately from record version.

## Rollback

| Failure | Action |
|---|---|
| Bad package content | Revert git commit of package; rebuild FTS |
| Broken Studio UI | Revert feature commits; `/studio` prior behavior |
| Auth regression | Revert API/middleware; keep public 404 denylist |
| Export defect | Disable download buttons; keep web reading |
| Accidental public leak | Treat as P0: disable route, scrub cache, incident note |

## Non-goals

No rewrite of applied SQL migrations; no Story Factory rollback coupling; no production deploy in Phase 1.
