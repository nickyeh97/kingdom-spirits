# Pre-production brief — Lion Baby

Write the record in English. Discuss it with the user in their preferred language.

- Date / skill version: 2026-10-12 / blendsmith 2026.09.011-ks.1
- Current scope / output location: first production of Lion Baby (stages 1–2 mesh). Scripts `art/blender/lion_baby.py`; outputs `art/models/Lion/`.
- Input files and references: no user-supplied images yet. Inspected: project profile, GDD §3.3–3.4, §4 S1, §7; Lamb Baby v001 (style and proportion reference for consistency). Real lion-cub anatomy from general knowledge, not yet from inspected photos.
- Blender and receiving-application versions: Blender 4.2.23 LTS (assistant), 5.2 (owner); Unity 6000.3.25f1 primary, Unreal preset secondary.
- Purpose: game (mobile Web), one beast on screen; nearest view is the "beast home" screen (full body, portrait). Deformation later via a shared quadruped skeleton (GDD §7.2), no rig this round.

## Intake completeness and communication

- Language: Traditional Chinese for conversation; this brief in English.
- Reused from the profile (no need to ask): NPR toon + outline; Unity primary / Unreal secondary; ≤ 8,000 evaluated triangles; single material; colour mask `Mask`; every mesh UV-unwrapped; scripts + verified `.blend` + FBX; origin at feet, facing −Y; separate `Mouth` object.
- Asked in the R04 recap: design choices Q1–Q6 below.
- Topology: mixed triangles/quads (same as Lamb; decimated metaball fur is triangles).
- Atlas: one UV map per mesh, no textures this round; future pattern mask ≤ 512² on the same UVs. No UDIM.

## Reference analysis and questions

| Part/item | Evidence and source | Confirmed | Hypothesis / unknown | Question | Decision |
| --- | --- | --- | --- | --- | --- |
| Overall proportion | Lamb Baby v001; GDD S1 shows Lamb/Dove/Lion babies side by side | head ≈ body (1:1), same overall height as Lamb Baby (~1.1) | — | — | reuse |
| Mane | Real cubs have no mane; a soft fluffy crown/cheek fur at most | — | small crown tuft + soft cheek ruff reads "lion" without an adult mane | Q1 | pending |
| Ears | Real lion ears are small, round, with dark backs | — | round ears, inner accent | — | proposal |
| Muzzle / mouth | Lamb lesson KS-L05 (avoid pig snout) | separate `Mouth` object | two small whisker pads + small triangle nose + "ω" cat mouth | Q2 | pending |
| Coat spots | Real cubs have faint rosette spots that fade with age | GDD: pattern appears from stage 2 | spots could be the Lion's stage-2 pattern | Q3 | pending |
| Tail | Real cubs: long thin tail, tuft grows later | — | curve tail with small soft tuft | — | proposal |
| Legs/paws | Lamb uses hooves; lions have round paws | shared skeleton needs same leg placement | same leg positions as Lamb Baby; round paw balls | Q5 | pending |
| Colour slots | profile mask convention | primary/secondary/accent | primary = body fur; secondary = muzzle, belly, paws, inner ears; accent = crown tuft, tail tuft, cheeks? | Q4 | pending |

## Supplementary reference research — when useful

| Source | Subject | Inspected | Finding and limits | Agreement | User confirmation |
| --- | --- | --- | --- | --- | --- |
| none yet | lion cub anatomy | no | general knowledge only; owner may supply preferred photos (Q6) | — | pending |
| https://img.ltn.com.tw/Upload/news/600/2018/08/10/phprod9RQ.jpg (accessed 2026-10-12, supplied by owner) | real lion cub, frontal | yes | large round ears set wide and high; heart-shaped face narrowing to a longer muzzle with a nose bridge; wide dark nose; puffy cream whisker pads and small white chin; dark tear marks from inner eye corners; small dark forehead marks; thick legs. Proportions are photographic, adapted to chibi (eyes kept as Lamb Baby for S1 consistency). | owner reference for v002 face | used in v002 |

## Occluded components and internals

| Component | Why it may be needed | Proposal | User choice |
| --- | --- | --- | --- |
| Belly underside | camera never sees it | simplified (no fur lobes) as Lamb | reuse |
| Mouth interior | eating animation opens the mouth | dark mouth shape only, no teeth/tongue | pending (Q2) |

## Production specification

- Units, origin, orientation: metres; origin at feet centre; faces −Y.
- Parts: Head, Body (metaball fur), Muzzle pads, Nose, Mouth (separate child), Eyes/EyeShine, Cheeks, Ears/EarInner, Legs/Paws, Tail (curve) + TailTuft, CrownTuft/CheekRuff (metaball, same object as body fur).
- Budget: ≤ 8,000 evaluated triangles; target 6,000–7,000 (Lamb Baby 6,824). Counting triangles.
- UVs: Smart UV Project per mesh in finalize; non-overlapping; future pattern mask ≤ 512².
- NPR colour delivery: `Mask` per profile; outline method open (G2).
- Handoff: selection and Extras on (finalize_export).
- `.blend`, FBX (Unity + Unreal presets), verification with `verify_blend.py`.
- R11 readiness: Blender 4.2.23 available headless; `art/models/Lion/` writable.

## Rig specification — R10

- Not in this round. Requirement carried forward: leg positions compatible with Lamb Baby for a shared quadruped skeleton.

## Complete user-facing requirement recap — R04

- Presented to the user: 2026-10-12 (chat, Traditional Chinese).
- User confirmation 2026-10-12 (faithful English summary):
  - Q1: option (a) — small crown tuft plus soft cheek ruff.
  - Q2: approved — whisker pads, triangle nose, "ω" mouth as a separate object.
  - Q3: baby uses cub spots as its stage-2 pattern; grown forms use tabby-cat-style stripes.
  - Q4: primary is the body **skin**, not fur; secondary (muzzle, belly, paws, inner ears) must read as a cute flesh tone; fur (tuft, ruff, tail tuft) is accent; blush and pads fixed pink (assistant proposal, not objected).
  - Q5: paw pads (toe beans) required so they show when the beast waves hello.
  - Q6: no references; design from real lion-cub features; must share one skeleton with the other quadrupeds.
  - Rig: not this round; shared skeleton compatibility required.

## Basis for starting production

- Status: **confirmed to start** (2026-10-12). Built as Lion_Baby v001.
- Stage-2 spot pattern texture and adult tabby stripes: later scope (pattern mask on UVs).
- 2026-10-12 owner decision: body spots stay visible from stage 1 (option a, geometry on the baby mesh). Blush removed in v003.
