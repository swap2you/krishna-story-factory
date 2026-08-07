# Wireframes — Golden Prayer Page (text wireframes)

Placeholders only. No production artwork. Private preview (D06).

## Mobile 320px

```
┌────────────────────────────┐
│ [Bhāva]  ≡                 │
├────────────────────────────┤
│ KNOWLEDGE · PRIVATE        │
│ H1 Prayer title            │
│ [status: blocked|preview]  │
│ [hero art placeholder]     │
├────────────────────────────┤
│ Lens: ( LL | EX | TN | ST )│  ← 44px min height
├────────────────────────────┤
│ Purpose: one sentence…     │
├────────────────────────────┤
│ STANZA 1                   │
│ Devanāgarī (wrap)          │
│ IAST (wrap, diacritics)    │
│ English translation        │
│ [lens explanation]         │
│ [art placeholder below]    │
├────────────────────────────┤
│ [ Focus mode ]             │
│ Practice: one gentle cue   │
│ Source ▸ (collapsed LL/EX) │
│ Related: (approved only)   │
│ [PDF] [DOCX]  (or disabled)│
│ Footer                     │
└────────────────────────────┘
```

Little Learner focus-first: one stanza + “Next idea” + always “Show all”.

## Tablet ~768px

- Lens control single row.  
- Art may sit beside text from ~720px if alt/contrast OK.  
- Source inline `<details>` (prefer over drawer).

## Desktop ≥1100px

```
┌──────────────────────────────────────────────┐
│ Header                                       │
├────────────────────────────┬─────────────────┤
│ Hero + lens + purpose      │ (Study/Teen)    │
│ Stanza column ~60–72ch     │ stanza jump     │
│ …                          │ source snapshot │
│ Practice / related / DL    │                 │
└────────────────────────────┴─────────────────┘
```

Little Learner: no right rail.

## 200% / 400% zoom

- Lens wraps to multiple rows; targets remain ≥44px.  
- Sticky header must not cover stanza heading.  
- 400%: force single column; suppress decorative motion/particles.  
- No clipped IAST/Devanāgarī.

## Print / PDF Letter & A4

```
[Header: title · version · Bhāva]
STANZA n
  Devanāgarī
  IAST
  English
  Source line
[keep-together: do not split unit]
[Footer: page · rights short]
```

Hide: site chrome, lens UI, focus chrome, download buttons.  
Validate Letter and A4; no orphan headings / blank overflow / split mantra units.
