# Pre-production brief — Lion Leader

- Date / skill version: 2026-10-12 / blendsmith 2026.09.011-ks.1
- Scope: first production of Lion Leader (stage 4 mesh). Script `art/blender/lion_leader.py`; outputs `art/models/Lion/`.
- Inputs: Lion Adult v007 (accepted: "很棒，味道出來了"), Lamb Leader v001 (gold accessories), profile, Meshy Lion Cub reference (worklog 010).

## Owner request (2026-10-12)

"Start Lion Leader; this time replace the cape with a crown and a necklace."

## Decisions taken by the assistant (owner may adjust)

| Item | Decision |
| --- | --- |
| Base | Run `lion_adult.py` (v007) unchanged, then add leader parts — the adult's later fixes carry over automatically. |
| Mane | Third, larger ring behind the adult's two rings (same metaball) — a fuller "lion king" mane; still frames the face only. |
| Crown | Small gold crown between the ears, tilted 10° forward: 15-sided band, five cone points with ball tips (front point tallest), ruby on the front. Fixed gold (same value as Lamb Leader clasps), fixed ruby red. |
| Necklace | Gold chain ring ray-cast onto the body: high on the withers (behind the mane), low on the chest below the mane; round gold medallion with a ruby. |
| Face | Same as adult (no mature-eye change this round). |
| Budget | Body loft decimated to 75 % and mane target 1,150 to give ~900 triangles to the accessories. |

## Status

Built as Lion_Leader v001; awaiting owner review.
