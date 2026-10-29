# Worklog — 2026-10-29 — 002 Pattern stage switch and Dove feather scallops

- Time / timezone: 2026-10-29, Asia/Taipei
- Asset / project: kingdom-spirits — shader `SpiritBeast/PaletteMask`, `BeastForms`, Dove Baby/Adult/Leader
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / verification
- Status: production complete; owner check in Unity pending.
- Related: Dove brief Q4 (option a, scalloped feathers, confirmed 2026-10-21); worklogs 2026-10-21_001, 2026-10-29_001.

## Context / user request

Faithful English summary (2026-10-29): "Switch to UGUI first, and finish the remaining four of the five items." This item: the pattern stage switch (the baby mesh is shared by stages 1–2, and GDD §7.2 says patterns appear from stage 2) and the Dove's scalloped feather pattern.

## Scope / actions and implementation

- Shader: `_PatternStrength` (0 = no pattern, 1 = full), `lerp(1, pattern, strength)`.
- Core: `BeastForms.PatternStrength(variant, stage)` — from stage 2; Lion from stage 1 (owner decision 2026-10-12, natural coat on the baby). Six new tests (98 total). `BeastView` sets it per stage.
- `finalize_export.py`: new pattern kind `scallop` (Voronoi distance-to-edge with a wide soft rim, randomness 0.6) and `region_y` (pattern only on the back half: back, wings, tail; face and chest stay clean). Lion's noise path unchanged.
- Dove scripts: scallop settings (scale (8, 5, 8), low 0.7, rim 0.22). Rebuilt Baby v003, Adult v002, Leader v003; geometry unchanged.
- Three internal iterations before delivery (not delivered): (1) cells far too fine — Voronoi's own default scale ×5 multiplied the requested scale; (2) narrow rims looked like a cracked net; (3) distance-to-centre (and Smooth F1, which compresses distances) gave blotches too faint to read.

## Verification / tests and observations

| Check | Method | Result | Evidence |
| --- | --- | --- | --- |
| Core tests | `dotnet test Tools/CoreTests` | PASS | 98/98 |
| Runtime compile | `dotnet build Tools/RuntimeCompileCheck` | PASS | 0 errors |
| Fresh-reopen verification | `verify_blend.py` on Baby v003 / Adult v002 / Leader v003 | PASS | 20 PASS each, pattern packed 512² |
| FBX colour mask | `Tools/fbx_mask_report.py` | PASS | same slot counts as before |
| Preview renders | `Tools/render_preview.py` | PASS | soft rounded feather tiles on wings and back, subtle; face and chest clean |
| Stage switch in game | Unity demo, Dove stage 1 → 2 | NOT RUN | owner to check: no pattern at stage 1, pattern from stage 2 |

## User feedback

- Pending; this does not mean accepted.
