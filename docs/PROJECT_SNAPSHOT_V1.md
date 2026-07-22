# Krishna Story Factory — Project Snapshot V1

Canonical engineering/operations snapshot for Cursor, Codex, Claude, or a human operator. Prefer this file over historical repair prompts.

## Purpose

Local Python automation that generates **one Krishna Book bedtime story package per run** for children ages **6–12**, validates an exact **eight-file** package, and uploads it to **Google Drive**. WhatsApp and Telegram sending are **disabled** for the pilot. CLI is source of truth; Streamlit dashboard is optional.

Repository: [github.com/swap2you/krishna-story-factory](https://github.com/swap2you/krishna-story-factory)

## Architecture (short)

```text
input/series_plan.csv          static episode metadata
input/krishna_book_master_plan.csv   full editorial plan
tracking/queue_state.csv       runtime status (pending/done)
run_daily_story.py             CLI entry (--mode prod|test)
krishna_story_factory/         pipeline, generation, audio, images, PDF, Drive
scripts/run_prod.ps1           prod wrapper (venv Python)
scripts/run_test.ps1           test wrapper (no paid APIs)
scripts/test_all.ps1           full pytest
output/<chapter>_<slug>/       exact eight final files
```

Production path: queue → Story Format V2 text → TTS → images → activity PDF → staging → validate → atomic promote → Drive upload + readback → advance queue on full PASS only.

## Story Format V2

Parent-facing `story.md` has **no YAML frontmatter**. Visible sections (order matters):

1. Greeting  
2. Series (`Krishna Book Bedtime`)  
3. Story number and title  
4. Scriptural Source  
5. Recap  
6. Main Story  
7. Devotional Meaning  
8. Five Lessons  
9. Think About It  
10. Five-Star Challenge  
11. Bedtime Prayer  
12. Next Story Preview  
13. Parent/Teacher Note  

Hidden (HTML comment): Audio Narration, visual briefs, activity data. Narration is generated from the Audio Narration section; `manifest.json` stores `narration_source_sha`. Golden structural reference: Story **006**.

Details: [CONTENT_STANDARD.md](CONTENT_STANDARD.md), `krishna_story_factory/content/story_format_v2.py`.

## Exact eight-file package

Every `output/<chapter_no>_<slug>/` must contain **exactly** these eight files (no extras in the final folder):

1. `story.md`  
2. `narration.mp3`  
3. `story_poster.png`  
4. `coloring_page.png`  
5. `simple_coloring_page.png`  
6. `activity_sheet.pdf`  
7. `whatsapp_caption.txt`  
8. `manifest.json`  

`line_art_prompt.txt` and other intermediates are **not** part of the publishable package.

## Source hierarchy

Highest authority first:

1. **Krishna Book / Śrīmad-Bhāgavatam boundary** for the selected episode (`source_reference`, `scripture_reference`, `must_include`, `must_avoid`, `start_boundary`, `end_boundary`).  
2. **`input/krishna_book_master_plan.csv`** — full editorial series (tracked).  
3. **`input/series_plan.csv`** — CLI-ready static projection (tracked; **no** execution status).  
4. **`tracking/queue_state.csv`** — runtime pending/done (gitignored).  
5. **Content rules** — [CONTENT_STANDARD.md](CONTENT_STANDARD.md), `input/content_quality_rules.md`.  
6. **Generation prompts** — `prompts/` (especially master agent + daily story prompts).  

Never invent scripture quotations. Never mix unrelated pastimes. Never skip queue sequence.

## Provider fallback (audio)

1. Preflight **ElevenLabs** locked voice **Renee** (`eleven_v3`, `mp3_44100_128`).  
2. If ElevenLabs fails (quota/auth/balance), preflight **OpenAI TTS** voice **marin** (`gpt-4o-mini-tts-2025-12-15`).  
3. If both fail and `AUDIO_REQUIRED=true`, abort **before** story/image/PDF/Drive work; queue stays pending.  

Config keys: `AUDIO_PROVIDER_MODE=auto`, `AUDIO_PROVIDER_PRIMARY=elevenlabs`, `AUDIO_PROVIDER_FALLBACK=openai`. Do not re-bill duplicate paid TTS chunks when a verified candidate already passes. OpenAI long narration uses lossless chunk assembly with SHA checks.

## Image and activity pipelines

- **Poster** → `story_poster.png` (cinematic portrait; local typography).  
- **Coloring** → `coloring_page.png` (thick line art; child-safe; no weapons).  
- **Simple coloring** → `simple_coloring_page.png`.  
- **Activity Engine V2** → `activity_sheet.pdf` (2–4 pages typical; story-specific; vision QA; answer keys in manifest only).  

Intermediates may live under work/staging dirs; only the eight finals are promoted.

## Queue rules

- Runtime status lives only in `tracking/queue_state.csv`.  
- One next-pending story per normal prod run.  
- Advance to `done` **only** after local exact-eight PASS, publishable gate, and successful Drive upload/readback (when Drive is enabled).  
- Partial failure → leave queue unchanged.  
- Do not put `status` on `series_plan.csv`.  
- Same-day duplicate normal prod is guarded; use intentional `--force` / rebuild tools carefully.  
- Locked Stories **001–006** must not be regenerated without explicit approval.

## Drive layout

- Parent folder ID/URL from `.env` (`GOOGLE_DRIVE_FOLDER_ID` / `GOOGLE_DRIVE_FOLDER_URL`).  
- Each story: folder `<chapter_no>_<slug>` with the same eight files.  
- Caption + `manifest.package.package_link` get the per-story folder URL.  
- Upload controlled by `GOOGLE_DRIVE_UPLOAD_ENABLED`.  

See [DRIVE_AND_PACKAGE_LAYOUT.md](DRIVE_AND_PACKAGE_LAYOUT.md).

## Publishable gates

`manifest.publishable` is true only when:

- mode is prod (not test);  
- quality status is `PASS` with no quality errors;  
- audio is generation-verified (real provider, not preserved/unknown);  
- `narration_source_sha` and audio SHA present;  
- audio not stale (`AUDIO_STALE`);  
- exact eight-file package present.  

Test mode must not call paid APIs and is never publishable.

## Safety guards

- Source boundary guards (`generation/source_guard.py`).  
- Child-safe content (no graphic violence; gentle treatment of hard events).  
- Staging + atomic package swap (`package_swap.py`); failed promote restores backup.  
- WhatsApp/Telegram remain `false` unless an operator explicitly enables them (pilot: keep disabled).  
- Never commit `.env`, credentials, `output/*` packages, or runtime tracking CSVs.  
- Scheduler runner forces Drive on and messaging off for the process env.

## Scheduler

- Task name: **`Krishna Story Factory MWF`**  
- Schedule: Monday / Wednesday / Friday **06:00** local  
- Installer: `scripts/install_mwf_story_task.ps1`  
- Runner: `scripts/run_daily_story_scheduled.ps1` → `run_daily_story.py --mode prod`  
- Overlap: IgnoreNew; 60-minute limit; 2 retries / 30 minutes  
- Legacy **`Krishna Story Factory Daily`** must not remain enabled  

Installer defaults to **Disabled** unless `-Enable`. See [SCHEDULER.md](SCHEDULER.md).

## Release state (pilot 001–006)

| Item | State |
| --- | --- |
| Stories 001–006 | Locked (Story Format V2); do not modify without approval |
| Next pending at snapshot | **007** (`kamsa-begins-his-persecutions`) |
| Senior devotee review | **Pending** |
| Planned Git tag | `v1.0.0-pilot-stories-001-006` |
| Evidence | [releases/PILOT_001_006_RELEASE_LOCK.md](releases/PILOT_001_006_RELEASE_LOCK.md), [releases/PILOT_001_006_HASHES.json](releases/PILOT_001_006_HASHES.json) |
| Messaging | WhatsApp / Telegram disabled |
| Distribution | Google Drive |

Pilot narration for 001–006 used OpenAI Marin when ElevenLabs Renee was unavailable; policy still prefers Renee first.

## Manual generation

```powershell
cd C:\Development\Workspace\DevotionalRepo\krishna-story-factory
.\scripts\run_test.ps1 --force          # structure only; no paid APIs
.\scripts\run_prod.ps1                  # next pending; Drive if enabled
```

Optional: `--chapter NNN`, `--force`, `--no-upload`, `--rebuild-components activity,coloring`, `--debug`. Do not invent flags. Full ops: [DAILY_OPERATIONS.md](DAILY_OPERATIONS.md).

## Recovery from tag

```powershell
git fetch --tags
git switch --detach v1.0.0-pilot-stories-001-006
```

Tag restores **code/config**, not gitignored `output/` media. Drive folders + hash evidence preserve pilot artifacts. Return to main:

```powershell
git switch main
git pull --ff-only
```

See [RELEASE_AND_ROLLBACK.md](RELEASE_AND_ROLLBACK.md).

## Required recreate directories / files

To recreate the system you need:

| Path | Role |
| --- | --- |
| `krishna_story_factory/` | Application code |
| `run_daily_story.py` | CLI |
| `scripts/` | Wrappers, bootstrap, scheduler, diagnostics |
| `tests/` | Gates and release evidence tests |
| `input/` | Master plan, series plan, content rules, recipients CSV |
| `prompts/` | Generation + master agent prompt |
| `docs/` | Canonical docs + `docs/releases/` |
| `requirements.txt` | Dependencies |
| `.env.example` | Env template (copy to local `.env`) |
| `assets/reference/` | Optional image style references |
| `tracking/` | Runtime queue/logs (local; templates if present) |
| `credentials/` | Local Drive OAuth only (never commit) |
| `output/` | Local packages (never commit) |
| `.venv/` | Created by `scripts/bootstrap.ps1` (Python 3.12) |

## Related canonical docs

- [ARCHITECTURE.md](ARCHITECTURE.md)  
- [CONTENT_STANDARD.md](CONTENT_STANDARD.md)  
- [DAILY_OPERATIONS.md](DAILY_OPERATIONS.md)  
- [SETUP_AND_CREDENTIALS.md](SETUP_AND_CREDENTIALS.md)  
- [TESTING_AND_RELEASE_GATES.md](TESTING_AND_RELEASE_GATES.md)  
- [DRIVE_AND_PACKAGE_LAYOUT.md](DRIVE_AND_PACKAGE_LAYOUT.md)  
- [SCHEDULER.md](SCHEDULER.md)  
- [RELEASE_AND_ROLLBACK.md](RELEASE_AND_ROLLBACK.md)  
- [`../prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md`](../prompts/KRISHNA_STORY_FACTORY_MASTER_AGENT.md)  
