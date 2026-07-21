# Manual Story Rebuild Runbook

Use this runbook for safe rebuilds of Stories **001–006** without advancing the queue, enabling the scheduler, or sending WhatsApp/Telegram.

Authoritative tools:

- `scripts/rebuild_story_packages.py`
- `scripts/manual_rebuild_story.ps1` (venv wrapper; never silently adds `--force`)
- `scripts/repair_story_markdown_local.py` (structure/content repairs only; never calls paid APIs)

Exact production package is always **eight files**:

1. `story.md`
2. `narration.mp3`
3. `story_poster.png`
4. `coloring_page.png`
5. `simple_coloring_page.png`
6. `activity_sheet.pdf`
7. `whatsapp_caption.txt`
8. `manifest.json`

## Parent-facing story.md (no YAML frontmatter)

Distributed `story.md` does **not** include YAML frontmatter. Title/source metadata live in
`### Scriptural Source` plus `manifest.json`. Parsers remain backward-compatible with older
YAML-fronted files during rebuild.
## Safety checks (before every run)

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from krishna_story_factory.csv_store import ensure_csv_files, read_next_pending, read_plan_by_chapter; r=Path('.'); ensure_csv_files(r); p=read_next_pending(r); print('next', p.chapter_no if p else None); print([(c, read_plan_by_chapter(r,c).status) for c in ['001','002','003','004','005','006','007']])"
schtasks /query /tn "Krishna Story Factory Daily" /v /fo LIST
```

Expected:

- Stories 001–006: `done`
- Story 007: `pending`
- Scheduler: **Disabled**

## Provider preflight

The rebuild script resets the provider cache and preflights before destructive narration work:

- ElevenLabs Renee first when gates pass
- OpenAI Marin fallback
- If neither is ready and narration is requested: abort without partial packages

## Dry-run

```powershell
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 001,002,003,004,005 --dry-run
.\scripts\manual_rebuild_story.ps1 -Chapters 001,002,003,004,005 -DryRun
```

Dry-run plans actions, checks queue safety, and writes a report. It does not call paid APIs or replace packages.

## Local rebuild (staging → local replace)

```powershell
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 001,002,003,004,005 --local-only
.\scripts\manual_rebuild_story.ps1 -Chapters 001,002,003,004,005 -LocalOnly
```

Behavior:

1. Timestamped backup under `output/_archive/manual_rebuild_<stamp>/`
2. Staging under `output/_staging/manual_rebuild_<stamp>/`
3. Provider preflight before narration
4. Atomic local replacement of the eight final files
5. Queue unchanged; Story 007 remains pending
6. JSON + Markdown report under `output/_staging/`

## One story / one component

```powershell
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 003 --local-only
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 003 --components narration --local-only
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 003 --components activity --local-only
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 003 --components poster,coloring,simple_coloring --local-only
.\scripts\manual_rebuild_story.ps1 -Chapter 003 -Components narration -LocalOnly
```

Component-only rebuilds preserve hashes for untouched files whenever possible.

## Story 006 repaired package

```powershell
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 006 --local-only
.\scripts\manual_rebuild_story.ps1 -Chapter 006 -LocalOnly
```

## Drive upload (opt-in only)

```powershell
.\.venv\Scripts\python.exe scripts\rebuild_story_packages.py --chapters 001,002,003,004,005 --upload-drive
.\scripts\manual_rebuild_story.ps1 -Chapter 006 -UploadDrive
```

Drive mutation requires the explicit `--upload-drive` / `-UploadDrive` flag. Do not upload until staging validation passes and an operator approves.

## Validation only

```powershell
.\scripts\manual_rebuild_story.ps1 -Chapters 001,002,003,004,005,006 -DryRun -ValidateOnly
```

## Backup and rollback

- Local replace uses directory-level atomic swap (`package_swap.atomic_replace_package_dir`): staging validated → production renamed to archive backup → staging renamed into place; failed final rename restores the backup.
- Backups: `output/_archive/manual_rebuild_<stamp>/`
- Staging: `output/_staging/manual_rebuild_<stamp>/`
- On failure before local replace, production packages remain unchanged
- To roll back after a bad local replace, copy the matching archive folder back over `output/<chapter>_<slug>/`

## Audio drift / AUDIO_STALE

Preserved narration must not claim PASS when story narration text changed:

- Manifest stores `narration_source_sha` only for generation-verified audio.
- Mismatch or missing hash → `AUDIO_STALE` until narration is regenerated.
- Local markdown repair never clears this gate and never invents provider identity (`unknown_preserved`).

## Final report

Each run writes:

- `output/_staging/manual_rebuild_report_<stamp>.json`
- `output/_staging/manual_rebuild_report_<stamp>.md`

Confirm in the report:

- exact eight files
- queue unchanged / next pending = 007
- Drive modified only when upload was requested
- real audio provider metadata when narration was rebuilt
- AUDIO_STALE when narration was preserved after story-text repair
