# 13 — Knowledge Pathways & Search

## Search functionality — live verification

Initial probe against a guessed REST endpoint (`/api/v1/knowledge/search?q=...`) returned `count: 0` for multiple genuine terms ("Krishna", "Bhagavad", "Sanatana-dharma"). This looked like a broken search at first, **but this was a false alarm caused by using the wrong endpoint** — the app does not expose that path as a working query API.

The actual product search was then tested through the real UI: typed "Krishna" into the `/knowledge` page's search box (`Search articles, questions, and published guides`) and submitted via the Search button. This correctly navigated to `/knowledge/search?q=Krishna` (a server-rendered Next.js route, HTTP 200) and returned genuine, relevant results:

- "Sources and permissions — How Bhāva cites Krishna Book and related scripture without claiming blanket BBT ownership."
- "What is Bhāva? — Bhāva is an independent curated devotional-learning portal beginning with Krishna Book bedtime stories." (returned twice, once as an article and once as a Q&A entry)

**Correction to initial hypothesis:** search is implemented and functions correctly; my first test used a nonexistent API path, not a defect in the product. This is documented here in the interest of full transparency about the review process, not as a product defect.

## Pathways / topics navigation

The `/knowledge` landing page exposes structured pathway groups (all live-rendered, not stubs):

- Learn the foundations: New to Bhakti, Scriptures, Learning paths
- Practice & worship: Daily Practice, Prayers & Āratis, Ślokas & Stutis, Deity Worship
- Community & service: Families & Children, Teachers, Preachers, Sunday School
- Ask & standards: Q&A, Ask privately, Suggest a correction, Editorial standards
- Alphabetical index, Recently updated, Published guides

## Verdict for this section

**PASS.** Real, working search confirmed via the actual UI. Pathway navigation structure is present and functional.
