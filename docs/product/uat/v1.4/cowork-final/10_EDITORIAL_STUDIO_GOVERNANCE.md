# V1.4 Editorial Studio Governance

## Positive finding: Studio is now a functioning, authenticated, role-aware console (not a static disclosure page as accepted in V1.3)

`/studio/knowledge`:
- Absent from public nav (confirmed: header nav = Home/Library/For Teachers/Prabhupāda Vāṇī/Knowledge/About/Contact only).
- `robots.txt` disallows `/studio`.
- Before sign-in, the route renders **only** a bootstrap sign-in form (role selector + token field) — no roadmap data, no record table, nothing else — confirming the data view is genuinely gated, not just visually hidden by client JS while data is already in the page.
- Role selector lists exactly the 9 roles the mission specifies: `steward, administrator, contributor, content_editor, scriptural_reviewer, devotional_reviewer, copy_editor, moderator, auditor`.
- Documented auth: "Local secure bootstrap. Default token is the value of `BHAVA_STUDIO_BOOTSTRAP_TOKEN` (or `bhava-local-studio` when unset). Never use external auth providers for V1.4." — a loopback-only, non-production credential model appropriate for a local review instance.

## Live sign-in test

Signed in as role `steward` using the documented default token. On success:
- Header changed to "Signed in as steward. Sign out" — confirms a real session state change, not a no-op.
- Full workflow displayed: **Draft → Source Review → Devotional Review → Copy Review → Approved → Scheduled → Published → Updated → Archived** — matches the mission's specified workflow exactly, and matches `docs/reviews/BHAVA_V1_4_EDITORIAL_GOVERNANCE_REVIEW.md`'s claim.
- Roadmap dashboard populated live: total 348, lifecycle breakdown `source_research: 348`, working lifecycle/pillar filters ("Showing 348 of 348"), and a real record table (see `08_KNOWLEDGE_348_RECORD_AUDIT.md` for the full cross-check).

## What this confirms vs. what remains untested

Confirmed live: authentication gate works, role selection is presented and accepted, the roadmap view is populated from the live API (not static HTML), filtering works.

**Not tested this session** (mission explicitly warns not to fail solely for this, since V1.4 is documented as deferring rich per-type editing):
- Whether role selection actually **enforces** different permissions per role (e.g., whether a `contributor` session is blocked from actions a `steward` session can take) — only the `steward` role was tested. No attempt was made to mutate a record, advance a lifecycle stage, or test the "governance evaluate API" mentioned in the mission, since the mission's "review and evidence only — do not modify application code, do not modify the real queue" instructions were read broadly to also mean not exercising real content-mutation endpoints against the shared `cursor-v14` instance's live catalog database.
- Revision audit trail, preview, and unsafe-publication-blocked behavior were not exercised.
- Whether the httpOnly-cookie session claim (`docs/reviews/BHAVA_V1_4_CODEX_TECHNICAL_REVIEW.md`: "Studio uses httpOnly bootstrap cookies") is accurate was not directly inspected (httpOnly cookies are by design invisible to page JS, which is consistent with what was observed — no session token was visible in `document.cookie` — but this is not conclusive proof of the httpOnly flag specifically without a network-header inspection, which was not performed).

## Conclusion

This is a genuine, verified improvement over V1.3 (real auth + real live data, not a static stub), and the specific claims checked (workflow stages, role list, 348-record dashboard) all hold up under live testing. The deeper claims about per-role mutation enforcement and audit trails are unverified, not contradicted — reported honestly as untested rather than assumed passing.
