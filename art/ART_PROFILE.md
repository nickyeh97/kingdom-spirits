# Art profile — kingdom-spirits

Version: **1** (2026-10-12). Traditional Chinese reading copy: [ART_PROFILE.zh-TW.md](ART_PROFILE.zh-TW.md); update both together.

This profile holds project-wide decisions for every 3D model in this repository. The [blendsmith skill](../.claude/skills/blendsmith/SKILL.md) treats them as the owner's explicit, already-confirmed instructions. Asset-specific details go in each asset's brief or worklog. Requirements and limits come from [docs/GDD.md](../docs/GDD.md) §7 and [docs/DESIGN_PRINCIPLES.md](../docs/DESIGN_PRINCIPLES.md).

## Style and target

| Decision | Value |
| --- | --- |
| Style mode (R02) | **NPR toon + outline.** Chibi low poly, toon bands from the engine shader, outline required. No Normal/Roughness/Metallic maps. |
| Primary engine | Unity 6000.3.25f1 (6.3 LTS), URP, **Web** build for phone browsers. |
| Secondary engine | Unreal — export preset kept for future use; import test NOT RUN until an Unreal project exists. |
| Outline method | **Open — decide during G2 shader work.** Candidate for Unity URP: a normal-extrude shader pass; add smoothed outline normals if gaps appear at part joins. |
| Colour delivery | Vertex colour attribute `Mask` (see below) + material parameters; 8 palettes; growth pattern mask texture on UVs from stage 2. |
| Art boundary | Palworld-like *style vocabulary* only; never copy any Palworld character's shape, name, palette or signature features. Beasts are original, based on biblical animals; names display in English (Lamb, Dove, Lion; later Deer, Eagle, Fish). |

## Budgets and meshes

- Three meshes per species: Baby (stages 1–2), Adult (stage 3), Leader (stage 4). One beast on screen at a time.
- **At most 8,000 evaluated triangles per mesh** (counting triangles, not faces). Single material. Textures at most 1024²; pattern mask at most 512².
- Web build at most 15 MB compressed in total.
- Origin at the feet centre (Z = 0), facing −Y in Blender (Unity forward after export), 1 unit = 1 metre.
- Mouth stays a separate child object (`Mouth`) for the "eats the fruit of the Spirit" animation.

## Colour mask convention (`Mask`, face-corner float colour)

| Mask value | Meaning |
| --- | --- |
| A = 1, R = 1 | primary palette slot (e.g. wool) |
| A = 1, G = 1 | secondary slot (face, ears, legs) |
| A = 1, B = 1 | accent slot (cheeks, inner ears, cape) |
| A = 1, channel = 0.45 | lining: 45% of that slot's colour (darker shade, follows palette swaps) |
| A = 0 | fixed colour = RGB (ink for eyes/nose/hooves, white eye shine, ivory horns, gold, collar red) |

Slot meaning is per species (Lamb: primary wool, secondary face; Lion: primary body skin, secondary flesh tone, accent fur). The finalize script maps common part names to slots, and a shape script can override any part with `o["mask"] = (R, G, B, A)`; use the override whenever a name means something different for the species.

Growth patterns (pattern mask on UVs, from stage 2): Lion — cub spots on the baby mesh, tabby-cat stripes on grown meshes. Lamb — to be decided.

Engine formula: `colour = A ? (R*primary + G*secondary + B*accent) : RGB`. FBX exports colours as Linear. Fixed colours shift when re-imported through sRGB conversion; the engine shader must account for this (open item for G2).

## Pipeline and delivery (R11, R12)

The owner is learning procedural modelling, so **both** the scripts and the verified `.blend` are deliverables.

1. **Shape script** (editable source, commented in Traditional Chinese for learning): `art/blender/<species>_<stage>.py`, e.g. `lamb_baby.py`. It sets `scene["spirit_name"]` and optionally `scene["wool_tri_target"]`.
2. **Finalize** `art/blender/finalize_export.py`: converts metaballs/curves, decimates wool to the target, applies rotation/scale, removes n-gons, writes `Mask`, joins all but `Mouth`, unwraps UVs on every mesh, builds a readable preview material, enables selection/Extras, exports FBX, saves a versioned `.blend`.
3. **Verify** `art/blender/verify_blend.py` on the saved file in a fresh Blender process; all checks must PASS.

Command line (from the repository root):

```
blender -b --python art/blender/lamb_baby.py --python art/blender/finalize_export.py -- art/models/Lamb --unreal
blender -b art/models/Lamb/Lamb_Baby_v001.blend --python-exit-code 1 --python art/blender/verify_blend.py
```

Outputs live in `art/models/<Species>/`: `<Name>_vNNN.blend` (never overwritten), `<Name>.fbx` (Unity preset), `<Name>_UE.fbx` (Unreal preset). Do not put `.blend` files inside Unity `Assets/`.

| Preset | Axes | Scale | Other |
| --- | --- | --- | --- |
| Unity | Forward −Z, Up Y, bake space transform | FBX_SCALE_ALL (1 m = 1 unit) | smoothing Face, colours Linear, no leaf bones |
| Unreal | Blender defaults (Forward −Z, Up Y), converted by the Unreal importer | FBX_SCALE_NONE (metres written, Unreal converts to cm) | smoothing Face; set vertex colour import to Replace; lightmap UV generated on import |

## Versions

- Owner's desktop: Blender 5.2. Assistant (cloud, headless): Blender 4.2.23 LTS. Scripts must run on both. Each `.blend` stores `scene["spirit_built_with"]`.

## Process decisions

- **R04:** full recap only at the first production of each new asset or mesh tier; later feedback adjustments are described in a sentence and done.
- **R07:** English is authoritative for CLAUDE.md, skill documents, templates, this profile and worklogs; Traditional Chinese copies are updated in the same change. Conversation follows the owner's language (Traditional Chinese, Taiwan). Script comments stay Traditional Chinese for learning.
- **Progress:** `docs/PROGRESS.md` records only major art items — whether each species and stage is done, and pipeline/shader/rig milestones. Per-version art changes go in worklogs only.
- **Worklogs:** `docs/art-worklog/YYYY-MM-DD_NNN_<topic>.md`, English, committed so every computer and session can read them.
- **Teaching:** the owner learns step by step; explain new techniques and terms (see the [glossary](../.claude/skills/blendsmith/references/glossary.zh-TW.md)).

## Project lessons (summary; details in the feedback register)

- Shape hierarchy: large form → few medium lobes → few small details. Metaballs fuse lobes.
- Calibrate metaball sizes: surface = 0.574 × radius (stiffness 2), 0.66 × (stiffness 3.5) at threshold 0.6.
- Scalloped wool: lobe spacing / radius ≈ 2.4; compute counts from ring circumference.
- Closed shell first, subtract with negative elements (hood with face window).
- Accessories hug the body with Shrinkwrap from a draft that starts inside a hull larger than the wool.
- Spend triangles on the silhouette; small parts use low-resolution primitives.
