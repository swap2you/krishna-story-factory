# Bhāva V1.1 — Claude Adversarial Review

**Branch:** `feature/bhava-portal-v1`  
**Reviewer role:** adversarial product / legal / identity / child-safety  
**Date:** 2026-07-23

## Attack surface checked

| Threat | Result |
| --- | --- |
| Public Read leaks production briefs / SSML | Mitigated via parser + e2e/API leak tests |
| Civil identity (`Swapnil`, LinkedIn, GitHub site) on public pages | Mitigated; only `Svarna Gauranga Das` + steward email |
| Fabricated ślokas / false Prabhupāda quotes | Public ślokas pending; reflections marked needs_review / package seeds |
| “Used with permission” without grant | Source notes use `excerpt-needs-review` and explicit non-claim language |
| Copyright exposure of KrishnaBook.pdf | Ignored, untracked, unserved |
| Hidden paid API calls from portal | None in V1.1 paths |
| Public Studio production controls | Loopback + CSRF; actions disabled |
| Child notes uploaded | Notes remain localStorage-only |

## Residual adversarial notes (non-blocking)

- Vedabase links are chapter-level verified URLs, not verse deep-links for every story boundary.
- Teaching reflections seeded from package lessons still need human review before quoting as teaching canon.
- Sunday School / Preachers workspaces are planning tools; they must not be mistaken for licensed curriculum republication.

## Verdict

**PASS for release candidate.** Required DEF-01 / DEF-02 class defects addressed. No blocker found that should stop CoWork UAT.
