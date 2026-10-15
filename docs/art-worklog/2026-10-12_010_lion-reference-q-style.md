# 2026-10-12 — Lion: back to Q style; Meshy model kept as silhouette and pattern reference

## Owner decision (faithful summary)

"Change the style back to Q (chibi), but record this silhouette and this fur pattern so they are applied to the lion." Lion Adult v004 (semi-realistic Meshy import) is **not** the delivered style. The Meshy Lion Cub (CC0, `art/source/`) becomes the reference for the lion's silhouette and coat pattern; the next Lion Adult is rebuilt in Q style.

## Bug found while measuring: v004 is rotated

The source model's spine is turned ≈ 29° around Z (head toward +X−Y, tail toward −X+Y). v004 only checked which end the head was on, so `Lion_Adult_v004.blend` and the current `Lion_Adult.fbx` / `_UE.fbx` face about 29° off forward. Fixed in `lion_adult_meshy.py`: spine = chest centroid → rump centroid, rotate the vertices in numpy so it lies on +Y, centre on the spine. Checked with a front render in a scratch build. Not re-delivered because the style is changing; the files are replaced when the Q-style Lion Adult ships.

Side note: setting `rotation_euler` and then `transform_apply(rotation=True)` in the same script did nothing (no depsgraph update in between); writing coordinates with `foreach_set` avoids the problem.

## Silhouette reference (measured after aligning, height 1.42 m)

| Feature | Measurement / observation |
| --- | --- |
| Overall | length 2.22 incl. tail; torso 1.10 long, 0.77 wide, 0.60 deep (z 0.45–1.05) |
| Legs | belly clearance 0.40–0.44 ≈ 30 % of height; thick legs, large round paws with visible toes |
| Back line | withers highest (1.14), level back (1.02–1.04), croup slightly lower (0.98) |
| Head | 0.45 long × 0.57 wide × 0.42 high; carried forward, top ≈ 0.28 above the withers; flat broad crown |
| Ears | large, round, set high on the sides of the head; dark backs |
| Face | broad muzzle, pale chin, dark nose leather, heavy brow |
| Tail | long and thin, hangs to ≈ 0.3 m, dark end tuft |
| Pose | walking stance; head turned slightly to its right (not to copy into the base pose) |

Q-style translation: keep the *order* of the silhouette — deep chest, level back with highest withers, head carried above and ahead of the shoulders, thick legs and big paws, long hanging tail with a tuft, big round high ears — but use chibi ratios (head ≈ body as in Lion Baby, shorter legs, Lion Baby eyes and face language).

## Coat pattern reference

Measured from the baked albedo (sRGB averages; include painted shading):

| Zone | Colour | Note |
| --- | --- | --- |
| Back / flank | #956343 / #8c5e40 | base tawny, slightly darker along the spine |
| Crown | #a17150 | lighter, fluffy |
| Muzzle, chin, chest ruff | #967054, lighter streaks | pale cream highlights |
| Belly | #7b543e | darker in the bake because of painted occlusion |
| Tail tip | #784d38 | dark tuft |

Pattern character: **no spots, no stripes** — a natural lion coat. Lighter zones on muzzle, chin, chest ruff and inner legs; darker spine, ear backs and tail tuft; fine directional fur strokes that follow the body (back → down the flanks, fluffier chest ruff and cheek fur). Delivery in Q style: a pattern-mask texture on UVs (≤ 512², profile) holding light/dark zones plus a fur-stroke grain; it must not look like a repeated copy-paste tile (owner's earlier rule). Not geometry stripes.

This replaces the earlier "tabby-cat stripes for grown meshes" decision. Lion Baby keeps its accepted cub spots unless the owner says otherwise.
