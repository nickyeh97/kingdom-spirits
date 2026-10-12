# Pre-production brief — Lion Adult

- Date / skill version: 2026-10-12 / blendsmith 2026.09.011-ks.1
- Scope: first production of Lion Adult (stage 3 mesh). Script `art/blender/lion_adult.py`; outputs `art/models/Lion/`.
- References inspected: Lion Baby v003 (face construction, colour slots), Lamb Adult v001 (stage-3 proportions), owner's lion-cub photo (face volumes). Real young-lion anatomy from general knowledge.
- Versions: Blender 4.2.23 (assistant) / 5.2 (owner); Unity primary, Unreal preset.

## Reused (profile and earlier confirmations)

NPR toon + outline; ≤ 8,000 evaluated triangles; `Mask` colour slots as Lion Baby (primary skin, secondary flesh tone, accent fur, fixed pink paw pads, no blush); UVs on every mesh; scripts + verified `.blend` + FBX; separate `Mouth`; tabby-cat stripes for grown forms (owner, 2026-10-12).

## Proposals awaiting confirmation

| Item | Proposal |
| --- | --- |
| Proportions / skeleton | Same as Lamb Adult: head scale 0.92, head raised and forward with a neck, body centre (0, 0.10, 0.66), legs x 0.18, y −0.22 / 0.38, length 0.42 — shared quadruped skeleton for the adult tier. |
| Face | Lion Baby v003 face (eyes, muzzle base, bridge ridge, nose, pads, ω mouth, tear marks) carried over through relative face coordinates, as Lamb Adult did. |
| Mane (Q1) | Young-lion short mane: a fluffy ring framing the face plus a chest ruff (accent); full flowing mane reserved for Leader. |
| Stripes (Q2) | Geometry strips at 72 % primary (same trick as spots): forehead "M"-style marks, 4–5 stripes across the back, rings near the tail end. Body spots removed. |
| Tail (Q3) | Longer tail with a gentle S curve and a bigger end tuft (lion signature), less curl than the baby. |
| Paws (Q4) | Larger round paws with pads, as baby. |

## Status

Confirmed 2026-10-12 (owner): (1) short young-lion mane, full mane for Leader — yes; (2) forehead "M" tabby mark — yes; (3) S-shaped tail — yes. Built as Lion_Adult v001.

2026-10-12 owner feedback on v001 (faithful summary): back-of-head mane ugly and unrealistic; legs, tail and face odd — use the supplied feline reference images for body shape; tabby M must follow real cats, not an isolated M; back stripes look strange. Owner explicitly deferred originality concerns to a later pass ("make it work first"); only body proportions were taken from the reference — mane shape and colours stay our own. v002 rebuilt accordingly. Shared skeleton: paw landing positions equal Lamb Adult; bone lengths differ (shared hierarchy, rotation-based animation).
