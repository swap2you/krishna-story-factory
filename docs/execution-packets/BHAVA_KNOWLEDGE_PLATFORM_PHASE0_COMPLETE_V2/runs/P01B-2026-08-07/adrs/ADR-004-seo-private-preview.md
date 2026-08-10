# ADR-004 — SEO exclusions for private preview

## Status

Proposed (P01B)

## Decision

Every private-preview page: `noindex,nofollow,noarchive` (+ optional `X-Robots-Tag`). Never add preview/roadmap IDs to sitemap. Robots Disallow complements but is not a security control.

## Consequences

Aligns with P1-F09; public article indexing unchanged.
