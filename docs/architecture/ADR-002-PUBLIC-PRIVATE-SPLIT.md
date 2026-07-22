# ADR-002 — Public / Private Split

## Status

Accepted

## Context

Children and teachers need an open library. Operators need queue, generation, Drive, and scheduler controls. Mixing those surfaces would leak secrets and enable remote factory abuse.

## Decision

1. **Public web** (`apps/web` public routes) talks only to read-only catalog APIs and static/media asset routes.
2. **Factory Studio** lives under a private route group and is documented as localhost-only.
3. **Local factory API** binds exclusively to `127.0.0.1`, with CSRF, origin allowlist, and operation allowlist.
4. Public production deployments must omit or reverse-proxy-block `/api/v1/local/*`.

## Consequences

- Clear threat model for child privacy and operator safety.
- Studio features can evolve without expanding the public attack surface.
