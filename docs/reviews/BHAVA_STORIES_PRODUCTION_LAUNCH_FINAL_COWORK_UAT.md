# BHĀVA STORIES PRODUCTION LAUNCH — FINAL COWORK UAT

Independent UAT for the completed production-launch baseline (copyright + single runtime).

## Authority

- Branch: `feature/bhava-portal-v1` only
- Do not create a PR or merge
- Do not modify `main` / tags
- CoWork may commit **only** reports, evidence, and screenshots

## Confirm before testing

```powershell
git switch feature/bhava-portal-v1
git fetch origin
git status -sb
git rev-parse HEAD
git rev-parse origin/feature/bhava-portal-v1
```

Require local HEAD == origin. Record the product SHA under test.

## Runtime

Exactly one instance:

- Name: `bhava-final`
- Web: `http://127.0.0.1:3000` (open this only)
- API: `http://127.0.0.1:8000` (via Next proxy)

Confirm old Bhāva ports/tunnels are stopped and `.bhava/instances/bhava-final/runtime.json` matches.

## Checklist

### Git / SHA

- [ ] Product SHA matches the launch evidence metadata
- [ ] Working tree clean aside from CoWork evidence commits
- [ ] No PR / merge / main / tag changes

### Copyright identity

- [ ] Owner spelling **Svarna** Gauranga Das (never Swarna)
- [ ] Publisher imprint: Dauji Publication
- [ ] Project: Bhāva
- [ ] Email: svarnagaurangdas@gmail.com
- [ ] No phone number
- [ ] Central config: `config/publication_identity.yaml`

### Website

- [ ] Footer shows © 2026 Svarna Gauranga Das + Dauji Publication line
- [ ] `/rights` page live with limitations + registration disclaimer
- [ ] Footer link **Copyright & Permissions**
- [ ] Per-story Source tab rights pointer
- [ ] Sitemap includes Stories 001–009 and `/rights`
- [ ] Sitemap excludes Story 010 and Studio/dev mutation routes

### Stories 001–009

- [ ] Public packages version `2.1.0-copyright`
- [ ] Exact eight files each
- [ ] `manifest.json` contains `rights` sidecar
- [ ] Pre-copyright archives under `output/_archive/pre-copyright/<n>/2.0/`
- [ ] story.md Rights and Credits section
- [ ] Caption © line; PNG credit strip; PDF rights page; MP3 ID3 only
- [ ] No first-publication year inventing; status publicly_available_unreviewed
- [ ] Sound-recording claim needs_manual_review (no unsupported ℗)
- [ ] Drive not mutated; manual update noted

### Safety

- [ ] No Story 010 output
- [ ] Queue unchanged
- [ ] Scheduler not triggered
- [ ] Providers not called
- [ ] Sensitive files uncommitted

### Accessibility / security / screenshots

- [ ] Production npm audit zero
- [ ] Zero critical/serious axe findings (documented WebKit-mobile skips only)
- [ ] Screenshot archive includes home footer, rights page, Story 001/009 rights-facing views

### MyPilotDropbox

- [ ] Private key preserved
- [ ] Duplicates cleaned only after archival copy verified
- [ ] Nothing from MyPilotDropbox committed

## Verdict

Return one of:

```text
READY FOR PRODUCTION / PASS WITH NON-BLOCKING NOTES / BLOCKED
```

with SHA, runtime URL, and evidence paths.
