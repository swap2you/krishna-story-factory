# Requirements Traceability — Vāṇī Krishna Book Dictation Archive

| ID | Requirement | Implementation | Verification |
|---|---|---|---|
| R1 | Separate collection not limited by Stories 001–035 | Catalog slots 00–90 independent of story ceiling | Catalog count 91; gaps honest |
| R2 | Union of lawful accessible recordings | Source inventory + IDT acquisition | `inventory/source_inventory.json` |
| R3 | No invented audio/transcripts/voice clone | Acquisition + conservative restore only | QA ledger; no generative tools |
| R4 | Do not mutate child stories | No story package writes | Git diff excludes `output/` stories |
| R5 | Calm listening UX | Landing/catalog/detail/mini-player | Screenshots + UAT notes |
| R6 | Design before code | This design + RTM | Docs present in handoff |
| R7 | Direct permitted access only | No Cloudflare bypass; IDT direct MP3 | Access results in inventory |
| R8 | Best source track-by-track + alternates | IDT selected; Krishna.org alternate noted | Manifest `source.alternates` |
| R9 | Immutable originals + checksums | `original/` + sha256 in manifests | Hash ledger |
| R10 | Conservative restore + fallback | `scripts/vani/acquire_restore_manifest.py` | Per-track QA |
| R11 | Routes landing/catalog/detail | `apps/web/app/prabhupada-vani/**` | Route matrix |
| R12 | Player: seek/resume/speed/sleep/Media Session | `components/vani/*` + audio-url allowlist | Frontend tests + UAT |
| R13 | API + range + traversal protection | `bhava_api/vani/*` | `tests/test_vani_archive.py` |
| R14 | Rights server-enforced | `publish_gates.py` | Unit tests for public/private |
| R15 | Separate content bundle | Bundle builder script | Bundle SHA sidecar |
| R16 | Stage 1 even if public rights unresolved | Staging deploy with private review rights | Stage smoke |
| R17 | Public prod only with affirmative rights | Default unresolved | Verdict gate |
| R18 | One handoff ZIP | Final builder | ZIP + SHA-256 |
