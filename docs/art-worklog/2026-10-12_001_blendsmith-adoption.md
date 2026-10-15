# Worklog — 2026-10-12 — 001 blendsmith adoption and Lamb v001 delivery

- Time / timezone: 2026-10-12, UTC
- Asset / project: kingdom-spirits — Lamb (Baby, Adult, Leader); project-wide art rules
- Skill version: none -> blendsmith 2026.09.011-ks.1 (modified derivative)
- Work type: specification / production / verification
- Status: complete for the scope below. Production status is separate from user acceptance (see User feedback).
- Related: Lamb shape work 2026-10-01 to 2026-10-06 (no worklog existed then; lessons recorded in `references/feedback-register.md`, KS-L01 to KS-L10).

## Context / user request

Faithful English summary of the owner's Traditional Chinese messages:

1. Read https://github.com/brianchenanimator/blendsmith and discuss applying it to Claude Code so all future models of the ministry game use these skills.
2. Choose option B (modify a copy in this repository). A separate fork to help the upstream author generalise NPR/PBR may follow later; for now target this game's models for Unity/Unreal.
3. R02: decide the style at kickoff — cartoon low poly uses toon thinking plus an outline; PBR uses full BSDF thinking plus BaseColor, Normal, Roughness and Metallic maps.
4. R03: every mesh must be UV-unwrapped, because both NPR and PBR need UVs.
5. R07: CLAUDE.md, skill rules, support documents, templates and worklogs in English; update the Traditional Chinese copy when an original changes.
6. R08: keep the upstream web-research behaviour.
7. R11: in this project deliver both scripts and the `.blend` (the owner is learning procedural modelling); a future fork need not sync scripts — the key is a verifiable `.blend`.
8. R04: only the first execution of a change needs full confirmation; later adjustments do not.
9. Explain every professional term in detail for learning.

## Confirmations / known and unknown

- Confirmed: items 2–8 above (explicit owner decisions, 2026-10-12).
- Assistant interpretations (flagged to the owner): Traditional Chinese copies are kept for documents that have one (skill, glossary, request template, CLAUDE.md, art profile); references, checklists, feedback register and worklogs are English-only. GDD, PROGRESS and other `docs/` files stay Traditional Chinese. Script comments stay Traditional Chinese for learning. Worklogs are committed in `docs/art-worklog/`.
- Open: outline method for Unity URP (decide in G2 shader work); Unreal and Unity import tests (no engine available in this environment).

## Scope / actions and implementation

- Merged `origin/main` (G0 Unity skeleton from the owner's home PC) into the branch; resolved the `docs/PROGRESS.md` conflict keeping both sides.
- Copied upstream `skill/blendsmith` (commit b46f037) to `.claude/skills/blendsmith`, kept LICENSE and the upstream notice, added a GPL §5a modification notice in `NOTICE.md`.
- Modified `SKILL.md` and `SKILL.zh-TW.md`: project-profile rule, version policy, R02 style modes, R03, R04, R07, R11, new R12 engine handoff; intake paragraph asks style mode and engines.
- Added `references/glossary.md` and `glossary.zh-TW.md`; added checklist §8 (NPR) and §9 (engine handoff); appended KS entries to the feedback register; updated the brief, request and worklog templates.
- Added `art/ART_PROFILE.md` (+ zh-TW). Rewrote `CLAUDE.md` in English; previous Chinese text updated into `CLAUDE.zh-TW.md`.
- `art/blender/finalize_export.py`: output-directory argument, `--unreal` preset, n-gon removal (poke), Smart UV Project on every mesh, R01 node layout with frames, R06 selection/Extras, versioned `.blend` save.
- New `art/blender/verify_blend.py`: fresh-reopen checks with non-zero exit on failure.
- Built and verified Lamb Baby/Adult/Leader v001 into `art/models/Lamb/`.

## Files / versions

| File | Action | Version/purpose |
| --- | --- | --- |
| `.claude/skills/blendsmith/**` | added, modified | 2026.09.011-ks.1 |
| `art/ART_PROFILE.md`, `.zh-TW.md` | added | profile v1 |
| `CLAUDE.md`, `CLAUDE.zh-TW.md` | rewritten / added | English original + copy |
| `art/blender/finalize_export.py` | modified | R03/R06/R11/R12 compliance |
| `art/blender/verify_blend.py` | added | R11 fresh-reopen verification |
| `art/models/Lamb/Lamb_Baby_v001.blend` | added | 1,608,209 bytes |
| `art/models/Lamb/Lamb_Adult_v001.blend` | added | 1,701,845 bytes |
| `art/models/Lamb/Lamb_Leader_v001.blend` | added | 1,707,853 bytes |
| `art/models/Lamb/*.fbx`, `*_UE.fbx` | added | Unity and Unreal presets |

## Decisions / concise rationale and tradeoffs

- Kept the skill name `blendsmith` with a `-ks.1` version suffix so the derivative is identifiable but future upstream merges stay simple. Project specifics live in `art/ART_PROFILE.md`, keeping the skill generic for the planned fork.
- Smart UV Project was chosen for automatic UVs on organic, decimated meshes; seams will be refined by hand where the growth pattern needs clean islands.
- N-gon caps are poked into centre fans (local, proportioned) rather than fanned from a boundary vertex, following R03.
- Unreal preset uses Blender default axes and FBX_SCALE_NONE; unverified in Unreal, labelled NOT RUN.

## Verification / tests and observations

| Check | Method/command/environment | Result | Evidence and limitations |
| --- | --- | --- | --- |
| Build Baby/Adult/Leader | `blender -b --python <shape>.py --python finalize_export.py -- art/models/Lamb --unreal`, Blender 4.2.23 LTS | PASS | 6,824 / 7,936 / 7,992 evaluated triangles |
| Fresh reopen, 16 checks each | `blender -b <file> --python-exit-code 1 --python verify_blend.py` | PASS | 16 PASS, 0 FAIL for each file (file size, budget, no n-gons, UVs inside 0–1, Mask, scale applied, selection, collections, overlays/Extras in 10 3D Views, Mouth child) |
| Verification fails correctly | same with budget argument `100` | PASS | exit code 1 |
| Unity import | — | NOT RUN | no Unity in this environment |
| Unreal import | — | NOT RUN | no Unreal project |
| Shader Editor visual inspection (R01) | — | NOT RUN | headless; nodes laid out programmatically with frames |
| Blender 5.2 run | — | NOT RUN | owner's desktop version; to be confirmed by the owner |
| UV quality (stretch/seams) | — | NOT RUN | only existence/range checked; checker inspection pending |

## Review notes / limitations and follow-up

- Leader is at 7,992 / 8,000 triangles; the next accessory must reduce wool or primitive resolution first.
- Next measurable objective: import Lamb FBX into Unity, confirm facing/scale/vertex colours and decide the outline method.

## User feedback

- **Pending; this does not mean accepted.**

## Skill update

- 2026.09.011 -> 2026.09.011-ks.1. Rules R02, R03, R04, R07, R11 changed; R12 added; project-profile rule added. Basis: owner instructions KS-01..KS-08 (2026-10-12).
- English and Traditional Chinese copies updated in the same change (SKILL, glossary, request template, CLAUDE.md, art profile).
- Next trial: the Lion Baby should be produced with this process (first-execution recap, profile reuse, scripts + verified `.blend`).
