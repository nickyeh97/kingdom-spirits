# Worklog — 2026-10-21 — 004 Unity "Blender preview" render mode

- Time / timezone: 2026-10-21, Asia/Taipei
- Asset / project: kingdom-spirits — engine shader `SpiritBeast/PaletteMask`, `RenderStyle`
- Skill version: 2026.09.011-ks.1 (unchanged)
- Work type: production (engine side) / verification
- Status: code complete; Unity verification NOT RUN (no Unity in the assistant environment). Owner check pending.
- Related: worklog 2026-10-20_001 (URP toon shader).

## Context / user request

Faithful English summary (2026-10-21): "Changes to the Dove wait for feedback. First, set up a render so that what I see in Unity matches the lighting and rendering of the images you show me from the cloud container, and let me switch manually between render modes."

## Confirmations / known and unknown

- The review renders use Cycles (Blender 4.2.23) with a sun of strength 3 at (50°, 0, −30°), a world colour (0.55, 0.60, 0.65) at strength 0.6, and the default AgX view transform.
- Measured in Cycles (EXR, white plane): sun strength 3 → 0.9527 (Diffuse) / 0.9541 (Principled, roughness 0.8), i.e. S/π; white world strength 1 → 0.998. So Lambert + unoccluded ambient reproduces the direct terms within 0.2 %.
- Background pixel after AgX: sRGB (151, 155, 159).
- AgX cannot be matched by a formula reliably, so a 32³ LUT was rendered by Cycles itself (emission plane, orthographic camera, 1 sample, no denoising). Checked against six direct Cycles renders (greys and saturated colours): identical 8-bit values. A first check disagreed by up to 25 levels; the cause was Cycles denoising on the tiny test images, not the LUT.
- Known remaining differences: no bounce light or ambient occlusion in Unity (crevices slightly lighter); different camera lens and framing.

## Scope / actions and implementation

- Shader: global `_SpiritStyle` (0 toon, 1 Blender preview). Preview path: Lambert × main light × shadow attenuation + `_SpiritAmbient`, then the AgX LUT (log2-encoded input 2^-12–2^4), converted back to linear for the sRGB framebuffer. Outline hidden in preview mode. New `ShadowCaster` pass; main-light shadow keywords in the forward pass.
- `Assets/Runtime/RenderStyle.cs`: switches the global, the sun (direction, intensity 3/π, white, soft shadows), the ambient and the camera background; restores the scene's own light and background in toon mode, where the light casts no shadows. Remembered in PlayerPrefs. Resets to toon when Play mode ends.
- Buttons "渲染：卡通 / Blender 預覽" in the offline demo and the palette preview. The real game (GameApp) always uses toon.
- URP asset: main-light shadows and soft shadows allowed, shadow distance 8 (only used when the light casts shadows, i.e. preview mode).
- `Assets/Resources/Shaders/AgX_Lut.png` + `AgxLutImporter` (linear, uncompressed, clamp, bilinear, no mipmaps).
- `Tools/bake_agx_lut.py` (reproduces the committed LUT exactly) and `Tools/render_preview.py` (the review render script, now in the repo as the reference).

## Verification / tests and observations

| Check | Method/command/environment | Result | Evidence and limitations |
| --- | --- | --- | --- |
| LUT equals Cycles AgX | 6 colours, Cycles emission vs LUT entry, 8-bit | PASS | identical values |
| Bake script reproduces LUT | `Tools/bake_agx_lut.py`, decoded pixel compare | PASS | pixel data identical (PNG metadata differs) |
| Runtime C# compiles | `dotnet build Tools/RuntimeCompileCheck` | PASS | 0 errors, 0 warnings |
| Core tests | `dotnet test Tools/CoreTests` | PASS | 90/90 |
| New UI glyphs in font subset | fontTools cmap | PASS | 渲染卡通預覽 present |
| Shader compiles, visual match in Unity | Unity 6000.3.25f1 | NOT RUN | owner to compare the palette preview (Blender mode, p8, rotation stopped) with a review render |

## User feedback

- Pending; this does not mean accepted.
