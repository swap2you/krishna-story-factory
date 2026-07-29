# Lighthouse baseline — V1.6

Instance: http://127.0.0.1:3000
Captured: 2026-07-27T12:33:29.3460036Z

| Route | Perf | A11y | BP | SEO | LCP ms | CLS | TBT ms |
|-------|------|------|----|-----|--------|-----|--------|
| `/` | 69 | 100 | 100 | 100 | 8983 | 0.031 | 100 |
| `/library` | 69 | 98 | 100 | 100 | 39357 | 0 | 85 |
| `/stories/001` | 68 | 97 | 100 | 100 | 34487 | 0 | 236 |
| `/stories/008` | 70 | 97 | 100 | 100 | 42135 | 0 | 146 |
| `/knowledge` | 83 | 100 | 100 | 100 | 4169 | 0 | 67 |
| `/knowledge/search?q=Krishna` | 89 | 100 | 100 | 100 | 3469 | 0.002 | 84 |
| `/learning/children-youth` | 90 | 100 | 100 | 100 | 3395 | 0 | 70 |
| `/teachers` | 90 | 100 | 100 | 100 | 3341 | 0 | 84 |
| `/printables` | 85 | 100 | 100 | 100 | 3704 | 0 | 123 |
| `/contact` | 84 | 100 | 100 | 100 | 4073 | 0 | 78 |

## Targets

- Performance >= 85 (stretch on local headless)
- Accessibility >= 95
- Best Practices >= 90
- SEO >= 90
- CLS <= 0.1

Material fixes applied only when scores show clear overfetch/CLS/font blockers. Local headless Lighthouse is a baseline, not a field device claim.
