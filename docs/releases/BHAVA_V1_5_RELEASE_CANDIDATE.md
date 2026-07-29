# Bhāva Portal V1.5 — Release Candidate

**Branch:** `feature/bhava-portal-v1`  
**Tested SHA:** `fe57b4661712845b12bf313ea46321d71723c1bb`  
**Evidence:** `docs/product/uat/v1.5/runs/20260724-181701-fe57b46/`  
**PR:** none (not created)  
**Main/master/tags:** unchanged

## Completed

1. Scheduler forensics + repair (Start-Process, staging, atomic publish, lock reclaim)
2. Story 008 recovery (reuse story+audio; exact-eight; Drive verify; queue done)
3. Catalog gates + 007→008 navigation
4. Audio DEF-06: blob-first + native MP3 fallback for WebKit
5. Design/nav/home: Tillana brand display; Learning menu; platform positioning
6. Knowledge readability + migration candidates; trust/FAQ/contact polish
7. Full Playwright + pytest green; SHA-bound evidence committed with this release handoff

## Safety

- Stories 001–007 hashes match `BHAVA_V1_5_SAFETY_BASELINE.json`
- Story 008 only exposed after exact-eight + publishable
- No PR/merge; feature branch only

## Non-blocking known items

- Curated content for Teachers / Sunday School / Preachers / Prabhupāda Vāṇī remains planned/coming soon
- Lighthouse not in CI; axe critical/serious covered via Playwright

## Verdict

**READY FOR FINAL COWORK UAT**

## Errata

- Corrected full tested SHA to `fe57b4661712845b12bf313ea46321d71723c1bb` (short `fe57b46`). An earlier draft incorrectly concatenated digits from an adjacent commit hash.

