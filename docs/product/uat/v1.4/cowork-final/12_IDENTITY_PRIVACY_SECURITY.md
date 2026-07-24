# V1.4 Identity, Privacy, and Security Spot Checks

## Public identity — verified live

Footer, rendered on every page tested: **"Stewarded with care by Svarna Gauranga Das · Harrisburg, Pennsylvania"**. No civil name.

Contact page (`/contact`) email resolved directly: the live, rendered email is **`svarnagaurangdas@gmail.com`** — matching the V1.3 spelling, not the V1.4 mission text's `svarnagaurangadas@gmail.com` (extra "a"). This is most likely a typo in the mission text rather than a product defect, since the app's spelling is stable and consistent with the prior release. `document.body.innerText` on `/contact` was regex-scanned for `swapnil|swap2you|swap2patil` — **no match** (`hasSwapnil: false`). No civil name or personal-portfolio leakage found on the Contact page.

## Security spot checks — verified live

| Check | Result |
|---|---|
| Public Knowledge search does not leak 348 private roadmap records | **Pass** — `count: 0` for a query matching 30+ roadmap pillar entries |
| Direct API access to roadmap collection/record | **Pass** — both return 404 |
| Story 008 not exposed | **Pass** — API 404; page renders honest "pending" shell with all backing calls 404; no link from Story 007 |
| `/dev/audio-lab`, `/dev/logo-sheet` absent from public nav/sitemap | **Pass** — both labeled "NOT IN NAV", neither referenced in `sitemap.xml` |
| `/studio` disallowed in `robots.txt` | **Pass** |
| Studio gated behind auth (not just hidden) | **Pass** — pre-auth view shows only the sign-in form, no data |
| No real secrets tracked in git | **Pass** — `git grep` for common secret-prefix patterns found none; `KrishnaBook.pdf` and `MyPilotDropbox/` both gitignored and untracked |

## Not tested this session

Path traversal on the media/asset proxy, CSRF, CORS policy, stored/reflected XSS, Markdown/MDX sanitization, submission rate limiting/honeypot, role-escalation attempts within the Studio, and source-rights-bypass attempts were **not** exercised this session — the mission's adversarial-review checklist (Section 15) was not run as a live penetration exercise; only the passive checks listed above were performed. `docs/reviews/BHAVA_V1_4_CLAUDE_ADVERSARIAL_REVIEW.md`'s claims (path traversal blocked, confidential patterns blocked, no release-blocking adversarial findings) were read but not independently re-verified live.
