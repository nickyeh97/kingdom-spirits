# CLAUDE.md

Guidance for Claude Code (and every AI collaborator) working in this repository. **This English file is authoritative**; [CLAUDE.zh-TW.md](CLAUDE.zh-TW.md) is the Traditional Chinese reading copy of the same version. Update both in the same change; if they differ, English governs.

## Language conventions

- **Conversation** with the user is in **Traditional Chinese** (Taiwan usage).
- **English originals with Traditional Chinese copies:** `CLAUDE.md`, skill rules and their supporting documents, templates, and the art profile (`art/ART_PROFILE.md`). When an English original changes, update its `*.zh-TW.md` copy in the same change. Art worklogs are English only.
- Other project documents (`docs/GDD.md`, `docs/PROGRESS.md`, `docs/DESIGN_PRINCIPLES.md`, `docs/ART_PIPELINE.md`, `docs/DEVELOPMENT.md`) and commit message bodies stay in Traditional Chinese.
- Code identifiers (classes, methods, fields, asset file names) are English; comments may be Chinese (Blender shape-script comments stay Traditional Chinese for learning).

## Project overview

**Kingdom Spirits (小領袖靈獸, kingdom-spirits)** — the digital version of the "service record card" for the Kingdom Leaders children's ministry (Unity 6, built for Web so it opens in a phone browser).
Part of the TBOJ (The Book of James) faith-practice programme; the ministry platform lives in [`nickyeh97/kingdom-little-leaders`](https://github.com/nickyeh97/kingdom-little-leaders), the programme in [`nickyeh97/TBOJ`](https://github.com/nickyeh97/TBOJ).

Every child has their own spirit beast that grows with the child's real service: after a parent sees the paper service card signed by a teacher, they record one service in the game → that item's level +1 → the beast celebrates and evolves when it crosses a threshold → an encouragement the parent wrote in advance appears.

> Full design: `docs/GDD.md` (the requirements baseline; read before development).

### Kingdom Leaders children's vision (core of the programme, highest level)

> **Raise little leaders of God's kingdom who live out the Father's good plan.**

1. **Self-image:** assurance of being the Father's child — so **the beast exists from day one**; it is not earned by serving.
2. **Character:** encouragement is rooted in Scripture and the fruit of the Spirit; no comparison, no guilt.
3. **Living the plan:** accumulated service is visible (item levels, beast stage), but compared only with oneself.

## Highest rules (read before development)

`docs/DESIGN_PRINCIPLES.md` is this repository's **highest rule set** (shared with the platform and TBOJ); every design must pass it first. Watch these especially for a game:

1. **No comparison** (red light #1): only the child's own beast is ever on screen; no rankings, showcases or sharing others.
2. **No retention mechanics** (red light #2): no daily login, streaks, hunger/decay, countdowns or push notifications. **The beast never de-evolves and is never sad because the game was not opened.**
3. **No random rewards, in-app purchases or ads** (red lights #3, #4).
4. **Time-on-app is not a metric** (red light #5): opening for 3 minutes and closing is correct use.
5. **Minimal child data** (red light #6): only the minimum the platform already has; no analytics or third-party SDKs.
6. **No shaming** (red light #7): level 1 (not yet served) is not "weak"; unexplored items are "waiting for you", not "missing". **Never show "N more to the next stage".**
7. If a design conflicts with the rules: **stop and raise it for discussion**; no shortcuts.

## Relationship with the ministry platform (division of work)

- **Text input on the platform, touch interaction in the game** (mobile Chinese input in Unity Web is poor).
- One copy of data: the platform's Supabase (`service_card_entries`, `beast_profiles`); the game calls REST directly with the parent's access token. **RLS is the security boundary**; role checks in the game are only UX.
- Auth handoff: the platform opens the game with the fragment `#at=<access_token>&child=<child_id>`; only the access token is passed, never the refresh token; when it expires, reopen from the platform.
- The service-item dictionary reuses the platform's `child_service_items`; the game keeps no list of its own.
- Always name it `gathering` (聚會日); copy says 「聚會日」, never 「主日」. The church meets on Saturday afternoons and not on a fixed weekday — **never hard-code Sunday / 週日**.

## Technology choices (decided)

| Layer | Choice |
| --- | --- |
| Engine | **Unity 6000.3.25f1 (Unity 6.3 LTS)**, target **Web**; URP + simple toon shader introduced in G2. No beta versions (no CI image) |
| UI | UGUI + TextMeshPro (static font atlas, Noto Sans TC subset) |
| Data | UnityWebRequest → Supabase REST; JSON via Newtonsoft |
| Tests | Core logic in `SpiritBeast.Core` without UnityEngine dependencies; the same NUnit tests run in `dotnet test Tools/CoreTests` (no licence needed) and in the Unity Test Framework (EditMode) |
| Command line | Unity CLI (`unity install …`) installs the editor; Editor `-batchmode` builds and tests (commands in `docs/DEVELOPMENT.md`) |
| Hosting / CI | Vercel or Cloudflare Pages static site; GitHub Actions (game-ci) |

### Hard constraints (mobile Web)

- Web build **≤ 30 MB** compressed (leader decision 2026-10-29; was 15 MB); first load on 4G ≤ 10 s.
- Only one beast in the scene; adult ≤ 8k triangles, textures ≤ 1024², single material.
- Portrait, one-handed, buttons ≥ 44 pt; **no text input anywhere in the game**.

### Art boundary

Reference Palworld's **style vocabulary** (rounded low poly, big-head proportions, cel shading, cute expressions), but **never copy any Palworld character's shape, name, palette or signature features**. Beasts are original, based on biblical animals, and **names always display in English** (Lamb, Dove, Lion; later Deer, Eagle, Fish). All assets must be original or properly licensed.

### 3D models (Blender)

- Every 3D-model task uses `.claude/skills/blendsmith` (a modified blendsmith, GPL-3.0-only; changes listed in its `NOTICE.md`) and first reads the art profile `art/ART_PROFILE.md` (style mode: NPR toon + outline; Unity primary, Unreal secondary; budgets, colour mask, delivery locations).
- Deliverables = shape scripts (`art/blender/`, the source, for learning) + versioned `.blend` and FBX verified by a fresh reopen (`art/models/`). Verify with `art/blender/verify_blend.py`.
- Art worklogs go in `docs/art-worklog/` (English). Terms are explained in `.claude/skills/blendsmith/references/glossary.zh-TW.md`.
- The alternative routes researched earlier (AI prompt generation, buying assets) are in `docs/ART_PIPELINE.md`.

## Repository layout

```
README.md                              # project intro and required-reading index (no dev setup)
CLAUDE.md                              # AI collaboration guide (English original)
CLAUDE.zh-TW.md                        # Traditional Chinese reading copy
.claude/skills/karpathy-guidelines/    # coding-behaviour skill (think first, simple first, surgical edits, goal-driven)
.claude/skills/blendsmith/             # 3D model production skill (modified blendsmith, GPL-3.0-only)
art/ART_PROFILE.md                     # art profile (English original + .zh-TW.md copy)
art/blender/                           # procedural shape scripts, finalize/export, delivery verification
art/models/                            # delivered versioned .blend and FBX (not inside Assets/)
docs/DESIGN_PRINCIPLES.md              # highest rules (shared with the platform; required reading)
docs/GDD.md                            # game design and development specification (requirements baseline)
docs/ART_PIPELINE.md                   # art production research (AI prompt → Blender; buy assets if poor)
docs/DEVELOPMENT.md                    # dev guide: Unity version, command-line tests/builds, CI secrets, Vercel deploy
docs/PROGRESS.md                       # progress overview (single source of truth; update at every sprint end)
docs/art-worklog/                      # art worklogs (English)
Assets/Core                            # pure C# core logic (testable): rules, catalog data, REST requests and JSON parsing
Assets/Resources                       # supabase.json (public settings), Fonts/ (Chinese font subset + OFL), Shaders/
Assets/Art/Resources/Beasts            # beast models in Unity: <EnglishName>_<Baby|Adult|Leader>.fbx (+ _Pattern.png)
Assets/Runtime                         # MonoBehaviours: screens, animation, Supabase client
Assets/Editor                          # command-line build script (SpiritBeast.Editor.Build.Web)
Assets/Plugins/WebGL                   # jslib: takes the auth fragment from the page
Assets/Tests/EditMode                  # core logic unit tests (NUnit only)
Assets/WebGLTemplates                  # custom index.html (reads auth fragment, clears address bar, loading screen)
Tools/CoreTests                        # dotnet test project compiling Assets/Core + Assets/Tests, no Unity licence
Tools/RuntimeCompileCheck              # compiles Core + Runtime against UnityEngine reference assemblies, no Unity licence
Tools/subset-font.py                   # regenerates the Chinese font subset
Tools/fbx_mask_report.py               # reads FBX vertex-colour layers; shows the layer Unity actually uses
.github/workflows/ci.yml               # core-tests / unity (licence needed) / deploy (main → Vercel)
```

## Workflow conventions

- **Think before coding:** apply `.claude/skills/karpathy-guidelines` to every code change — state assumptions, prefer simple, touch only what is needed, define verifiable success criteria first.
- **Progress document (mandatory):** `docs/PROGRESS.md` is the cross-session single source of truth for progress; update it at every sprint close, requirement change or completed external setup; read it before starting a new session.
- **Tests:** core rules (levels, stages, evolution, fragment parsing, encouragement selection) **must** have EditMode tests including edge cases; before a PR run at least `dotnet test Tools/CoreTests` and `dotnet build Tools/RuntimeCompileCheck`; when Unity is available also run the EditMode tests and a Web build; CI runs on push/PR.
- **No settings hard-coded in logic:** stage thresholds, palettes, fruits and the scripture pool live in `Assets/Core/Catalog.cs` (Core has no UnityEngine dependency, so both test paths can check them).
- **Regenerate the font subset after adding Chinese UI text** (`Tools/subset-font.py`); otherwise new characters render as boxes on WebGL.
- **Supabase settings** live in `Assets/Resources/supabase.json` (URL + anon key, public values); never put a service role key there.
- **Delivering a beast model to Unity:** copy `art/models/<Species>/<Name>.fbx` (and `textures/<Name>_Pattern.png` if any) into `Assets/Art/Resources/Beasts/`, run `python3 Tools/fbx_mask_report.py` on it (Unity must read the `Mask` layer), and record the source in `Assets/Art/LICENSES.md`.
- **Closing checks (after every implemented requirement):**
  1. Re-run the seven-item checklist in `docs/DESIGN_PRINCIPLES.md` §4.
  2. Run once on a **real phone** with a test account (load time, touch, fonts).
  3. If user-visible behaviour changed → update the parent chapter of `docs/HANDBOOK.md` in the platform repository.
- **Branches:** develop on `claude/*` or feature branches; never push directly to `main`.
- **Commits:** messages mainly in Traditional Chinese, clearly describing what changed and why.
- **Secrets:** the Supabase URL and anon key are public values and may be committed; never commit service keys, tokens or children's personal data. Tests always use fake names.
