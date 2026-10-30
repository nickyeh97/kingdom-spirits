# Worklog — 2026-10-29 — 007 Lion Adult/Leader rigs; nose-stretch fix

- Asset / project: kingdom-spirits — Lion Baby v007, Adult v008, Leader v002 (six clips each)
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / correction / verification
- Status: production complete; owner check in Unity pending.
- Related: worklogs 2026-10-29_005, _006; `art/RIGGING.zh-TW.md` §5d–5e.

## Owner request and feedback (2026-10-29, faithful English summary)

"Continue with the Lion Adult and Leader. In the beast home: play with the ball after 6 s idle, sleep after 15 s. When eating, seen from the side, the lion's brown nose gets stretched — it should not."

## Cause of the nose stretch

The nose vertices were outside the head region and got distance-based weights: 50 % `mouth` bone (plus some eye bones). Scaling the mouth bone in Eat stretched the nose. `verify_rig.py` had no check for this.

## Actions

- Weights: part bones (eye, lid, mouth, toy) excluded from distance weighting; head region moved forward to cover the muzzle; new rule: whole components whose centroid lies in the head region follow the head (Adult/Leader mane, Leader crown); ear override moved after it.
- New check in `verify_rig.py`: part bones own only rigid (0/1) weights, mouth bone none. It flags Lion_Baby_v006 (mouth: 432 vertices, eyes: ~527 each) and passes the new builds.
- Adult/Leader joints measured from the finalized meshes (leg columns, back/belly heights, Mouth origin); motion scale `k` = 1.6; toy roll 0.45 m.
- Props reduced (ball 10×5, band 8 sides, eye arcs square section) — the first Adult/Leader build was 8,336 / 8,298 triangles (budget 8,000).
- Game: idle Play after 6 s, Sleep after 15 s.

## Verification

| Check | Result | Evidence |
| --- | --- | --- |
| `verify_blend.py` Baby v007 / Adult v008 / Leader v002 | PASS | 19 PASS each; 6,848 / 7,984 / 7,946 triangles |
| `verify_rig.py` (incl. new part-bone check) | PASS | 32 PASS each |
| Nose weights after fix | PASS | nose vertices: head 100 % |
| Renders: Adult/Leader idle, wave, eat (incl. side view), sleep, play | PASS | mane follows head; crown stays; necklace stays on the chest; nose unchanged from the side |
| Unity playback | NOT RUN | owner to check |

## User feedback

- Pending; this does not mean accepted.
