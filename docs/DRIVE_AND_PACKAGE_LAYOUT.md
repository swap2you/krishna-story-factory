# Drive and Package Layout

## Exact eight-file package

Local path: `output/<chapter_no>_<slug>/`

| # | File | Role |
| --- | --- | --- |
| 1 | `story.md` | Story Format V2 (no YAML frontmatter) |
| 2 | `narration.mp3` | TTS from Audio Narration |
| 3 | `story_poster.png` | Cinematic poster |
| 4 | `coloring_page.png` | Line-art coloring page |
| 5 | `simple_coloring_page.png` | Simpler coloring page |
| 6 | `activity_sheet.pdf` | Activity Engine V2 printable |
| 7 | `whatsapp_caption.txt` | Parent caption + Drive link |
| 8 | `manifest.json` | Metadata, QA, publishable, package_link |

No video. Intermediates (`line_art_prompt.txt`, raw images, staging) are **not** final package members.

## Drive folder layout

```text
<GOOGLE_DRIVE_FOLDER_ID parent>
  ├── 001_<slug>/   (eight files)
  ├── 002_<slug>/
  ├── …
  └── NNN_<slug>/
```

When `GOOGLE_DRIVE_UPLOAD_ENABLED=true`, each prod success:

1. Ensures `<chapter_no>_<slug>` under the parent.  
2. Uploads exactly the eight finals.  
3. Sets `manifest.package.package_link` and updates the caption.  
4. Logs to `tracking/storage_log.csv`.  

Pilot parent folder is configured in local `.env` (see `.env.example` and release lock). Parents get Viewer on the parent; uploader needs Editor.

## Local sync fallback

If API upload is off but `GOOGLE_DRIVE_LOCAL_SYNC_ROOT` points at a synced Drive folder, the pipeline can copy the package there and still use the configured parent URL pattern.

## Connectivity test

```powershell
.\scripts\test_google_drive_upload.ps1
```
