# Worklog — 2026-10-29 — 001 Dove Leader v002 (chest pendant)

- Time / timezone: 2026-10-29, Asia/Taipei
- Asset / project: kingdom-spirits — Dove Leader (stage 4 mesh)
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production / verification
- Status: production complete; owner acceptance pending.
- Related: worklog 2026-10-21_003 (Leader v001, "plainer than the other leaders" observation).

## Context / user request

Faithful English summary (2026-10-29): "Recording mode works. Add an accessory on the Dove Leader's chest."

## Decisions / concise rationale

- Gold necklace + round gold pendant, the same family as the Lion Leader's necklace, but the pendant face carries a small olive branch (gold stem, four fixed olive-green leaves) instead of a ruby. It echoes the olive wreath (peace, Genesis 8:11) and tells the two leaders apart. Assistant decision; owner may adjust.
- The torso is a metaball, which cannot be ray-cast directly, so a BVH tree is built from its evaluated mesh; the chain ring (high behind the neck, low on the chest) is projected onto it as on the Lion Leader.
- Budget: torso metaball target lowered from 1,600 to 1,400 triangles.

## Files / versions

| File | Action | Version/purpose |
| --- | --- | --- |
| art/blender/dove_leader.py | changed | v002: section 4, chest pendant |
| art/models/Dove/Dove_Leader_v002.blend | new | verified source |
| art/models/Dove/Dove_Leader.fbx, Dove_Leader_UE.fbx | replaced | Unity / Unreal presets |
| Assets/Art/Resources/Beasts/Dove_Leader.fbx | replaced | game model (stage 4) |

## Verification / tests and observations

| Check | Method | Result | Evidence |
| --- | --- | --- | --- |
| Fresh-reopen verification | `verify_blend.py`, Blender 4.2.23 LTS | PASS | 19 PASS, 0 FAIL; 7,868 evaluated triangles; origin at (0, 0, 0) |
| FBX colour mask | `Tools/fbx_mask_report.py` | PASS | body: primary 4988, secondary 2984, accent 3124, fixed 6964 corners; Mouth: fixed 120 |
| Preview renders | `Tools/render_preview.py` (front / 3/4 / side / back / top) | PASS | chain follows the neck, pendant hangs on the chest, olive branch readable from the front |
| Leaders lineup | Lamb Leader v001, Dove Leader v002, Lion Leader v001 | observation | the Dove now has a chest accessory like the other two; still the slimmest (bird build) |
| Unity | Unity 6000.3.25f1 | NOT RUN | owner to check |

## User feedback

- 2026-10-29 (faithful English summary): "Pulled; the Dove Leader is fine." Checked by the owner in Unity. Accepted.
