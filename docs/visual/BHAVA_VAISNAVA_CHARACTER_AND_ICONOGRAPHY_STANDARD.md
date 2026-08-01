# Bhāva Vaiṣṇava Character and Iconography Standard

**Scope:** Stories **021+** (future generation).  
**Phase constraint:** Do **not** modify Stories **001–020** packages, posters, or coloring pages in this phase.

Audience: children **6–12**. Visuals must stay warm, devotional, child-safe, and faithful to Gauḍīya Vaiṣṇava presentation without graphic horror.

## Purpose

Lock a repeatable visual identity for human and demonic characters so poster, coloring, and simple-coloring pipelines produce consistent, reviewable art from Story 021 onward.

Related: [CONTENT_STANDARD.md](../CONTENT_STANDARD.md), `krishna_story_factory/visuals/models.py`, `krishna_story_factory/images/vision_qa.py`.

## Tilaka (Gauḍīya ūrdhva-puṇḍra)

| Rule | Requirement |
| --- | --- |
| Style | **Gauḍīya ūrdhva-puṇḍra** — two vertical clay marks on the forehead (not horizontal tripundra, not secular bindi-only decoration) |
| Material | Gopī-candana / tilaka clay appearance when marks are visible |
| Who wears it | Named Gauḍīya Vaiṣṇava devotees in scene (when age-appropriate and story-faithful): brāhmaṇas, sages, teachers, adult gopīs/gopas when depicted as devotees — not forced on every background figure |
| Kṛṣṇa / Balarāma | Follow pastime-appropriate form (infant/toddler/boy); do not add adult devotee tilaka unless the pastime calls for it |
| Demons / asuras | **No** Vaiṣṇava tilaka on antagonists |

## Tulasī beads

| Rule | Requirement |
| --- | --- |
| Who wears them | Named Gauḍīya Vaiṣṇava devotees when depicted in devotional dress |
| Presentation | Single strand at neck; respectful, not costume jewelry |
| Must avoid | Tulasī on demons; broken or disrespectful placement; using beads as generic “Indian necklace” without devotional context |

## Character identity

Each named figure in a visual brief must be identifiable across poster and both coloring pages:

- **Role** — e.g. mother, king, demon messenger, brāhmaṇa  
- **Devotional identity** — `gauḍīya_vaiṣṇava_devotee`, `vaiṣṇava_child`, `neutral_village`, `demon_child_safe`, `demigod`, `lord_pastime_form`  
- **Stable cues** — clothing palette, hair, age band, signature object (flute, cart, rope, etc.)  
- **Expression** — child-safe; fear without gore; mercy without sentimental caricature  

Reuse the same identity block in poster and coloring briefs for a given story.

## Child-safe demons

Demons must read as **clearly non-human or clearly antagonist** without nightmare imagery:

| Must show | Must avoid |
| --- | --- |
| Exaggerated but non-gory features (size, shadow, storm, distorted silhouette) | Blood, open wounds, rotting flesh, realistic corpses |
| Kṛṣṇa/Balarāma calm or playful amid danger | Torture, binding children, sexualized forms |
| Pastime-appropriate scale (e.g. Pūtanā: giant form **after** defeat, not seductive close-up) | Horror-movie lighting, fangs dripping, occult symbols |
| Gentle distance in coloring pages (outline-friendly) | Weapons pointed at viewer; graphic impalement |

When a pastime requires a fallen body, show **distant or symbolic** treatment; prefer aftermath with focus on Kṛṣṇa’s safety and mercy.

## Crop-aware QA

Posters and coloring pages are cropped in the web UI and printables. Review at export aspect ratios, not only full canvas.

| Surface | QA focus |
| --- | --- |
| Poster (`story_poster.png`) | Hero faces and tilaka remain inside safe title band; no critical detail in bottom 15% (caption/overlap zone) |
| Coloring (`coloring_page.png`) | Line weight ≥ child usability threshold; central scene centered for A4/Letter print |
| Simple coloring | Larger shapes; verify tilaka/beads still recognizable at reduced complexity |
| Header/footer crops | Run `object-fit: cover` simulation — tilaka must not be clipped off foreheads |

Vision QA prompts (`vision_qa.py`) must include: faithfulness to brief, child safety, coloring usability, **crop-safe composition**.

## Future visual-brief fields (021+)

Add these to poster/coloring brief JSON (extends `VisualBrief` in `models.py`):

| Field | Type | Purpose |
| --- | --- | --- |
| `tilaka_requirement` | enum | `required` \| `optional` \| `forbidden` \| `not_applicable` |
| `tilaka_style` | string | e.g. `gauḍīya_ūrdhva_puṇḍra` |
| `tulasi_beads_requirement` | enum | `required` \| `optional` \| `forbidden` \| `not_applicable` |
| `character_devotional_identity` | map | Per named character → identity enum + notes |
| `must_show` | list | Non-empty; scene-specific required elements |
| `must_avoid` | list | Non-empty; inherits global child-safe + iconography bans |
| `cultural_context` | string | Short note for reviewers (e.g. “Vraja village morning, no Mathurā royal dress”) |
| `reviewer_status` | enum | `draft` \| `pending_review` \| `approved` \| `defer` |

Validation: `must_show` / `must_avoid` non-empty; event-relevance keywords per `event_relevance.py`; `reviewer_status=approved` required before prod image spend on 021+.

## Global must_show / must_avoid (all 021+ visuals)

**Must show (when characters present):** pastime-faithful central action; respectful treatment of Kṛṣṇa/Balarāma; source-aligned setting; readable child faces.

**Must avoid:** wrong tilaka tradition; tulasī on demons; graphic violence; modern logos/watermarks; text baked into coloring line art; unrelated pastimes; romanticized adult themes; weapons as focal toy-like props.

## Review workflow

1. Author fills brief fields from `series_plan.csv` boundaries.  
2. Editorial pass on `cultural_context` + demon safety.  
3. Sample poster/coloring in **test mode** (no paid regen of 001–020).  
4. Crop-aware vision QA PASS → set `reviewer_status=approved`.  
5. Promote only after exact-eight package gate.

## Explicit non-goals (this phase)

- No retroactive reposter or recolor for Stories **001–020**.  
- No change to locked Stories **001–006** without explicit senior approval.  
- No new paid API batch runs solely to backfill tilaka on published art.
