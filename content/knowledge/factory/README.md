# Knowledge draft factory (private)

50-item private-draft factory for Unified Platform Build V2 / M2.

- **CLI:** `python scripts/knowledge_draft_factory.py --dry-run`
- **Module:** `apps/api/bhava_api/knowledge/draft_factory.py`
- **Status surface:** Studio `/studio/knowledge` (read-only summary)

## Authority (hard)

This factory **cannot** approve, merge, deploy, or publish. It only builds private draft scaffolds and dry-run evidence.

## Artifacts

| Path | Role |
|---|---|
| `prompt_ledger_v1.json` | Template/prompt ledger |
| `templates/` | Contract text for stages |
| `state/draft_factory_status.json` | Last run summary (studio-readable) |
| `drafts/` | Optional scaffold JSON (never public) |
