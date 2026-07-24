# V1.4 Accessibility and Responsive (limited coverage — tool limitation repeats a 4th time)

## Responsive

`resize_window({width:390,height:844})` was called against the live tab. The tool reported success, but `window.innerWidth`/`innerHeight` measured immediately after remained at the real, maximized window's actual size (2400×1138), not 390×844. **This is the fourth consecutive UAT round (V1.1, V1.2, V1.3, and now V1.4) in which this exact tool limitation is confirmed**: `resize_window` cannot genuinely change a real, maximized Windows Chrome window's viewport in this environment. No 390×844, 430×932, 768×1024, 1024×768, 1366×768, 1440×900, or 1920×1080 screenshot in this evidence set represents a genuinely resized viewport. No fabricated per-viewport pass is claimed.

The committed `docs/product/uat/live/traces/` evidence (see `15_AUTOMATED_MATRIX_AUDIT.md`) independently shows the automated Playwright suite's own responsive-overflow tests **failing** at several of these exact viewport widths (768/1024/1366/1440/1920) across multiple browser projects — which is real evidence, genuinely captured by Playwright's own browser automation (not subject to this session's manual-tool limitation), and points toward real overflow/layout issues at those widths that this session could not independently visually confirm or refute.

## Accessibility

Not run this session: a formal automated accessibility scan (e.g. axe), a keyboard-only navigation pass, a 200% zoom check, or a color-contrast measurement. `docs/product/uat/live/` contains an `axe-results.json` file from the earlier committed automated run; it was not opened this session (mission requires running fresh scans in addition to reviewing existing evidence — fresh scans were not performed).

No console accessibility warnings were observed on the pages visited this session, but this is not a substitute for a real scan.

## Conclusion

Per the mission's own standard ("Do not claim full WCAG conformance from automated scans alone" and, symmetrically, do not claim a viewport was tested when it wasn't), this session cannot claim the responsive or accessibility requirements are met. The one piece of independently-reliable evidence available (Playwright's own committed responsive-overflow failures) points toward unresolved issues, not a clean pass.
