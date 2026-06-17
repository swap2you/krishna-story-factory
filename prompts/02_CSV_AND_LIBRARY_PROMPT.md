# 02 CSV and Library Prompt

Implement and validate CSV-driven source management.

Primary queue:
- `input/series_plan.csv`

Required columns:
- `chapter_no`
- `slug`
- `title`
- `library_id`
- `source_reference`
- `scripture_reference`
- `summary_seed`
- `age_range`
- `package_type`
- `send_date`
- `devotional_focus`
- `activity_type`
- `status`
- `created_at`
- `notes`

Library catalog:
- `input/library_catalog.csv`

Supported libraries:
- `krishna_book`
- `srimad_bhagavatam`
- `bhagavad_gita`
- `ramayana`
- `ramcharitmanas`
- `amar_chitra_katha`

For Amar Chitra Katha, mark as `inspiration_only`. Do not reproduce copyrighted text, captions, panels, or layouts.

Tracking files:
- `tracking/story_log.csv`
- `tracking/send_log.csv`
- `tracking/quality_log.csv`

Keep backward compatibility with old `series_plan.csv` if optional columns are missing.

Deliverable: tests for CSV reading, pending row selection, and status updates.
