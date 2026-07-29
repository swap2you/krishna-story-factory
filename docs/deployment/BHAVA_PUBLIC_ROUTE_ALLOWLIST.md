# Bhāva Public Route Allowlist

Routes and API patterns that may appear on a future **public** `bhava.me` edge. Anything not listed here should be treated as deny-by-default until explicitly added.

**Related:** `BHAVA_PRIVATE_ROUTE_DENYLIST.md`, `BHAVA_COMPLETE_ROUTE_AND_CONTROL_MATRIX.md`.

**Inventory basis:** `apps/web/app/**/page.tsx`, `apps/web/app/sitemap.ts`, `SiteHeader` / `SiteFooter`, public API routers.

---

## 1. Edge policy sketch

```text
default: deny
allow: exact and prefix patterns below
redirect: /blog → /knowledge (already in next.config)
block: denylist (studio, local factory, dev)
```

---

## 2. Marketing & trust (allow)

| Pattern | Notes |
| --- | --- |
| `/` | Home |
| `/about` | |
| `/contact` | mailto-only UX |
| `/faq` | |
| `/privacy` | |
| `/accessibility` | |
| `/source-permissions` | |

---

## 3. Library (allow)

| Pattern | Notes |
| --- | --- |
| `/library` | Hub |
| `/library/krishna-book` | Launch spine |
| `/library/srimad-bhagavatam` | Planned shelf OK |
| `/library/srimad-bhagavatam/canto/*` | Cantos 1–12 shells |
| `/library/bhagavad-gita` | |
| `/library/ramayana` | |
| `/library/rama-katha` | |
| `/library/ramacaritamanasa` | |
| `/library/dasavatara` | |
| `/library/caitanya-caritamrta` | |
| `/library/caitanya-bhagavata` | |
| `/library/prayers-mantras` | |
| `/library/teacher-resources` | |

---

## 4. Stories & printables (allow)

| Pattern | Notes |
| --- | --- |
| `/stories/*` | Published packages + unpublished placeholder (placeholder should send `noindex`) |
| `/printables` | Live package downloads + planned type cards |

Published content today: **001–009**. Higher numbers may render as preparation shells without leaking queue titles beyond intentional UX.

---

## 5. Learning (allow)

| Pattern | Notes |
| --- | --- |
| `/learning/children-youth` | |
| `/sunday-school` | Honest planned curriculum structure |
| `/teachers` | Class-pack tool (client-side) |
| `/preachers` | Outline tool (client-side) |
| `/prabhupada-vani` | Planned / governed shelf |

Also allow legacy redirects (not destinations):

| Pattern | Destination |
| --- | --- |
| `/vanani`, `/vani` | `/prabhupada-vani` |

---

## 6. Knowledge (allow)

| Pattern | Notes |
| --- | --- |
| `/knowledge` | Home + search entry |
| `/knowledge/search` | Query string `q` allowed |
| `/knowledge/topics` | |
| `/knowledge/learning-paths` | |
| `/knowledge/pathways/*` | Seeded pathway slugs |
| `/knowledge/scriptures` | |
| `/knowledge/prayers` | |
| `/knowledge/slokas` | |
| `/knowledge/questions` | |
| `/knowledge/questions/*` | Seeded Q&A |
| `/knowledge/ask` | Private ask (mailto) |
| `/knowledge/corrections` | mailto |
| `/knowledge/standards` | |
| `/knowledge/index` | |
| `/knowledge/recent` | |
| `/knowledge/report-link` | |
| `/knowledge/*` | Published article slugs only (loader must refuse drafts) |

Blog compatibility:

| Pattern | Notes |
| --- | --- |
| `/blog`, `/blog/*` | Redirect → `/knowledge` |

---

## 7. Public static / PWA assets (allow)

| Pattern | Notes |
| --- | --- |
| `/brand/*` | Logos and collection art under `public/brand` |
| `/_next/static/*` | Next build assets |
| `/robots.txt` | Contains studio Disallow |
| `/sitemap.xml` | Generated from `app/sitemap.ts` |
| `/favicon.ico` / app icons | As present in `public/` |
| Manifest / service worker paths | If/when PWA files are published |

---

## 8. Public API (allow — read-only)

Exposed to browsers via Next rewrite `/api/*` → API origin.

| Pattern | Methods | Notes |
| --- | --- | --- |
| `/api/v1/health` | GET | Liveness |
| `/api/v1/stories` | GET | List |
| `/api/v1/stories/{storyNo}` | GET | Detail |
| `/api/v1/stories/{storyNo}/assets/{filename}` | GET | Allowlisted filenames only |
| `/api/v1/stories/{storyNo}/waveform` | GET | Peaks |
| `/api/v1/collections` | GET | |
| `/api/v1/collections/{slug}` | GET | |
| Knowledge search/read endpoints under `/api/v1/...` that are documented read-only | GET | No draft leakage |

Web App Router helpers that proxy the same media (keep allowlisted):

| Pattern | Notes |
| --- | --- |
| `/api/v1/stories/[storyNo]/assets/[filename]` | `apps/web/app/api/...` proxy |
| `/api/v1/stories/[storyNo]/waveform` | web proxy |

---

## 9. Explicitly not on this allowlist

See denylist for `/studio`, `/dev`, `/api/v1/local`, `/api/studio`, factory mutating verbs, and any admin CMS.

Draft Knowledge roadmap records, unpublished factory packages, and credential paths are **never** allowlisted.

---

## 10. Sitemap alignment task

Before public SEO, ensure `apps/web/app/sitemap.ts` only emits allowlisted **indexable** URLs and includes Stories through the current published max (001–009), not an outdated 001–007 loop.
