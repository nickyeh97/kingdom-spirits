# Worklog — 2026-10-29 — 009 Dove bird rigs (six clips)

- Asset / project: kingdom-spirits — Dove Baby v005, Adult v004, Leader v005
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / verification
- Status: production complete; owner check in Unity pending.
- Related: Dove brief Q1 (own bird skeleton); rig brief owner answers (gentle style for the Dove).

## Actions

- `rig_quadruped.py` bird branch (`kind: "bird"`): two IK legs, no front legs or ears; wing bones (shoulder → mid → tip) on the spine; one tail-fan bone. Wing and tail-feather parts are assigned whole by region (`wing_box`, `tail_box`) and excluded from distance weighting.
- Same six clips with bird variants: Happy spreads the wings, Wave raises the right wing and waves the tip, Play pecks the ball with the beak instead of a paw. Gentle style (× 0.55 amplitude, × 1.3 timing).
- `verify_rig.py`: for birds, the size check ignores wing/tail parts (open wings legitimately widen the outline; first run flagged 89 %); wing rotation limit 70°.
- Leader exceeded the budget by 80 triangles after props → largest piece trimmed 1.4 %.

## Verification

| Check | Result |
| --- | --- |
| `verify_blend.py` on the three Doves | PASS (19 each; Leader 7,974 triangles) |
| `verify_rig.py` on the three Doves | PASS (32 each) |
| Quadrupeds after the verify change | PASS (Lamb Adult re-checked: 32) |
| Renders: Baby/Adult idle, happy, wave, eat, sleep, play | PASS — wings open, eyes closed in sleep, pecks the ball |
| FBX | 22 bones, six takes |
| Unity playback, build size (FBX total 16 MB) | NOT RUN |

## User feedback

- Pending; this does not mean accepted.
