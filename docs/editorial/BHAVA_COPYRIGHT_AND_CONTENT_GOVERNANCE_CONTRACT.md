# Bhāva Copyright and Content Governance Contract

**Operational framework — not legal advice.**  
Extends [BHAVA_COPYRIGHT_AND_RIGHTS_POLICY.md](../legal/BHAVA_COPYRIGHT_AND_RIGHTS_POLICY.md) for editorial and generator gates.

Identity config: `config/publication_identity.yaml` via `krishna_story_factory.publication.get_identity()`.

## Original vs preexisting materials

| Category | Bhāva may claim | Treatment |
| --- | --- | --- |
| Original writing, adaptation, selection/arrangement, activities, layout, human narration performance | Yes (when human authorship standard met) | Copyright notice + manifest `rights` block |
| Krishna Book / ŚB **facts and pastime boundaries** | No ownership of scripture | Source attribution only; link Vedabase where appropriate |
| Verbatim verses, purports, Prabhupāda lectures/letters | No | Quote only when explicitly supplied; cite source |
| Third-party art, fonts, music, photos | No | License evidence required before use |
| AI-generated expressive content | Limited | [BHAVA_AI_ASSISTANCE_AND_AUTHORSHIP_POLICY.md](../legal/BHAVA_AI_ASSISTANCE_AND_AUTHORSHIP_POLICY.md) |

**Generator rule:** Every new story records `source_reference`, `scripture_reference`, and rights metadata in `manifest.json`. Do not invent “original scripture.”

## “Used with permission” gate

**Never** display “used with permission,” “licensed from,” or equivalent on public pages unless **all** are true:

1. Written permission or license artifact on file (path recorded in manifest or rights inventory).  
2. Scope covers the exact use (web, printables, audio, geographic).  
3. Attribution text matches the grant (not boilerplate).  
4. Senior editorial sign-off logged.

If evidence is missing → use neutral source attribution only (e.g. “Based on Krishna Book Chapter N”) or omit the asset.

Production v3 spot-check: no unsupported “used with permission” on live stories ([BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md](../releases/BHAVA_PRODUCTION_001_020_V3_FINAL_STATUS.md)).

## Controversial-content review gate

Trigger **mandatory** human review before publish when content includes:

| Trigger | Review focus |
| --- | --- |
| Demon / violence pastimes | Child-safe framing; no graphic detail |
| Gender, marriage, kidnapping pastimes (later KB chapters) | Age-appropriate omission or gentle summary |
| Cross-tradition imagery (e.g. Durgā eight-armed form) | Respectful, source-faithful, non-polemical |
| Political or sectarian conflict | Stay inside KB boundary; no modern politics |
| Health/safety activities | Parent/teacher note accuracy |
| New external quotes or translations | Rights + fidelity |

**Workflow:**

1. Author flags `controversial_review_required=true` in work metadata (021+).  
2. Reviewer records decision: `approved` \| `revise` \| `defer` with notes.  
3. Publish gate blocks `publishable=true` until `approved`.  
4. Deferrals documented in release notes — not silent ship.

Stories **001–020:** no retroactive content changes in this phase unless explicit defect approval.

## Manifest and public surface

- `/rights` and footer notices must match `publication_identity.yaml`.  
- Do not publish `contact_email` in story rights cards unless policy explicitly enables it.  
- Sound recording ℗ line only when `sound_recording_claim_status=approved`.  
- Do not invent first-publication year when `first_publication_date` is unreviewed.

## Evidence and inventory

| Artifact | Purpose |
| --- | --- |
| `docs/legal/BHAVA_STORIES_001_009_RIGHTS_INVENTORY.md` | Historical rights matrix |
| `docs/product/launch/cowork-final/01_COPYRIGHT_MATRIX.md` | Launch evidence |
| `docs/legal/templates/FUTURE_GENERATOR_COPYRIGHT_INTERFACES.md` | Future format hooks |

## Non-goals

- Not a substitute for U.S. Copyright Office registration ([BHAVA_REGISTRATION_READINESS_GUIDE.md](../legal/BHAVA_REGISTRATION_READINESS_GUIDE.md)).  
- Not authorization to scrape third-party media libraries.  
- No commit of `.env`, credentials, or permission PDFs to git.
