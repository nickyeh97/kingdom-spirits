# 2026-10-12 — Lion Adult v005 (Q style on the reference silhouette) and Lion Baby v004 (natural coat)

## Owner decisions

- Style back to Q; apply the Meshy Lion Cub silhouette and coat (worklog 010).
- Lion Baby also switches from cub spots to the natural coat. Start v005.

## Lion Adult v005 (`art/blender/lion_adult.py`, rewritten; v003 is in git history)

- **Body = loft from a measured profile.** Cross-sections of the aligned reference (back height, belly height, torso half width every 7.5 cm) are stored in `REF_PROFILE` and mapped to Q proportions: length × 0.68 so the paw spacing equals the shared skeleton (front y −0.22, hind y 0.38, x ±0.17), legs shortened (belly 0.40 → 0.30 m), height × 0.85, width × 0.95. Rounded-square sections (superellipse power 2.6), 28 points per ring, end rings shrunk and closed with triangle fans. Silhouette order kept: deep chest, highest withers, level back, slightly lower rump.
- **Face:** Lion Baby v003 face (accepted) scaled × 1.1 around the head centre via `F()`; snout and whisker pads slightly wider (reference has a broad muzzle). Head centre (0, −0.52, 1.10), carried above and ahead of the shoulders; neck ellipsoid bridges head and chest.
- **Legs:** v002/v003 cat legs (owner: "the legs resemble"), z shortened for Q; shoulder and thigh ellipsoids enclose the leg tops.
- **Cheek fur:** tapered chain of 4 metaballs per side flaring back and out from the lower head. Tried first: Lion Baby's bead ruff (read as a string of beads from the side) and 3 large balls (read as swellings from the front).
- **Tail:** long hanging curve with a dark tuft (accent × 0.6).

## Natural coat (both meshes)

| Zone | How |
| --- | --- |
| Base | primary |
| Darker spine | point attribute `shade` = 1 − 0.15·smoothstep(normal z 0.3–0.9); finalize multiplies slot channels |
| Light chest, belly, muzzle, chin, paws, inner ears | secondary parts |
| Dark ear backs | primary × 0.6 |
| Dark tail tuft (adult) | accent × 0.6 |
| Fur flow | pattern mask 512²: 3D noise in object space, scale (26, 26, 6) adult / (30, 30, 7) baby, mapped to 0.82–1.0 / 0.84–1.0, baked onto UVs |

Lion Baby v004: spots (body and forehead) and their helper functions removed; `shade`, ear backs, pattern and preview palette added. Everything else unchanged.

## Pipeline changes

- `finalize_export.py`: `shade` attribute; procedural pattern bake after UV unwrap (`scene["pattern"]`) to `textures/<Name>_Pattern.png`, packed and stored as `o["pattern"]`; preview material multiplies only the palette branch by the texture (fixed colours unaffected); `scene["preview_palette"]` converted from sRGB to Linear (first v005 preview was washed out).
- `verify_blend.py`: pattern mask packed and ≤ 512².
- Regression: Lamb Leader rebuilt in scratch — 16 PASS.

## Verification

- `Lion_Adult_v005.blend`: 17 PASS, 0 FAIL, 7,552 triangles.
- `Lion_Baby_v004.blend`: 17 PASS, 0 FAIL, 6,632 triangles.
- FBX (Unity + Unreal presets) re-exported for both; the rotated v004 adult FBX is replaced.

## Open

- Owner acceptance of both.
- Engine shader must multiply palette by the pattern mask (G2).
