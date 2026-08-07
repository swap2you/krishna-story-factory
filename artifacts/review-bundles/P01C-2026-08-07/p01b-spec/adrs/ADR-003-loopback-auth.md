# ADR-003 — Loopback Studio auth; deprecate forgeable header

## Status

Proposed (P01B) — D06 / OD-10

## Context

`X-Bhava-Studio: 1` alone is forgeable (P01A R03). Bootstrap token defaults are weak for shared hosts (R04).

## Decision

Phase 1 trust boundary = loopback + valid Studio session. Private Knowledge API must require loopback and session/secret. Shared preview needs real auth and separate owner approval.

## Consequences

Local pilot remains usable; non-local preview blocked until later phase; header-only gate removed/hardened in P01C allowlist.
