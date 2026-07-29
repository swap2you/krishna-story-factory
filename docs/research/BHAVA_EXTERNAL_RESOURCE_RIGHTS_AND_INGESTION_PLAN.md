# Bhāva External Resource Rights and Ingestion Plan

**Status:** Process plan for future external resources.  
**Core principle:** **Public availability ≠ permission.** A file on a temple Drive, education portal, or YouTube does **not** grant Bhāva rights to download, rehost, redistribute, or claim “used with permission.”

**Companion docs:**

- `docs/research/ISKCON_EDUCATION_MEDIA_LIBRARY_REFERENCE_AUDIT.md` (no download/rehost)
- `docs/research/BHAVA_RESOURCE_LIBRARY_TAXONOMY_PROPOSAL.md`
- `apps/web/app/source-permissions/page.tsx` (public provenance language)
- `docs/deployment/BHAVA_PRIVATE_ROUTE_DENYLIST.md`

This plan does **not** authorize ingestion in the Stories launch pass.

---

## 1. Scope

### In scope (future)

- Teacher worksheets, Sunday School outlines, prayer sheets, and media **after** documented clearance  
- Link-outs to canonical publisher pages  
- Short quotations / citations under documented policy  
- Bhāva-original derivatives that do not copy protected expression

### Out of scope / forbidden without counsel

- Scraping or bulk-downloading education media libraries  
- Uploading full BBT books or substantial reproductions  
- Using “used with permission” copy without a filed permission record  
- Committing third-party binaries “temporarily” into `output/` or `public/`  
- Auto-publishing AI-rewritten copyrighted passages

---

## 2. Roles

| Role | Responsibility |
| --- | --- |
| Steward | Final publish decision; contact channel for corrections |
| Rights reviewer | Verifies license / written permission / link-out-only |
| Scriptural reviewer | Fidelity & appropriate presentation (when content is spiritual teaching) |
| Editorial operator | Prepares metadata, taxonomy facets, public copy |
| Engineer | Implements loaders/gates; never bypasses rights flags |

Separation of duties: the person who finds a public URL should not alone mark `rights_status=licensed`.

---

## 3. Rights review workflow

```text
Discover → Classify → Contact/Permission → Document → Ingest decision → Publish gate → Monitor
```

### Step A — Discover (reference only)

- Record title, publisher, URL, date seen, and why it would help Bhāva learners.  
- Do **not** download the asset into the repo during discovery.  
- Set `rights_status=unknown`, `published_status=draft`, `review_status=unreviewed`.

### Step B — Classify source

Use public provenance vocabulary:

| `source_class` | Typical next action |
| --- | --- |
| `bhava_original` | Standard editorial review only |
| `bbt_source_reference` | Citation / adaptation rules; no full-text republication |
| `third_party` | Explicit permission or OSI/CC license verification |
| `pending_review` | Hold from public loaders |

Also set taxonomy `publisher`, `format`, `resource_type`.

### Step C — Determine permission basis

Acceptable bases (one required for public publish of third-party expression):

1. **Written permission** (email/letter) naming Bhāva, allowed uses, territory, duration, and media types.  
2. **Public license** that clearly allows the intended use (e.g. specific Creative Commons — read restrictions on adaptations/commercial).  
3. **Link-out only** — Bhāva publishes metadata + outbound link; no file hosting.  
4. **Citation-only excerpt** — short quotation with attribution under documented editorial policy (not a substitute for hosting chapters).

Reject bases:

- “It’s on the internet.”  
- “Another temple already mirrored it.”  
- “We gave credit in the filename.”  
- “Educational fair use” assumed without counsel for wholesale hosting.

### Step D — Document (internal)

Minimum clearance packet (store **outside** git or in a private steward vault — not in public web root):

| Field | Example |
| --- | --- |
| Resource working title | “Age 8–10 Janmāṣṭamī craft sheet” |
| Rights holder | Name / org |
| Permission basis | Written / license URL / link-out |
| Allowed uses | print classroom / on-site display / no audio / etc. |
| Expiry / revocation | Date or “until revoked” |
| Steward decision | approve / deny / link-out |
| `rights_doc_ref` | Internal id referenced from public metadata |

Public metadata may store `rights_doc_ref` as an opaque id; never commit the permission email body with personal phone numbers if avoidable.

### Step E — Ingest decision tree

| Decision | Repo action | Public action |
| --- | --- | --- |
| **Deny** | Keep notes only | Nothing |
| **Link-out** | Knowledge/external record with URL | Show card + external link + attribution |
| **Host under license** | Store asset in governed path after scan | Serve via allowlisted asset route |
| **Bhāva rewrite** | Original text/art only | `source_class=bhava_original` |

Hosting path requirements:

- Filename allowlist / virus scan as appropriate  
- No directory listing  
- Manifest entry with `rights_status` and `allowed_uses`  
- Loader refuses records failing rights + review + published gates

### Step F — Publish gate (all must pass)

- [ ] `rights_status` ∈ {`bhava_owned`, `licensed`, `permission_documented`, `citation_only`, `link_out_only`}  
- [ ] `review_status=approved`  
- [ ] `published_status=published`  
- [ ] Attribution string present when required  
- [ ] No “used with permission” unless `permission_documented`  
- [ ] For BBT-related material: no full-book or substantial-chapter dump  

### Step G — Monitor

- Honor takedown / revocation within a defined SLA (suggest 72 hours for public removal).  
- Corrections via `/knowledge/corrections` and `/contact`.  
- Periodic re-check of license URLs still valid.

---

## 4. Special cases

### 4.1 BBT publications

- Bhāva may **reference** Krishna Book and related works with clear non-ownership language (see About / Source permissions).  
- Bedtime story packages are Bhāva adaptations under the factory editorial process — still not a license to paste BBT text into Knowledge articles.  
- Śloka panels stay empty until curated verses are cleared (`excerpt-needs-review` style discipline).

### 4.2 ISKCON education media libraries

- Treat as **reference catalogs** for taxonomy only until a specific rights holder grants Bhāva permission.  
- Prefer link-out to the canonical institutional page.  
- Never bulk-mirror “for Sunday School convenience.”

### 4.3 Temple-local materials

- Permission from the creating temple / author, not assumed via congregational membership.  
- Record contact and date; scope classroom print vs. worldwide web download separately.

### 4.4 Audio / video

- Streaming vs download are different `allowed_uses`.  
- Do not hotlink media in ways that violate host ToS; prefer official embeds only when permitted — launch site currently focuses on Bhāva-hosted story narration.

---

## 5. Engineering checklist (when ingestion is later authorized)

1. Extend catalog/knowledge loaders to require rights + review + published triad.  
2. Add CI test: draft/unknown rights records never appear in public list fixtures.  
3. Asset proxy continues path-traversal protection and filename allowlists.  
4. Studio/Knowledge editorial UIs stay on denylist for public hosts.  
5. Logging: record publish events without storing secrets.

---

## 6. Launch posture (now)

| Activity | Allowed now? |
| --- | --- |
| Write taxonomy & rights docs | Yes |
| Browse reference libraries for facet names | Yes (no download tools) |
| Host new third-party PDFs/MP3s in repo | **No** |
| Claim blanket BBT permission in UI | **No** |
| Ship Stories 001–009 + Bhāva-original Knowledge seeds | Yes (existing gates) |

---

## 7. One-line steward reminder

If we cannot point to a clearance packet, we link out or we leave it unpublished — **public availability is not permission.**
