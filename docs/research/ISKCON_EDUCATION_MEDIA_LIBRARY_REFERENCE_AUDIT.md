# ISKCON Education Media Library — Reference Audit

**Purpose:** Capture a **reference taxonomy** useful for Bhāva’s future Resource Library, inspired by how ISKCON education / media libraries commonly organize materials for teachers and families.  
**Hard constraint:** This is a **research / mapping** document only. Do **not** download, scrape, mirror, rehost, or copy third-party media into this repository from this audit.

**Non-goals:** No ingestion pipeline execution, no rights clearance, no URL harvesting into `content/`, no binary assets.

---

## 1. Why audit reference libraries?

Bhāva already separates:

- **Story packages** (locked eight-file Krishna Book bedtime outputs)
- **Knowledge** (curated MD/JSON under `content/knowledge`)
- **Learning surfaces** (Teachers, Sunday School, Preachers, Printables — often planned)

External education libraries show proven facets for *finding* materials. Bhāva can adopt facet *names* and *workflows* without adopting their files.

---

## 2. Reference taxonomy axes

Most ISKCON-oriented education/media catalogs cluster items along four primary axes (names vary by site; concepts are stable):

### 2.1 Level (audience readiness)

| Level (reference concept) | Typical use | Bhāva mapping hint |
| --- | --- | --- |
| Early childhood / preschool | Short stories, songs, simple art | Little Listeners (5–7) |
| Children’s primary | Chapter stories, coloring, basic śloka | Young Explorers (8–12) |
| Teen / youth | Deeper kathā, Q&A, leadership | Teen Seekers / Youth Leaders |
| Adult / congregational | Lecture series, study guides | Families & Educators / Preachers |
| Teacher / facilitator | Lesson plans, training | `/teachers`, Sunday School |

**Audit note:** Level is about *learner readiness*, not scripture “advancement” claims. Keep language humble and non-sectarian-judgmental in UI.

### 2.2 Type (pedagogical role)

| Type | Examples in reference libs | Bhāva today |
| --- | --- | --- |
| Story / kathā | Chapter readings, pastime modules | `/stories/*`, Krishna Book shelf |
| Lesson plan | Weekly Sunday School outlines | `/sunday-school` (structure) |
| Activity / printable | Worksheets, coloring | `/printables` live + planned types |
| Audio / kīrtana | Songs, narrations | Story `narration.mp3`; Vāṇī planned |
| Video | Class recordings, festivals | Not a Bhāva launch surface |
| Lecture / class | Guru / speaker recordings | Prabhupāda Vāṇī shelf (planned, rights-gated) |
| Scripture study | Gītā/SB study packs | Library shelves (planned depth) |
| Prayer / ārati | Liturgy sheets | `/library/prayers-mantras`, Knowledge prayers |
| Training | Teacher certification modules | Out of scope for launch |
| Reference / FAQ | Policy & orientation docs | `/knowledge`, `/faq` |

### 2.3 Format (delivery medium)

| Format | Notes for Bhāva |
| --- | --- |
| HTML article | Knowledge MD → SSR pages |
| PDF | `activity_sheet.pdf` and future teacher packs |
| PNG / image | Posters, coloring pages |
| MP3 / audio | Narration; waveform companion |
| Markdown / plain text | Source packages, preacher export TXT |
| Slide deck | Not used yet |
| Video stream | Not used; do not embed third-party players without review |
| External link-out | Prefer for uncleared third-party catalogs (no rehost) |

### 2.4 Theme (topical / scriptural theme)

Reference libraries often tag by festival, deity, virtue, or scripture book. Useful theme buckets for Bhāva alignment:

| Theme bucket | Examples |
| --- | --- |
| Krishna Book / childhood pastimes | Stories 001–009 spine |
| Śrīmad-Bhāgavatam | Canto shelves |
| Bhagavad-gītā | Gītā shelf |
| Caitanya līlā | CC / CB shelves |
| Rāma-kathā | Rāmāyaṇa family shelves |
| Practice & sādhana | Daily practice pathway |
| Festivals | Janmāṣṭamī, Gaura Pūrṇimā (future) |
| Holy places | Tīrtha orientation (Knowledge pillars) |
| Values / character | Kindness, courage, protection themes in bedtime stories |
| Teacher craft | Classroom management, age bands |

### 2.5 Source (provenance — always required)

Reference catalogs sometimes bury provenance. Bhāva must surface it:

| Source class | Meaning |
| --- | --- |
| Bhāva original | Written/illustrated for Bhāva |
| BBT publication (reference) | Cite / adapt carefully; no full-book republication |
| ISKCON institutional education dept. | Curriculum frameworks — link-out until cleared |
| Temple / local Sunday School | Local packs — permission per temple |
| Independent devotee educator | Third-party — explicit license needed |
| Public domain / traditional | Still verify edition & translation rights |
| Unknown | Treat as `pending_review` — not public |

---

## 3. Observation patterns (without naming scrape targets)

Across typical ISKCON education/media library UIs, auditors should expect:

1. **Browse by age** and **browse by topic** as dual entry points.  
2. **Download buttons** that often point to Google Drive / institutional CDNs — **public link ≠ license to rehost**.  
3. **Mixed rights** in one folder (free classroom use vs. all-rights-reserved media).  
4. **Lecture audio** adjacent to **children’s crafts** — different Level/Type; don’t flatten.  
5. **Language variants** (English, Hindi, etc.) as a separate facet (see Bhāva taxonomy proposal).  
6. **“For teachers”** gates that are social/trust gates, not technical DRM.

Bhāva should copy the *facet clarity*, not the *file corpus*.

---

## 4. Gaps vs Bhāva launch surface

| Reference capability | Bhāva launch | Action |
| --- | --- | --- |
| Unified cross-type search | Knowledge search + story catalog separate | Future Resource Library index |
| Festival calendar packs | Not launch-critical | Planned theme facet |
| Video class library | Absent | Stay link-out / out of scope |
| Bulk ZIP curricula | Absent | Prefer per-asset rights |
| Multi-language UI | English-first | Language facet ready in taxonomy |
| Institutional login libraries | N/A | Bhāva remains open-read curated |

---

## 5. Safe research workflow (for humans)

1. Browse reference sites manually in a normal browser.  
2. Record **facet labels** and **example item titles** only in notes.  
3. Capture **license / copyright / “for personal use”** wording as quotes in the rights plan — not the media.  
4. Never use wget/curl/yt-dlp/scrapers against education libraries for this project track.  
5. Never commit third-party binaries “for convenience.”  
6. If a steward later obtains written permission, follow `BHAVA_EXTERNAL_RESOURCE_RIGHTS_AND_INGESTION_PLAN.md`.

---

## 6. Outputs of this audit (usable by Bhāva)

- Facet vocabulary: **Level / Type / Format / Theme / Source**  
- Confirmation that Printables + Stories already cover a children’s media subset  
- Confirmation that Vāṇī / lecture-like material is **rights-heavy** and must stay planned until cleared  
- Input into `BHAVA_RESOURCE_LIBRARY_TAXONOMY_PROPOSAL.md`

---

## 7. Explicit prohibition reminder

**Do not download or rehost** ISKCON education media library content as part of implementing or “completing” this audit. Reference ≠ inventory of files we may copy.
