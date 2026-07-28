# BHĀVA STORIES PRODUCTION LAUNCH — FINAL COWORK UAT

Independent UAT for the completed production-launch baseline (copyright + Unicode footers + single runtime).

## Authority

- Branch: `feature/bhava-portal-v1` only
- Do not create a PR or merge
- Do not modify `main` / tags
- CoWork may commit **only** reports, evidence, and screenshots

## Confirm before testing

```powershell
git switch feature/bhava-portal-v1
git fetch origin
git status -sb
git rev-parse HEAD
git rev-parse origin/feature/bhava-portal-v1
```

Require local HEAD == origin. Record the product SHA under test.

## Runtime

Exactly one instance:

- Name: `bhava-final`
- Web: `http://127.0.0.1:3000` (open this only)
- API: `http://127.0.0.1:8000` (via Next proxy)

Confirm stale instance `runtime.json` files were removed and only `bhava-final` remains active.

## Checklist

### Git / SHA

- [ ] Product SHA matches the launch evidence metadata
- [ ] Working tree clean aside from CoWork evidence commits
- [ ] No PR / merge / main / tag changes

### Copyright identity

- [ ] Owner spelling **Svarna** Gauranga Das (never Swarna)
- [ ] Publisher imprint: Dauji Publication
- [ ] Project: **Bhāva** (real ā — no black box / tofu)
- [ ] Email: svarnagaurangdas@gmail.com
- [ ] No phone number
- [ ] Central config: `config/publication_identity.yaml`

### Unicode / printables

- [ ] No black boxes in Bhāva, Kṛṣṇa, Pūtanā, or other diacritics on PDFs/images
- [ ] Every activity PDF page has a compact footer
- [ ] Final Rights and Credits page remains
- [ ] Footer does not overlap titles, page numbers, answers, cut lines, or artwork
- [ ] Poster/coloring credit strips use a Unicode font below artwork
- [ ] Sacred imagery unobstructed
- [ ] Version `2.1.0-copyright` archived; public version `2.1.1-copyright`
- [ ] Story narrative before Rights and Credits unchanged vs 2.0 masters

### Website

- [ ] Footer © 2026 Svarna Gauranga Das + Dauji Publication line
- [ ] `/rights` page live with limitations + registration disclaimer
- [ ] Sitemap includes Stories 001–009 and `/rights`
- [ ] Sitemap excludes Story 010 and Studio/dev mutation routes

### Stories 001–009

- [ ] Exact eight files each
- [ ] `manifest.json` contains `rights` sidecar
- [ ] Archives under `output/_archive/pre-copyright/<n>/2.0/` and `.../2.1.0-copyright/`
- [ ] Sound-recording claim `needs_manual_review`
- [ ] Drive not mutated

### Safety

- [ ] No Story 010 output (`story_010_output_absent: true`)
- [ ] Queue 009 done / 010 pending
- [ ] Scheduler not triggered; providers not called

### Accessibility / security / Playwright

- [ ] Production npm audit zero
- [ ] Zero critical/serious axe findings (documented WebKit-mobile skips only)
- [ ] Full Playwright matrix zero-failure on product SHA
- [ ] Raw WebKit notes rerun exists and passes
- [ ] Screenshot/render evidence includes rights pages and PDF page renders

## Verdict

Return one of:

```text
READY FOR PRODUCTION / PASS WITH NON-BLOCKING NOTES / BLOCKED
```

with SHA, runtime URL, and evidence paths.
