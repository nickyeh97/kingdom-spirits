# Worklog — 2026-10-29 — 004 Dove feather arcs (v004/v003/v004) and the instrument icon

- Asset / project: kingdom-spirits — Dove Baby/Adult/Leader pattern; `Service/instrument.png`
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: correction / verification
- Status: production complete; owner acceptance pending.
- Related: worklog 2026-10-29_002 (first scallop pattern).

## Owner feedback (2026-10-29, faithful English summary)

1. "PC can no longer click" (handled in code, see commit; not an art item).
2. "The heart icon looks neither like a drum nor an offering box — what is it?" (it was the tambourine for 小樂器).
3. "Can the Dove's wing feather pattern be made cuter? Patterns that are too large look worse than no pattern."
4. "Rig questions later; list them separately at the end."

## Actions

- Icon: 小樂器 redrawn as a pair of maracas side by side (two internal iterations: crossed/overlapping was cluttered; the first side-by-side version was clipped at the frame).
- Pattern: replaced the Voronoi bake with `bake_feather_scales` in `finalize_export.py` — a Python rasterizer that draws rows of small overlapping feather arcs (front rows cover back rows, so visible arcs point toward the tail), sized in metres from each texel's 3D position (no UV stretching), **only on secondary-slot triangles (wings and tail feathers)**; body, face and chest stay clean. Removed the unused `scallop` / `region_y` code. Lion's noise path unchanged (rebuilt Lion Baby pattern in scratch: identical statistics).
- Settings: Baby spacing 6 cm, Adult/Leader 7.2 cm, rim 14 %, darkest 0.78. One internal iteration: 3.6/4.4 cm read like fish scales.
- Rebuilt Dove Baby v004, Adult v003, Leader v004; geometry unchanged.

## Verification

| Check | Result | Evidence |
| --- | --- | --- |
| `verify_blend.py` on the three Dove files | PASS | 20 PASS each |
| Lion Baby pattern unchanged | PASS | p50 0.961 / p95 0.988 in both |
| Preview renders | PASS | small even arcs on wings and tail only |
| Unity, stage 1 → 2 | NOT RUN | owner to check |

## User feedback

- Pending; this does not mean accepted.
