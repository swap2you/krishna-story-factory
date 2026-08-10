# Phase Charter — P01 (Visual Learning Page Pilot)

## Identity

- Phase ID/name/version: **P01 / Governed Visual Learning Page Pilot / discovery run P01A-2026-08-06**
- Owner: Bhāva program owner (human)
- Lead orchestrator: Cursor
- Repository/base branch/base SHA: `swap2you/krishna-story-factory` / `develop` / `d6159e9af6b7033d1876141eae31944ec93fffc0`
- Feature branch (after approval): `feature/kf-p01-visual-learning-pilot` — **not created**
- Start/target review date: Discovery complete 2026-08-06; owner review pending

## Outcome

Prove a governed content→page→PDF/DOCX system with one golden prayer page and four confirmation pages in **private preview**, without changing staging, production, scheduler, or Story Factory.

## In scope

- P01A discovery/baseline/reuse/source availability (this run)  
- Later, if authorized: P01B specification; P01C implementation/validation; P01.R1 remediation  

## Explicitly excluded

- Branch/merge/deploy/publish/scheduler/paid APIs without owner gates  
- Framework migration; audio/podcast/3D  
- Fabricating Sanskrit/translation/approvals  
- Public exposure of 348 roadmap records  
- Mutating RELEASE_CONTENT / public story max  
- Etiquette/Deity Worship vertical until missing PDFs restored  

## Inputs and locked dependencies

- Package `BHAVA_KNOWLEDGE_PLATFORM_PHASE0_COMPLETE_V2` SHA-256 `3955E964FEE420436842E7C93C22D33BDEEA808B31A961057CCCEF24346C56DC`
- Repo governance: `AGENTS.md`, CI, release pin `bhava-content-001-022-v1`
- Protected assets: see `PROTECTED_ASSETS.md`
- Cost/provider limits: paid calls **off**

## Work packets

- **P01A discovery:** complete → owner review  
- **P01B specification:** not started  
- **P01C implementation/validation:** not authorized  
- **P01.R1 consolidated remediation:** n/a  

## Requirements and evidence

- Requirements path: deferred to P01B (`REQUIREMENTS.md`)  
- Traceability path: deferred to P01B  
- Test/evidence paths: this run folder + later validation reports  
- Definition of done: package `07_EVIDENCE_VALIDATION_AND_HANDOFF.md`  

## Allowed paths / path owners (P01A)

| Path/pattern | Owner | Allowed change |
|---|---|---|
| `docs/execution-packets/.../runs/P01A-2026-08-06/**` | Orchestrator | create discovery evidence only |
| Application / content / configs | — | **none** this packet |

## Risks and stop conditions

See `RISK_REGISTER.md`. Hard stop for build: missing authorized source text/rights (R01).

## Required owner decisions

- **Specification (P01B):** accept discovery; authorize specification work  
- **Build:** after P01B acceptance  
- **Merge / staging / production:** default **NO** for Phase 1  
