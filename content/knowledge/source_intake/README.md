# Source intake (private)

Private metadata for owner-supplied PDF source candidates under Bhāva Unified Platform Build V2 (M1).

## Rules

- **Originals stay outside git.** Do not commit PDF binaries, OCR derivatives, or extracted text dumps here.
- **Inventory is metadata only.** `owner_pdf_inventory_v2.json` tracks filenames, staging status, and review flags — never PDF bytes.
- **`OCR_PENDING`** marks image-only PDFs that need a supported OCR path before dossier work. Do not fabricate text to clear the flag.
- **No public serving of PDF bodies.** Studio may list intake counts/status; public routes must not expose original files.

Canonical program inventory CSV (docs): `docs/unified-platform-v2/source_inventory/OWNER_PDF_INVENTORY.csv`.
Runtime ledger (this folder): `owner_pdf_inventory_v2.json`.

## Dossier stubs (M2)

Private JSON stubs live under `dossiers/<seq>-<slug>.json`. Status is `SOURCE_INCOMPLETE` until exact edition/locator, Devanāgarī, IAST, English, and rights clearance are evidenced. Do not copy PDF text into these files.

Golden-page decision: [`GOLDEN_PAGE_DECISION.md`](GOLDEN_PAGE_DECISION.md) — no new scripture golden package published while intake remains incomplete.
