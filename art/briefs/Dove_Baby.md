# Pre-production brief — Dove (Baby first; Adult and Leader direction)

Write the record in English. Discuss it with the user in their preferred language.

- Date / skill version: 2026-10-20 / blendsmith 2026.09.011-ks.1
- Current scope / output location: first production of the Dove, the last launch species (GDD §3.4 #2, anchor verse Matthew 3:16). This brief fixes the direction for all three meshes; Baby (stages 1–2) is built first. Scripts `art/blender/dove_baby.py` (then `dove_adult.py`, `dove_leader.py`); outputs `art/models/Dove/`.
- Input files and references: no user-supplied images yet. Inspected: project profile, GDD §3.4, §4 S1, §7.2–7.3; Lamb Baby v001 and Lion Baby v004 (style, height and head ratio for the S1 side-by-side screen). Real dove anatomy from general knowledge, not yet from inspected photos.
- Blender and receiving-application versions: Blender 4.2.23 LTS (assistant), 5.2 (owner); Unity 6000.3.25f1 URP primary, Unreal preset secondary.
- Purpose: game (mobile Web), one beast on screen; nearest view is the "beast home" screen (full body, portrait). Must stand next to Lamb Baby and Lion Baby at first meeting (S1). No rig this round.

## Intake completeness and communication

- Language: Traditional Chinese for conversation; this brief in English.
- Reused from the profile (no need to ask): NPR toon + inverted-hull outline (decided 2026-10-20); Unity primary / Unreal secondary; ≤ 8,000 evaluated triangles; single material; colour mask `Mask`; every mesh UV-unwrapped; scripts + verified `.blend` + FBX; origin at feet, facing −Y; separate `Mouth` object; Q (chibi) style for every species; English display name "Dove".
- Asked in the R04 recap: design choices Q1–Q7 below.
- Topology: mixed triangles/quads (same as Lamb/Lion; decimated metaball down is triangles).
- Atlas: one UV map per mesh; growth pattern mask ≤ 512² on the same UVs from stage 2. No UDIM.

## New constraint: the Dove is not a quadruped

GDD §7.2 plans one humanoid and one quadruped skeleton shared across species. A dove fits neither, so the Dove needs its **own bird skeleton** (body, neck, head, two wings, tail fan, two legs) and its own idle / happy / evolve animations. This adds animation work that Lamb and Lion share. The shape below keeps that cost low: wings fold against the body and open as one simple hinge each; legs are short and only shift weight. Rig specification follows in a separate R10 brief before rigging (G2 rig/animation step).

## Reference analysis and questions

| Part/item | Evidence and source | Confirmed | Hypothesis / unknown | Question | Decision |
| --- | --- | --- | --- | --- | --- |
| Skeleton / pose | GDD §7.2 (humanoid + quadruped only) | needs a third skeleton | standing chibi dove on two short legs, wings folded at the sides, can lift them for "happy" | Q1 | pending |
| Overall proportion | Lamb Baby v001, Lion Baby v004; GDD S1 | same overall height as the other babies (~1.1) | round "fluffy ball" body, head ≈ 0.8 of body, big eyes as Lamb/Lion | — | proposal |
| Base look | Matthew 3:16; real doves: white dove (symbolic) or grey rock dove with iridescent neck | colours come from the 8 palettes | body follows the primary slot, so p8 雲朵 reads as a white dove and p1 奶油 as a cream dove; no iridescent neck (hard in toon style) | Q2 | pending |
| Colour slots | profile mask convention | primary/secondary/accent | primary = body, head, wings; secondary = face, chest, belly (lighter); accent = wing-tip and tail-tip bands, cheek blush; fixed = beak and feet soft coral, eyes ink, eye shine white | Q3 | pending |
| Beak / mouth | profile: separate `Mouth` for the "eats the fruit" animation | separate `Mouth` | small rounded beak; the lower half is the `Mouth` object so it can open; tiny cere bump on top | — | proposal |
| Head | real doves: small round head, no crest | — | baby: a small soft tuft of down on top (reads "young"); adult: smooth head | — | proposal |
| Wings | real doves: rounded wings, two dark wing bars on rock doves | — | baby: short stubby wings; adult: full folded wings with a visible primary-feather edge | — | proposal |
| Tail | real doves: rounded tail fan | — | baby: short tail nub; adult: fan of 5–7 rounded feathers; leader: longer tail plumes | — | proposal |
| Legs / feet | real doves: short coral-red legs, three toes forward | — | short legs with three rounded toes, fixed coral | — | proposal |
| Growth pattern (stage 2+) | GDD §7.2 (pattern mask from stage 2); Lion uses a natural coat | — | (a) soft scalloped feather pattern on wings and back, or (b) two wing bars like a rock dove | Q4 | pending |
| Leader accessory | GDD §7.2: halo is shared; each species adds its own (Lamb cape, Lion crown + necklace) | halo shared | olive-leaf wreath on the head (Genesis 8:11, peace), gold leaves with a fixed green; not in the beak, so the mouth can still open | Q5 | pending |
| Theme check | Matthew 3:16 (the Spirit descending like a dove); DESIGN_PRINCIPLES | — | the Dove is a companion named after a biblical animal, not a picture of the Holy Spirit; keep it gentle and plain, no extra glow beyond the shared stage-4 halo | Q6 | pending (leader / 師母 view welcome) |

## Supplementary reference research — when useful

| Source | Subject | Inspected | Finding and limits | Agreement | User confirmation |
| --- | --- | --- | --- | --- | --- |
| none yet | dove anatomy | no | general knowledge only; owner may supply preferred photos or a reference model (Q7) | — | pending |

## Occluded components and internals

| Component | Why it may be needed | Proposal | User choice |
| --- | --- | --- | --- |
| Underside between the legs | camera rarely sees it | simplified, closed down surface | proposal |
| Under-wing surface | visible when wings open in "happy" | same primary colour, no separate feather detail | proposal |
| Mouth interior | eating animation opens the beak | dark mouth shape only, no tongue | proposal |

## Production specification

- Units, origin, orientation: metres; origin at feet centre; faces −Y.
- Parts (Baby): Body (metaball down, joined with head down), Head, Face (secondary), Beak upper, `Mouth` (beak lower, separate child), Eyes/EyeShine, Cheeks, Wings L/R, TailNub, HeadTuft, Legs/Feet.
- Budget: ≤ 8,000 evaluated triangles; target 6,000–7,000 (Lamb Baby 6,824). Counting triangles.
- UVs: Smart UV Project per mesh in finalize; non-overlapping; pattern mask ≤ 512².
- NPR colour delivery: `Mask` per profile; `o["mask"]` overrides for Dove-specific parts (finalize SLOT names like `Body`/`Belly` already map; Wing/Beak/Feet need entries or overrides).
- Outline: inverted hull; avoid hard edges where the wings meet the body (smooth normals), so the outline does not split.
- Handoff: selection and Extras on (finalize_export).
- `.blend`, FBX (Unity + Unreal presets), verification with `verify_blend.py`; FBX copied to `Assets/Art/Resources/Beasts/Dove_Baby.fbx` (the placeholder is replaced automatically).
- R11 readiness: Blender 4.2.23 must be reinstalled in the assistant container before production (lost in the 2026-10 reset).

## Rig specification — R10

- Not in this round. Requirement carried forward: bird skeleton (see "New constraint"); wing hinge at the shoulder; tail fan as one bone; legs two bones each.

## Complete user-facing requirement recap — R04

- Presented to the user: 2026-10-20 (chat, Traditional Chinese). Questions:
  - Q1 Skeleton: OK to give the Dove its own bird skeleton and animations (more work than sharing), standing on two short legs with folded wings?
  - Q2 Base look: body colour follows the palette (雲朵 = white dove); no iridescent pigeon neck — OK?
  - Q3 Colour slots as in the table (fixed coral beak and feet) — OK?
  - Q4 Growth pattern from stage 2: (a) soft scalloped feathers or (b) two wing bars?
  - Q5 Leader accessory: olive-leaf wreath on the head (plus the shared halo) — OK, or another idea?
  - Q6 Theme: keep the Dove a plain, gentle companion and not a depiction of the Holy Spirit — would the leader / 師母 like to weigh in?
  - Q7 References or route: any dove photos the owner likes? Procedural script (as Lamb/Lion Baby) by default; an AI-generated reference (as Lion Adult v004) only if the first result is weak.
- User confirmation 2026-10-21 (faithful English summary): Q1 OK; Q2 OK; Q3 OK; Q4 option (a) soft scalloped feathers; Q5 OK (olive-leaf wreath); Q6 "just note it for now"; Q7 "make a first version" (procedural script, no references).

## Basis for starting production

- Status: **confirmed to start** (2026-10-21). Built as Dove_Baby v001.
- Q6 is recorded as a design note only: the Dove stays a plain, gentle companion; no extra glow beyond the shared stage-4 halo.
- Colour-slot adjustment found while building (assistant, flagged to the owner): in all 8 palettes the secondary colour is *darker* than the primary (e.g. 雲朵 #E9EEF2 / #A9B6C2 / #3C4A57). A secondary chest would therefore read darker than the body, which is not dove-like. v001 uses primary = head, body, chest; secondary = wings and tail; accent = wing-tip and tail-tip bands (dark, like a rock dove's bands); blush fixed pink instead of accent (a dark accent blush would look like a bruise). Fixed coral beak and feet as confirmed.
- Stage-2 scalloped pattern (Q4 a): needs a stage switch in the shader (the baby mesh is shared by stages 1–2, and the pattern must appear only from stage 2). Not in v001; follow-up.
