# Rig and animation brief — R10 (all beasts)

Write the record in English. Discuss it with the user in their preferred language.

- Date / skill version: 2026-10-29 / blendsmith 2026.09.011-ks.1
- Scope: skeletons and the first animation set for the nine delivered meshes (Lamb, Lion, Dove × Baby / Adult / Leader). This brief only proposes; **no rig is built until the owner confirms** (R10).
- Inputs inspected: GDD §4 (S2 idle + tap reaction, S6 happy + evolve), §7.2 (animations: idle, happy, evolve; "humanoid / quadruped skeleton each one set"); Lamb/Lion briefs (shared leg placement for a shared quadruped skeleton); Dove brief Q1 (own bird skeleton, confirmed 2026-10-21); `BeastView.cs` (current procedural hop / spin / evolve-glow on the whole model).
- Engine: Unity 6000.3.25f1, URP, Web; `com.unity.modules.animation` is already in the manifest.

## Owner request (2026-10-29)

Faithful English summary: "Switch to UGUI first, and finish the remaining four of the five items." For this item, R10 requires the owner to confirm what needs to animate before rigging, so the deliverable this round is this brief plus questions.

## What is already animated (no rig needed)

`BeastView` moves the whole model in code: idle bob, tap = hop, level-up = hop + spin, evolve = glow → swap mesh → appear. These keep working with or without a rig.

## Proposal

### Skeletons (two sets, per GDD §7.2 and Dove Q1)

| Skeleton | Used by | Bones (≈) | Notes |
| --- | --- | --- | --- |
| Quadruped | Lamb, Lion (Baby / Adult / Leader) | root, hips, spine, chest, neck, head, jaw (mouth), 4 legs × 3 (upper, lower, paw/hoof), tail × 3, ears × 2 | One hierarchy and bone names for all six meshes; bone **lengths** differ per mesh (Lion Adult brief: "shared hierarchy, rotation-based animation"). Leg roots already line up (Baby x 0.15, y −0.08/0.20; Adult x 0.17–0.18). |
| Bird | Dove (Baby / Adult / Leader) | root, body, chest, neck, head, beak (lower = `Mouth`), 2 wings × 2 (shoulder, tip), tail fan, 2 legs × 2 | Wing hinge at the shoulder (front-top of the wing), as noted in the Dove scripts. |

Skinning: automatic weights, then fixes at the neck and leg roots. Accessories (cape, crown, necklace, wreath, pendant) are weighted to the bone they sit on (head, chest), so they move with the body.

### Animation set (first round)

| Clip | Where it is used | Length | Quadruped | Bird |
| --- | --- | --- | --- | --- |
| Idle | S2 home, always | 3 s loop | breathe (chest), slow tail sway, ear flick every few seconds | breathe, small head tilt, tail twitch |
| Happy | tap, level-up (S6) | 1 s | small hop, tail wag | wing flap ×2, hop |
| Wave hello | first meeting (S1), opening the game | 1.5 s | sit, lift one front paw (Lion shows its paw pads) | lift one wing |
| Eat the fruit | after picking a fruit (S5) | 1.5 s | open mouth (jaw), chew ×2 | peck ×2 (beak opens) |
| Evolve | stays as code (glow → swap mesh) | — | — | — |

Blinking: not in this round (eyes are separate shapes joined into the body; a blink would need eye bones or blend shapes — proposed for later).

### Unity side

- One **Animator Controller per skeleton** (Quadruped, Bird), the same states for every beast: Idle (default) → Happy / Wave / Eat (trigger, then back to Idle).
- Clips are exported in the FBX with the rig (Generic animation type, not Humanoid). Because bone names are identical across a skeleton's meshes, one set of clips per skeleton is shared by its three forms.
- `BeastView` gains `Play("Happy")` etc. and keeps its code motion as the fallback when a model has no Animator.
- Build size: nine rigged meshes plus about 8 clips should add roughly 1–2 MB (the current build is 14.2 MB, budget 30 MB).

### Production order

1. Quadruped skeleton on Lion Baby → Idle + Happy → check in Unity (proves the pipeline end to end).
2. Same skeleton on the other five quadruped meshes; Wave + Eat.
3. Bird skeleton on the three Dove meshes; the four clips.

## Questions for the owner — R04/R10 recap

- **Q1 Clip list:** Idle, Happy, Wave hello, Eat the fruit (evolve stays as code) — OK, or add / remove any?
- **Q2 Wave hello:** play it at the first meeting and every time the game opens, or only at the first meeting?
- **Q3 Blinking:** skip for now (as proposed), or include in this round?
- **Q4 Style of motion:** gentle and slow (calm, matches the "no pressure" principle) or bouncy and lively?
- **Q5 Order:** start with Lion Baby as the pipeline test (as proposed), or another beast?
- **Q6 Who animates:** the assistant keys all clips in Blender by script (consistent, editable source as with the models), or the owner wants to learn by keying some clips in Blender's Pose Mode?

## Owner answers (2026-10-29, faithful English summary)

1. Clips: also add **Sleep** and **Play with a toy**.
2. Wave hello: **every time** the game opens.
3. Blinking: **not now**.
4. Motion style: **Lion lively; Lamb and Dove gentle**.
5. Start with the **Lion**.
6. The assistant animates, but must **write it up as documentation in the art docs**; the owner will learn rigging in a separate session.
7. Motions must **not be abnormally twisted**; they must respect **IK** (feet planted, joints bending the natural way).

## Decisions taken from the answers (assistant, owner may adjust)

- Clip set per skeleton: Idle, Happy, Wave, Eat, Sleep, Play (six). Evolve stays in code.
- Legs use **IK** in Blender (an IK target bone per foot plus a pole bone per knee/elbow), so feet stay planted while the body moves and joints bend only forward/backward; clips are baked to the deform bones on export.
- Validation for "no abnormal twisting": scripted checks on every clip — planted feet do not slide (< 1 cm) when they should be planted, no bone rotates more than its limit, knees/elbows never bend backwards — plus preview renders of key frames.
- Unity plays clips with the **legacy `Animation` component** (FBX import type Legacy): no Animator Controller asset needed, clips play by name from code. Revisit only if blending needs grow.
- Rigging is a separate step after `finalize_export.py`: `art/blender/rig_quadruped.py` opens the finalized `.blend`, adds the armature, weights and clips, saves a new version and exports the FBX with animation.
- Production order: **Lion Baby → Idle + Happy → owner checks in Unity**, then the other four Lion Baby clips, then Lion Adult/Leader, then Lamb (gentle), then the bird skeleton for Dove (gentle).

## Open items raised by the answers

- **Sleep with open eyes:** blinking is "not now", but a sleeping beast with open eyes looks odd. Options: (a) closed-eye shapes swapped in only for Sleep (two small curved lines, no blink animation), (b) sleep facing away / head tucked so the eyes are hidden, (c) add blinking after all.
- **The toy:** which toy? Proposal: a small ball (fixed colour, shared by all beasts), appears only during the Play clip.

## Owner decisions on the open items (2026-10-29, faithful English summary)

- Sleep eyes: "(a) first, then (c)" — now: closed-eye arcs shown only during Sleep; later: add blinking.
- Toy: a small ball.

Implementation (assistant): an `eye.L/R` bone carries the open eyes and a `lid.L/R` bone carries closed-eye arcs that are collapsed to a point at rest; Sleep scales the eye bones down and the lid bones up. The ball is part of the mesh on a `toy` bone, collapsed at rest and expanded only in Play. Both stay inside the single mesh and material (profile budget) and need no extra Unity setup.

## Status

- **Confirmed to start** (2026-10-29) for the Lion Baby skeleton with Idle + Happy; Sleep and Play unblocked the same day (decisions above).
