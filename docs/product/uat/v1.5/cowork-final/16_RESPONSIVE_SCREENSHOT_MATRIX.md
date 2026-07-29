# 16 — Responsive / Screenshot Matrix

## Tooling limitation (confirmed again this session)

The `resize_window` tool was invoked against the live Claude-in-Chrome tab (target 390×844, a mobile viewport). The tool call itself reported success ("Successfully resized window containing tab ... to 390x844 pixels"), but a direct JS check immediately afterward (`window.innerWidth`/`innerHeight`) showed the real viewport remained **1920×854** — unchanged. This is the same limitation observed and documented in every prior V1/V1.1/V1.2/V1.3/V1.4 UAT cycle: `resize_window` does not actually alter the real browser viewport in this environment, despite reporting success. This is now a consistently reproduced, six-cycle-running tooling limitation, not a one-off flake.

## Consequence and mitigation

Because true mobile/tablet viewport emulation could not be independently forced this session, this review did **not** attempt to fabricate responsive screenshots at incorrect viewport sizes. Instead, responsive correctness relies on:

1. The official automated Playwright responsive suite, which genuinely does control real Chromium/Firefox/WebKit viewport sizes (not subject to this tool's limitation, since Playwright sets viewport directly rather than resizing an OS window): widths 390, 430, 768, 1024, 1366, 1440, 1920, all passing, per `docs/product/uat/v1.5/ROUTE_VISUAL_A11Y_MATRIX.md` and the `350 passed` overall Playwright result.
2. Manual DOM/CSS inspection at the sandbox's actual fixed viewport (1920×854), which is a valid desktop-width check but does not substitute for genuine narrow-viewport verification.

## Verdict for this section

**PASS WITH NON-BLOCKING NOTES.** Genuine narrow-viewport manual verification could not be independently performed due to a confirmed, repeatedly-reproduced tooling limitation (not a product defect). Automated Playwright responsive coverage (7 widths, all passing) is the substantive evidence for responsive correctness this cycle. Recommend the product team keep an eye on this reviewer-tooling gap for future CoWork UAT cycles — it is not something this session could resolve from within the sandbox.
