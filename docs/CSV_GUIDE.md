# CSV Guide

## Main queue

`input/series_plan.csv`

Each row is one story package.

Required fields:

```text
chapter_no,slug,title,source_reference,scripture_reference,summary_seed,status
```

Recommended full fields:

```text
chapter_no,slug,title,library_id,source_reference,scripture_reference,summary_seed,age_range,package_type,send_date,devotional_focus,activity_type,status,created_at,notes
```

## Status values

Use these only:

```text
pending
generated
quality_pass
sent
failed
skipped
done
```

The current CLI marks completed rows as `done`.

## Library catalog

`input/library_catalog.csv`

Supported `library_id` values:

```text
krishna_book
srimad_bhagavatam
bhagavad_gita
ramayana
ramcharitmanas
amar_chitra_katha
```

`amar_chitra_katha` must be treated as inspiration only. Do not copy text or image layouts.

## Logs

`tracking/story_log.csv` records each run.

`tracking/send_log.csv` is reserved for detailed sender audit.

`tracking/quality_log.csv` is reserved for detailed quality audit.
