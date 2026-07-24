# 12 — Knowledge 348-Record Public Gate

## Local roadmap data

`content/knowledge/roadmap/records.json` independently parsed:

- **Total records: 348** (matches expected count)
- `lifecycle`: 100% `source_research` (348/348) — i.e., every record is still at the research/backlog stage
- `package_status`: 100% `research_backlog` (348/348) — none have progressed to published/reviewed status
- `visibility`: 340 `public`, 8 `restricted_review`
- `pillar` distribution: Sanatana-dharma (31), Gaudiya Vaisnavism (47), ISKCON (20), Practice (67), Prayer and Sloka (44), Culture and Festivals (41), Devotee Lives (22), Holy Places (20), Teaching Resources (18), Questions (24), Editorial Standards (14) — sums to 348

## Public-gate verification (live)

The public `/knowledge` page explicitly states: *"Public pages show approved resources only; the editorial roadmap stays private until reviewed."*

Independently confirmed this claim by attempting to fetch the roadmap and individual backlog topic IDs directly:

| Path attempted | Result |
|---|---|
| `/knowledge/TOP-0001` | 404 |
| `/knowledge/roadmap` | 404 |
| `/knowledge/roadmap/TOP-0001` | 404 |
| `/knowledge/what-sanatana-dharma-means` (slugified title guess) | 404 |
| `/api/v1/knowledge/roadmap` | 404 |
| `/api/v1/knowledge/records` | 404 |

None of the 348 backlog topic records are individually reachable via any public route or API endpoint tried. Spot-checked 5 random record IDs (TOP-0328, TOP-0058, TOP-0013, TOP-0141, TOP-0126) — all `research_backlog` / not separately routable.

## Verdict for this section

**PASS.** The 348-record roadmap is genuinely gated: it exists as internal planning data only, is accurately described as private/unreviewed on the public page, and no individual record is exposed through any route or API tested. No private-roadmap leakage found.
