# Vendored Noto fonts (SIL Open Font License 1.1)

These fonts are vendored so Knowledge PDF export is deterministic on Windows,
Linux CI, and the production API container. Do not rely on host system fonts.

| File | Purpose |
|---|---|
| `NotoSansDevanagari-Regular.ttf` | Devanāgarī body in PDF exports |
| `NotoSans-Regular.ttf` | Latin / IAST / English in PDF exports |
| `OFL.txt` | SIL Open Font License 1.1 |
| `CHECKSUMS.sha256` | SHA-256 of the font binaries and license |

Sources: [notofonts/devanagari](https://github.com/notofonts/devanagari), [notofonts/latin-greek-cyrillic](https://github.com/notofonts/latin-greek-cyrillic).

Export fails closed if these files are missing or checksum-mismatched — no silent glyph fallback.
