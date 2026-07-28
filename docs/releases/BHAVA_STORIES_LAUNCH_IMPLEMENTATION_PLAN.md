# Bhāva Stories Production Launch — Implementation Plan

## Authority

- Contract: `MyPilotDropbox/bhava-stories-production-launch/BHAVA_STORIES_PRODUCTION_LAUNCH_ONE_PASS.md`
- Branch: `feature/bhava-portal-v1`
- Starting tip: `87930f87b34deb9887afc994458f6981e0effd4e`
- Release name: **BHĀVA STORIES PRODUCTION LAUNCH** (no micro-release number)

## Safety locks

- Stories 001–009 byte-locked (72 SHA-256 hashes in `docs/releases/BHAVA_STORIES_LAUNCH_SAFETY_BASELINE.json`)
- Story 010 remains pending / absent from `output/`
- No paid providers, Drive mutation, scheduler trigger, or queue mutation
- No PR / merge / main / tags

## Work streams

1. Close CoWork defects (contrast, Preachers ARIA, timeline copy, dynamic 009 next preview, catalog-driven audio + 009)
2. Controlled Next.js 15.5.22 + React 19.1.9 security upgrade; production npm audit gate
3. Story-first homepage / library / printables UX; unpublished Story 010 `noindex`
4. Full route/control matrix + visual audit docs; fix P0/P1/P2 launch issues found
5. Playwright PNG screenshot project + expanded axe suite + Lighthouse samples
6. Deployment-readiness docs for bhava.me (do not deploy)
7. Knowledge taxonomy / rights research docs (do not block launch)
8. SHA-bound full matrix + final CoWork UAT prompt + commit/push

## Non-goals this pass

- Generate Story 010+
- Populate full Knowledge / Teachers / Sunday School / Preachers / Vāṇī libraries
- Deploy bhava.me
