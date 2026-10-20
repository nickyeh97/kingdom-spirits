# Worklog — 2026-10-20 — 001 URP toon shader and outline

- Asset / project: kingdom-spirits — engine shader `SpiritBeast/PaletteMask` (all beasts)
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production (engine side) / specification
- Status: partial — code complete; Unity verification NOT RUN (no Unity in the assistant environment). Owner check pending.
- Related: `art/ART_PROFILE.md` (outline method, colour conversion); GDD §7.2, §8.1.

## Context / user request

Faithful English summary (2026-10-20): "Postpone the G1 work; start building G2." G2 = art and graphics. First item: move to URP and replace the built-in shader with a toon shader with outline (outline method left open in the profile).

## Confirmations / known and unknown

- Confirmed by profile/GDD: NPR toon + outline, URP, Web build for phones, single material per mesh.
- Decided this round (assistant, owner may adjust): outline = inverted hull; mobile URP asset with HDR and shadows off.
- Resolved open item: fixed-colour conversion. `finalize_export.py` writes `Mask` as `FLOAT_COLOR` (linear values) and exports with `colors_type='LINEAR'`; Unity reads vertex colours without conversion; the project is in Linear colour space. So no conversion is needed and the engine matches the Blender preview. A conversion was briefly added and then removed after reading the export script.
- Unknown: whether outline gaps appear at part joins on the existing Lamb/Lion meshes (needs an in-editor look).

## Scope / actions and implementation

- `Assets/Resources/Shaders/PaletteMask.shader`: rewritten in URP HLSL. Pass 1 `UniversalForward`: same slot × pattern formula, two-band toon light (smoothstep around `_ShadowThreshold`, width `_ShadowSoftness`), warm `_ShadowTint` in shadow, `SampleSH` ambient, `_MinLight` floor. Pass 2 `SRPDefaultUnlit`, `Cull Front`: clip-space normal extrude, `_OutlineWidth` as a fraction of screen height, aspect-corrected, `_OutlineColor` dark brown. `_UseMask = 0` gives a flat `_BaseColor` mode for placeholder parts. `_View` debug modes kept; outline hidden in debug views. Material constants in `UnityPerMaterial` (SRP Batcher).
- `Assets/Runtime/PaletteMaterial.cs`: `Flat(Color)` for placeholder parts. `BeastView` placeholders now use it instead of `Legacy Shaders/Diffuse`.
- `Packages/manifest.json`: `com.unity.render-pipelines.universal` 17.3.0.
- `Assets/Editor/RenderPipelineSetup.cs`: creates `Assets/Settings/SpiritBeast_URP.asset` + renderer on first open and sets it as the default pipeline; menu item; `Build.Web` calls it.
- No Blender file was modified.

## Files / versions

| File | Action | Version/purpose |
| --- | --- | --- |
| Assets/Resources/Shaders/PaletteMask.shader | rewritten | URP toon + outline |
| Assets/Runtime/PaletteMaterial.cs, BeastView.cs | changed | flat mode for placeholders |
| Assets/Editor/RenderPipelineSetup.cs | new | URP asset setup |
| Packages/manifest.json | changed | URP package |
| art/ART_PROFILE.md, .zh-TW.md | changed | outline decision, colour conversion resolved |
| docs/DEVELOPMENT.md | changed | URP setup and shader parameters |

## Decisions / concise rationale and tradeoffs

- Inverted hull over a post-process edge pass: works on WebGL2 without a depth/normals texture, costs one extra draw per mesh, and matches the "thin outline" look. Hard edges can split the hull; first fix is smoothing normals in Blender, baked outline normals only if needed.
- Screen-space width: constant thickness for the single on-screen beast at any zoom.
- Shadows off: toon bands come from N·L; cast shadows add cost on phones and are not part of the style.

## Verification / tests and observations

| Check | Method/command/environment | Result | Evidence and limitations |
| --- | --- | --- | --- |
| Runtime C# compiles | `dotnet build Tools/RuntimeCompileCheck` | PASS | 0 errors, 0 warnings; Editor scripts are not covered |
| Core tests | `dotnet test Tools/CoreTests` (TZ=Asia/Taipei) | PASS | 90/90 |
| Shader compiles in Unity | Unity 6000.3.25f1 | NOT RUN | needs the owner's editor |
| Visual look, outline gaps | Palette preview on Lamb/Lion | NOT RUN | needs the owner's editor |

## Review notes / limitations and follow-up

- Owner to open the project, let URP set up, commit `Assets/Settings/*` and `ProjectSettings/GraphicsSettings.asset`, then check the palette preview.
- No DepthOnly/ShadowCaster passes (not needed with depth texture and shadows off).
- Next measurable objective: outline visible and unbroken on all six meshes in the palette preview; no pink materials.

## User feedback

- Pending; this does not mean accepted.
