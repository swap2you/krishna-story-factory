# 3D / Motion Lab — offline research contract (Unified Platform M5)

**Status:** research readiness only.  
**Public site impact:** none. No public nav item, no runtime 3D dependency on the live site, no autoplay mascot, no cursor-follow effect, no permanent character.

## Purpose

Establish a governed experimental lane for future 3D/motion learning aids without destabilizing Bhāva's public platform.

## Hard exclusions (live site)

- No public navigation entry for a 3D lab or mascot.
- No runtime 3D libraries (Three.js, Babylon, WebGL app shells, etc.) added to `apps/web` production bundles for this milestone.
- No autoplay 3D, cursor-follow characters, or permanent floating mascot.
- Motion on the public site remains CSS/UI only and must honor `prefers-reduced-motion` (see `apps/web/app/globals.css`).

## Contract gates (every experiment)

An experiment may be considered decision-ready only when all of the following are recorded:

1. **Source / asset rights** — provenance, license, attribution, and whether characters/iconography may be shown publicly.
2. **Reproducibility** — pinned tool versions, seed/parameters, input asset hashes, and rebuild steps.
3. **Hardware / time / cost reporting** — machine class, wall-clock, and estimated cost for the run.
4. **Iconographic / character review** — stewardship sign-off that depictions are appropriate and non-misleading.
5. **Artifact manifest** — inventory of outputs with checksums and retention path (see below).

## Artifact path (gitignored)

Operator artifacts are written outside tracked content:

```text
work/3d-motion-lab/artifacts/
```

The repository root `/work/` tree is gitignored. Do not commit binaries, caches, or generated meshes.

Tracked pointer (this file + `ARTIFACTS.md`) documents the path; local directories may be created by operators as needed:

```text
work/3d-motion-lab/
  artifacts/
    <experiment-id>/
      manifest.json
      ...
```

### Minimal artifact `manifest.json` shape

```json
{
  "experiment_id": "example",
  "created_at": "ISO-8601",
  "rights": { "status": "unknown", "notes": "" },
  "reproducibility": { "tools": [], "params": {}, "input_hashes": [] },
  "hardware_time_cost": { "machine": "", "wall_clock_sec": 0, "cost_usd_estimate": 0 },
  "iconographic_review": { "status": "not_started", "reviewer": null },
  "outputs": []
}
```

## Decision posture

M5 delivers a **decision-ready research lane**, not a public 3D product. Promotion into any public surface requires a separate owner gate beyond this contract.
