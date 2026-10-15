# 2026-10-12 — Lion Adult v004 from a CC0 Meshy model

## Why

Owner rejected procedural Lion Adult v001–v003 (silhouette and face never matched the references). Owner chose a CC0 Meshy "Lion Cub" model by cyber_fox ("這種也行") and committed it to `art/source/` (provenance in `art/source/LICENSE.md`). Task: turn it into a game-ready mesh.

## Source inspection

- One object `Mesh_0`: 170,137 vertices / 340,270 triangles, `UVMap`; 1.41 × 1.90 × 1.40 m; head already toward −Y.
- `Material_0`: Principled BSDF with three packed 2048² images — base colour (sRGB), roughness/metal (Non-Color via Separate Color), normal map.
- No text blocks or scripts; opened with `--disable-autoexec` and appended with `bpy.data.libraries.load` (objects only).

## Process (`art/blender/lion_adult_meshy.py`, then `finalize_export.py`)

1. Append `Mesh_0` as High; scale to 1.42 m height (same as v003), centre X/Y, feet at Z = 0 (bounds via numpy `foreach_get` — per-vertex Python loops timed out on 170k vertices).
2. Rewire the source material to base colour → Emission so the bake records pure albedo (no lighting, no metallic darkening).
3. Copy to Low, Decimate (Collapse, X symmetry) 340,270 → 7,600 triangles; smooth shading.
4. New UVs on Low (Smart UV Project, 66°, margin 0.02); bake EMIT selected-to-active (cage extrusion 0.03, max ray 0.08, margin 16 px) into a 1024² image; saved to `art/models/Lion/textures/Lion_Adult_Albedo.png` and packed into the `.blend`.
5. Delete High and all source data; mark Low `mask = (1,0,0,1)`, `keep_uv`, `albedo`; scene `has_mouth = False`.
6. Finalize generalized: `Mouth` optional (`scene["has_mouth"]`), Smart UV skipped for `keep_uv` objects, preview material multiplies by the albedo image (primary preview colour white).
7. Verify generalized: mouth check reported as SKIP when `has_mouth = False`; new check that the albedo image is packed and ≤ 1024².

Build time ≈ 11 s on 4 CPU threads.

## Verification

`Lion_Adult_v004.blend` (3.2 MB): 11 PASS, 1 SKIP (mouth, recorded deviation), 0 FAIL — 7,600 evaluated triangles, no n-gons, UVs inside 0–1, `Mask`, scale applied, selectable, Extras on, albedo packed 1024². FBX: `Lion_Adult.fbx` (Unity), `Lion_Adult_UE.fbx` (Unreal, import NOT RUN). Preview renders (three-quarter, front, side) reviewed: face, ears, paws and tail tuft survive the decimation; texture detail carries the fur.

## Deviations from the profile (owner accepted the trade-offs before the build)

- **Style:** semi-realistic, not the chibi Q style of Lamb / Lion Baby.
- **Colour:** texture-driven; palettes can only tint (primary multiplies the albedo, e.g. a white lion). No secondary/accent slots, no pattern mask.
- **Mouth:** no separate `Mouth` object (mouth is painted in the texture); the eating animation needs a shape key or an added part later.
- **Skeleton:** paw positions follow the source pose (walking stance), not the shared quadruped landing points.
- **UVs:** Smart UV on a decimated mesh gives many small islands; fine for the baked albedo, poor for hand-painting a future pattern mask.
- **NPR:** the baked albedo contains painted shading; under the toon shader it may look doubled. Decide in G2 shader work.

## Open

Owner acceptance of v004; whether Lion Baby / Leader should follow the same imported style for consistency.
