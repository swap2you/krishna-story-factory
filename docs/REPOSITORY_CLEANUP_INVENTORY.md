# Repository Cleanup Inventory

Assessment only. **Do not delete anything from this list automatically.**
Use a separate docs-only PR (`chore/repository-documentation-cleanup`) after human review.

## KEEP

### Runtime code
| Path | Reason |
| --- | --- |
| `krishna_story_factory/` | Core package |
| `run_daily_story.py` | CLI entrypoint |
| `dashboard.py` | Optional Streamlit UI |
| `requirements.txt` | Dependencies |
| `.env.example` | Config template |
| `.gitignore` | Safety |

### Active scripts
| Path | Reason |
| --- | --- |
| `scripts/bootstrap.ps1` | Environment bootstrap |
| `scripts/run_prod.ps1` / `run_test.ps1` / `test_all.ps1` | Daily / CI wrappers |
| `scripts/run_dashboard.ps1` | Optional UI |
| `scripts/install_daily_story_task.ps1` / `remove_daily_story_task.ps1` / `create_task_scheduler_job.ps1` / `test_daily_story_task.ps1` / `run_daily_story_scheduled.ps1` / `run_daily_story_windows.ps1` | Scheduler ops |
| `scripts/clean_local_outputs.ps1` / `repair_venv.ps1` | Local maintenance |
| `scripts/test_google_drive_upload.*` / `test_whatsapp_*` | Channel smoke tests |
| `scripts/validate_master_plan.py` / `validate_story_visuals.py` / `check_audio_quality.py` / `diagnose_local_config.py` | Diagnostics |
| `scripts/generate_story_visuals.*` | Supported visual tooling |
| `scripts/manual_rebuild_story.ps1` | Documented rebuild path |

### Durable tests
| Path | Reason |
| --- | --- |
| `tests/` | Full pytest suite including release locks |

### Current input / queue templates
| Path | Reason |
| --- | --- |
| `input/series_plan.csv` | Episode source of truth |
| `input/whatsapp_recipients.csv` | Recipient source of truth |
| `input/content_quality_rules.md` | Editorial rules (if present) |
| `tracking/templates/` | Tracked CSV templates |

### Current docs / release records
| Path | Reason |
| --- | --- |
| `README.md` / `AGENTS.md` | Operator entry |
| `docs/01_DAILY_RUNBOOK.md` … `docs/15_*.md` | Active numbered docs |
| `docs/releases/PILOT_001_006_RELEASE_LOCK.md` | Pilot lock |
| `docs/releases/PILOT_001_006_HASHES.json` | Non-media hash evidence |
| `prompts/DAILY_STORY_MASTER.md` | Active master prompt |
| `prompts/activity_bank/` | Active activity prompt bank |

## DELETE CANDIDATES

Do **not** delete in the pilot lock PR. Review in `chore/repository-documentation-cleanup`.

| Path | Reason | Referenced by code/docs/tests? | Safe-to-delete confidence | Replacement |
| --- | --- | --- | --- | --- |
| `ACTIVITY_AND_LINEART_RELEASE_REPORT.md` | One-time root release report | Docs only (historical) | High | `docs/releases/PILOT_001_006_RELEASE_LOCK.md` |
| `BUILD_REPORT.md` | Stale build narrative | No | High | README + numbered docs |
| `FINAL_ACTIVITY_ENGINE_V2_RELEASE_REPORT.md` | Duplicate activity release note | Docs mention historically | High | `docs/11_ACTIVITY_ENGINE_V2.md` |
| `FINAL_ACTIVITY_ENGINE_V2_REPORT.md` | Duplicate of above | No | High | `docs/11_ACTIVITY_ENGINE_V2.md` |
| `FINAL_AUTOMATION_AND_GOVERNANCE_REPORT.md` | One-time synthesis | No | High | `docs/09_SERIES_PLAN_GOVERNANCE.md` |
| `FINAL_V1_RELEASE_REPORT.md` | Superseded by pilot lock | No | High | `docs/releases/PILOT_001_006_RELEASE_LOCK.md` |
| `VALIDATION_ARTIFACTS.md` | Ad-hoc validation dump | No | Medium | `docs/06_TESTING_AND_VALIDATION.md` |
| `docs/14_STORY_002_005_REPAIR_BACKLOG.md` | Completed repair backlog | Possibly linked from ops prompts | Medium | Pilot release lock + hash evidence |
| `docs/operations/prompt-bank/STORY_005_FINAL_REPAIR_CURSOR_PROMPT.md` | One-time Cursor repair prompt | Ops bank only | High | Release lock |
| `docs/operations/prompt-bank/02_CODEX_TECHNICAL_REVIEW.md` | Duplicate of validation twin | Ops bank | Medium | Keep one of `02_*` pair |
| `docs/operations/prompt-bank/02_CODEX_TECHNICAL_VALIDATION.md` | Twin of review prompt | Ops bank | Medium | Keep one of `02_*` pair |
| `docs/operations/prompt-bank/03_CLAUDE_CONTENT_REVIEW.md` | Duplicate twin | Ops bank | Medium | Keep one of `03_*` pair |
| `docs/operations/prompt-bank/03_CLAUDE_CODE_CONTENT_VALIDATION.md` | Twin of review prompt | Ops bank | Medium | Keep one of `03_*` pair |
| `docs/operations/prompt-bank/04_COWORK_PACKAGE_REVIEW.md` | Duplicate twin | Ops bank | Medium | Keep one of `04_*` pair |
| `docs/operations/prompt-bank/04_COWORK_PARENT_PACKAGE_VALIDATION.md` | Twin | Ops bank | Medium | Keep one of `04_*` pair |
| `docs/operations/prompt-bank/05_FINAL_SYNTHESIS_AND_LOCK.md` | Duplicate twin | Ops bank | Medium | Keep one of `05_*` pair |
| `docs/operations/prompt-bank/05_FINAL_SYNTHESIS_AND_MERGE.md` | Twin | Ops bank | Medium | Keep one of `05_*` pair |
| `prompts/_archive/**` | Superseded prompt archive | No runtime import found | High | `prompts/DAILY_STORY_MASTER.md` |
| `docs/archive/initial_build_notes/**` | Initial scaffold notes | Historical only | Medium | Numbered `docs/01–15` |
| `scripts/rebuild_001_005_v2_safe.py` | One-time Template V2 rebuild | No durable test import | High | Release lock evidence |
| `scripts/rebuild_story_005_format_v2.py` | One-time Story 005 rebuild | No | High | Release lock |
| `scripts/rebuild_story_005_matching.py` | One-time matching repair | No | High | Activity engine docs |
| `scripts/rebuild_story_packages.py` | Broad rebuild helper | Possibly referenced in runbooks | Medium | `scripts/manual_rebuild_story.ps1` |
| `scripts/repair_story_005*.py` | One-time Story 005 repairs | No | High | Release lock |
| `scripts/repair_story_markdown_local.py` | One-time markdown repair | No | Medium | Content repair modules in package |
| `scripts/expand_story_005_v2_lengths.py` | One-time length expander | No | High | — |
| `scripts/add_simple_coloring_and_repair_005.py` | One-time coloring add | No | High | Image generator |
| `scripts/verify_story_005_*.py` | One-time verification scripts | No | Medium | Durable pytest |
| `scripts/openai_tts_fallback_pilot.py` | Pilot TTS experiment | Docs may mention | Medium | `docs/13_OPENAI_TTS_FALLBACK.md` |
| `scripts/preflight_elevenlabs_renee_rebuild.py` | One-time voice preflight | No | Medium | Audio provider module |
| `scripts/renee_pronunciation_smoke.py` | Voice smoke helper | No | Low | Keep until voice policy settles |
| `scripts/_repair_pilot_artifacts_004_005.py` | Ephemeral this-session repair | No | High (after archive) | Local `.local_release_archive/` |
| `scripts/_regen_005_*.py` / `scripts/_inspect_004_005.py` | Ephemeral this-session helpers | No | High (after archive) | Local archive |

## Locked directories — never delete

`krishna_story_factory/`, `scripts/` (as a directory), `tests/`, `input/`, `tracking/`, `credentials/`, `output/`, `docs/`.

## Recommended cleanup PR scope

1. Remove verified obsolete root `FINAL_*` / `BUILD_*` / `VALIDATION_*` reports.
2. Deduplicate `docs/operations/prompt-bank/` twin prompts (keep one of each numbered pair).
3. Leave `prompts/_archive/` and `docs/archive/` unless explicitly approved.
4. Do not remove active scheduler / Drive / WhatsApp smoke scripts without a replacement.
