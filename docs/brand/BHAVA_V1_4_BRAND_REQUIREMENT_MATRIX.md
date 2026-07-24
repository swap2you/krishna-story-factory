# Bhāva V1.4 — Brand Requirement Matrix

Precedence: final acceptance → inventory → QA → exports → references → phase batches as provenance only.

| Requirement | Canonical asset | App surface | Status |
|-------------|-----------------|-------------|--------|
| Desktop header logo | `logo-small-header` (3600×520) / compact horizontal | Header `.brand-logo-header` true aspect | `implemented_not_verified` |
| Mobile identity | `logo-icon-only` + live `bhāva` text | Header mobile lockup | `implemented_not_verified` |
| Footer dark logo | `logo-dark-bg` | Footer | `implemented_not_verified` |
| Favicon / PWA | icon-only / platform icons | `metadata.icons` | `implemented_not_verified` |
| Primary horizontal | `logo-primary-horizontal` checksum `8be35441…` | Available; comparison page | `partial` |
| Monochrome print | `logo-mono-*` | Printables / print CSS | `partial` |
| 12 canto covers | `collection-canto-01`…`12` | Library canto grid | `implemented_not_verified` |
| Collection covers | library cards | Library | `implemented_not_verified` |
| Contact/FAQ heroes | `hero-contact-*` / `hero-faq-*` | Contact, FAQ | `implemented_not_verified` |
| Knowledge cover | `collection-bhakti-blog` | Knowledge intro | `implemented_not_verified` |
| Empty states / learning icons | `/empty-states`, `/icons` | Various | `partial` |
| Social/OG | `/social` | metadata | `partial` |

No approved asset may be claimed complete from import alone — rendering must be verified in live UAT.
