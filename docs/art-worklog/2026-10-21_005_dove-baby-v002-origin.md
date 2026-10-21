# Worklog — 2026-10-21 — 005 Dove Baby v002 (origin fix)

- Time / timezone: 2026-10-21, Asia/Taipei
- Asset / project: kingdom-spirits — Dove Baby (stages 1–2 mesh); finalize/verify scripts
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: correction / verification
- Status: correction complete; owner check in Unity pending.
- Related: worklog 2026-10-21_001 (Dove Baby v001).

## Context / user request

Faithful English summary of the owner's report (2026-10-21, two Unity screenshots of the offline demo in Blender-preview mode): "Colours and rendering are OK, but in the Main scene the dove has dropped down and is not in the centre of the view — is a Y value set wrong?" The screenshot shows Dove at stage 2 with only the head visible above the palette swatches; Lamb at the same stage is placed correctly.

## Cause

Not a Unity Y value. `finalize_export.py` joins all parts into the part with the most triangles and keeps that part's origin. For Lamb, Lion and Dove Adult/Leader that part is a metaball object created at the world origin, so the origin happened to be at the feet. For Dove Baby the largest part is the `Head` sphere, so the joined mesh's origin was the head centre (0, −0.30, 0.72). Unity places the model's origin on the ground, so the body sank 0.72 m. `verify_blend.py` did not check the origin, so v001 passed.

## Scope / actions and implementation

- `finalize_export.py`: after joining, set the origin to the world origin (cursor at (0, 0, 0), `origin_set(ORIGIN_CURSOR)`) before parenting the mouth.
- `verify_blend.py`: new check — root mesh object at (0, 0, 0) and lowest point within 2 cm of Z = 0.
- Rebuilt Dove Baby with the unchanged shape script → `Dove_Baby_v002.blend`; FBX re-exported and copied to `Assets/Art/Resources/Beasts/Dove_Baby.fbx`. Geometry unchanged.

## Verification / tests and observations

| Check | Method | Result | Evidence |
| --- | --- | --- | --- |
| New check catches the bug | `verify_blend.py` on Dove_Baby_v001 | FAIL (expected) | location (0, −0.3, 0.72) |
| Dove Baby v002 | `verify_blend.py` | PASS | 19 PASS, 0 FAIL; location (0, 0, 0), lowest Z 0.002 |
| Other delivered models | `verify_blend.py` on Lamb Baby v001, Lion Baby v004, Dove Adult v001, Dove Leader v001; origin script on all nine | PASS | all at (0, 0, 0), lowest Z within ±0.006 |
| Unity demo placement | Unity 6000.3.25f1 | NOT RUN | owner to check |

## User feedback

- 2026-10-21: owner confirmed colours and rendering of the Blender-preview mode are OK (worklog 004).
- Placement fix: pending.
