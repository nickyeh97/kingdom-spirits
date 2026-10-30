# Worklog — 2026-10-29 — 006 Lion Baby v006: Wave, Eat, Sleep, Play

- Asset / project: kingdom-spirits — Lion Baby rig, clips 3–6
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / verification
- Status: production complete; owner check in Unity pending.
- Related: worklog 2026-10-29_005 (v005: Idle, Happy); `art/RIGGING.zh-TW.md` §5b–5d.

## Owner decisions (2026-10-29, faithful English summary)

Sleep eyes: "(a) first, then (c)" — closed-eye arcs now, blinking later. Toy: a small ball.

## Actions

- `rig_quadruped.py`: closed-eye arcs and a red ball with a yellow band joined into the mesh, collapsed to 1 % on `lid.L/R` and `toy` bones; `eye.L/R` bones for the open eyes; `mouth` bone carries the Mouth object; new clips Wave (1.5 s), Eat (1.5 s), Sleep (4 s loop), Play (2 s); IK limits widened (front ±90°, hind ±75°); `wloc` world-space offsets for control bones; every clip keys every bone at rest on frame 0.
- `verify_rig.py`: the ball bone is excluded from the rotation limit (it rolls).
- Internal iterations before delivery (none delivered): (1) the bat paw dipped into the ground and slid 3.06 cm — control-bone local axes are tilted; fixed with `wloc`; (2) 1.56 cm slide at lift-off — paw now lifts vertically before reaching; (3) Sleep's closed eyes leaked into Play — unkeyed bones kept the previous pose; fixed by keying all bones per clip; (4) the ball sat under the head and rode up with the pounce — moved closer, rolls 30 cm, bone no longer under `root`; (5) the wave was hard to see — paw raised higher.

## Verification

| Check | Method | Result | Evidence |
| --- | --- | --- | --- |
| Model checks | `verify_blend.py` on Lion_Baby_v006 | PASS | 19 PASS |
| Rig checks (6 clips) | `verify_rig.py` on Lion_Baby_v006 | PASS | 31 PASS |
| FBX contents | re-import | PASS | 28 bones; takes Eat, Happy, Idle, Play, Sleep, Wave; 1.8 MB |
| Key poses | Cycles renders (wave, eat, sleep with closed eyes, play: ball out, bat, pounce with ball on the ground) | PASS | — |
| Unity playback | Unity 6000.3.25f1 | NOT RUN | owner to check via the demo action buttons |

## User feedback

- Pending; this does not mean accepted.
