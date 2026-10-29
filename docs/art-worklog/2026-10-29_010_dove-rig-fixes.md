# Worklog — 2026-10-29 — 010 Dove rig fixes (v006 / v005 / v006)

- Asset / project: kingdom-spirits — Dove Baby v006, Adult v005, Leader v006
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: correction / verification
- Status: correction complete; owner check in Unity pending.
- Related: worklog 2026-10-29_009.

## Owner feedback (2026-10-29, faithful English summary)

"The Lamb is basically fine. The Dove: when waving, the wing and the feathers separate; when jumping and sleeping the belly deforms into a point; kicking the ball with the beak means crouching very low — pick either the foot or the beak. Fix the Dove first."

## Causes and fixes

| Problem | Cause | Fix |
| --- | --- | --- |
| Wing and primaries separate in Wave | wing body on `wing`, primaries on `wingtip`; the tip waved alone | one bone per wing; all wing parts on it; wave swings the whole wing |
| Belly pointy in Happy / Sleep | belly vertices near the hidden thigh bones got leg weights | bird leg bones influence only leg/toe components (entirely below hip height); body never takes leg weights |
| Play needs a deep crouch | beak peck | right foot kicks forward; ball placed in front of the right foot; wings open slightly for balance |

## Verification

| Check | Result |
| --- | --- |
| `verify_blend.py` / `verify_rig.py` on the three Doves | PASS (19 / 32 each) |
| Side renders Adult: idle, happy, sleep, wave | belly stays round; wing moves as one piece |
| Front renders Baby, Leader: happy, wave, sleep, kick, ball rolled | PASS |
| Unity | NOT RUN |

## User feedback

- Lamb: "basically fine" (2026-10-29). Dove fixes: pending.
