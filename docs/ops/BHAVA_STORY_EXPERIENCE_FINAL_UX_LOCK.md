# Bhāva story experience — final UX lock

Code-only UI stabilization for public Stories 001–020.

## Scope

- Story-page poster wallpaper (subtle, story pages only)
- Accessible coloring/poster image viewer (scroll lock, sticky Close, portal)
- True floating audio mini-player (`createPortal` + `position: fixed`)
- Regression coverage for tabs, wallpaper, viewer, mini-player
- Production `npm audit --omit=dev` remains zero

## Non-changes

- Content release remains `bhava-content-001-020-v3`
- No Story 021 generation
- Scheduler remains Disabled
- No narration / story text / asset regeneration
- Production (`main`) untouched

## Opacity guidance (wallpaper img)

| Viewport | Approx. image opacity |
|---|---|
| Desktop | 0.18 |
| Tablet (≤1024) | 0.16 |
| Mobile (≤640) | 0.12 |

Parchment `::after` overlay preserves text contrast.

## Validation commands

```powershell
cd apps\web
npm run lint
npm run typecheck
npm test -- --run
npm run build
npm audit --omit=dev
npx playwright test e2e/story-experience-ux-lock.spec.ts e2e/pdf-and-images.spec.ts --project=chromium-desktop

# From repo root with .venv
.\.venv\Scripts\python.exe -m pytest tests/portal -q
```

## Security

- `npm audit --omit=dev`: 0 vulnerabilities (recorded at UX-lock implementation)
- No new production dependencies added for this change
