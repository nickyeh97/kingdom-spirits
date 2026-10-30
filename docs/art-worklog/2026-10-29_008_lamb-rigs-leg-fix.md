# Worklog — 2026-10-29 — 008 Lamb rigs; detached paws fix

- Asset / project: kingdom-spirits — Lamb Baby/Adult/Leader v002 (six clips each); Lion Baby v009, Adult v010, Leader v004 rebuilt
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / correction / verification
- Status: production complete; owner check in Unity pending.

## Owner feedback (2026-10-29, faithful English summary)

"Pulled; very well done. The only flaw: on the Adult and Leader the paws separate from the legs, but that's fine for now — continue with the Lamb and the Dove."

## Cause of the detached paws

The "rigid small part" rule used vertex count (< 250). Whole leg tubes have few vertices, so each leg moved as one rigid block and never bent at the knee, while the paw followed the IK paw bone. IK itself was fine (elbow up to 77° in Wave). Now only parts physically smaller than 8 cm are rigid. Close-up renders (Sleep, Wave, Play) confirm the legs bend and paws stay attached.

## Lamb specifics

- Gentle style: amplitude × 0.55, timing × 1.3. No tail (tail bones omitted, tail keys skipped).
- Ears: assigned by whole component near the ear (a sphere test grabbed hood wool); horns via `head_parts`.
- Triangle budget: Adult/Leader exceeded 8,000 after adding props → the largest piece (wool) is separated, decimated ~3 %, and joined back. A first attempt (Decimate with a vertex group on the whole object) also collapsed the small ball to a dot; caught in renders.
- Wave paw lifts vertically before reaching (Lamb Baby slid 1.49 cm before).

## Verification

| Check | Result |
| --- | --- |
| `verify_blend.py` on all six | PASS (Lamb 18, Lion 19 each; Lamb Adult/Leader 7,974 triangles) |
| `verify_rig.py` on all six | PASS (32 each) |
| Renders: Lamb ×3 (idle, wave, eat, sleep, play), Adult legs close-up | PASS |
| Unity playback, build size | NOT RUN (FBX total 12 MB before Unity's animation compression) |

## User feedback

- Pending; this does not mean accepted.
