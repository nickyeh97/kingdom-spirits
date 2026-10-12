# blendsmith glossary

Version: **2026.09.011-ks.1**. Traditional Chinese reading copy: [glossary.zh-TW.md](glossary.zh-TW.md). Update both in the same change.

This glossary is written for someone learning 3D modelling. Each entry tries to answer four things:

- **What it is** — in one sentence.
- **Why it matters** — what goes wrong if you ignore it.
- **Lamb example** — what actually happened while building the lamb in `art/blender/`.
- **Where in Blender** — where to find or do it.

Rule IDs (R01–R12) refer to [SKILL.md](../SKILL.md).

---

## 1. Process and documents

**Reference**
- What: photos, drawings, real objects or specifications the model is based on.
- Why: without references, proportions and details are guesses, and wrong guesses mean rebuilding. R04 asks to separate visible facts from inference.
- Lamb: the real sheep photo showed a white face framed by wool and ears sticking out horizontally from the wool.

**Occluded structure**
- What: parts the references do not show, such as an animal's underside or a product's interior.
- Why: unseen is not the same as unneeded. R04 asks to decide per part: full, simplified or omitted.
- Lamb: no wool under the belly (`d.z < -0.35` is skipped) because the game camera never sees it and it saves triangles.

**Production brief**
- What: the written specification before work starts: purpose, dimensions, budgets, UVs, materials, rig, deliverables.
- Why: everyone needs the same definition of "done". Template: `assets/production-brief.template.md`.

**Recap (R04)**
- What: restating the whole request in the user's language and asking for confirmation before building.
- This project: a full recap only at the first production of each new asset; later feedback-driven adjustments need only a one- or two-sentence note.

**Detail tier (low / medium / high)**
- What: low, medium or high detail. There are no universal numbers; it depends on use and camera distance.
- Lamb: a mobile Web game showing one spirit beast at a time, so the budget is at most 8,000 triangles for adult forms.

**Budget**
- What: an agreed upper limit, e.g. triangle count, texture size, material count.
- Why: phones have limited performance and download size; going over budget slows loading and frame rate.

**Worklog (R05)**
- What: a record after each work session: request, actions, verification, results, feedback.
- Why: it lets another session or computer continue. In this project: `docs/art-worklog/`, in English.

**Feedback register**
- What: user feedback turned into reusable rules, in `references/feedback-register.md`.
- Lamb: "wool lobe spacing / radius of about 2.4 keeps the scalloped grain" and "horns grow outside the head" are recorded there for the lion.

**Deliverable / handoff**
- What: the files handed to the next person (the user, animation, Unity) and the state that lets them continue.
- This project (R11): generation scripts (source, for learning) + a verified versioned `.blend` + engine FBX.

**Versioned filename**
- What: a new filename for each output, e.g. `Lamb_Adult_v003.blend`, never overwriting the old one.
- Why: you can compare against earlier versions, and feedback refers to a specific version.

**PASS / FAIL / NOT RUN / N/A**
- What: the four ways to report a check.
- Why: a check that was not run must not be reported as passed. Without an actual Unity import, write NOT RUN, not "should be fine".

**Fresh reopen**
- What: after saving, open that exact file in a new Blender process and check again.
- Why: some things live only in memory and never reach the file (e.g. a wrong external texture path). Only a reopen proves the file itself.

---

## 2. Shape and objects

**Silhouette**
- What: the outline you see when the model is filled solid black.
- Why: on a small phone screen people recognise characters mostly by silhouette. NPR mode depends on it.
- Lamb: big head, ears, fluffy wool and curled horns read as a sheep in pure black.

**Proportion / head-to-body ratio**
- What: relative sizes of parts.
- Lamb: about 1:1 for the baby and 1:2 for the adult. A bigger head reads as younger — the main "cute" control.

**Blockout / clay**
- What: the stage that fixes proportions with simple shapes, before detail; clay means viewing it untextured in grey.
- Lamb: the two spheres of lesson 1.

**Primary / secondary / tertiary forms**
- What: overall outline, main undulations, small details.
- Why: get primary right, then secondary, then a few tertiary details. Skipping to details produced the first "bunch of grapes" wool.

**Origin / pivot**
- What: the object's own centre; move, rotate and scale use it.
- Why: games align characters to the ground by their origin; the mouth's origin at its centre lets it open from the middle.
- Where: the small orange dot; Object → Set Origin.

**Transform: Location / Rotation / Scale**
- What: how an object is placed in space, without changing the mesh itself.
- Where: `N` panel, Item tab.

**Apply transform**
- What: bake scale and rotation into the mesh so the values return to 1 and 0, with no visible change.
- Why: non-uniform scale (different X/Y/Z) distorts children, breaks normals and confuses rigs. Apply before engine export.
- Where: `Ctrl+A` → Rotation & Scale.

**Parent / child, hierarchy**
- What: a child follows its parent but can still move itself; it stores its position relative to the parent.
- Lamb: Mouth is a child of the body — it goes where the body goes but can still open.
- Where: select child, then parent, `Ctrl+P`.

**Collection**
- What: a folder in the Outliner for grouping objects.
- Lamb: the early wool puffs lived in a Wool collection so they could be hidden together.

**Instance**
- What: several objects sharing one mesh; editing one changes all.
- Why: repeated parts (e.g. identical buttons) use less memory and are easier to change.
- Where: `Alt+D` duplicates as an instance (`Shift+D` is an independent copy).

**Modifier / modifier stack**
- What: effects layered on a mesh (decimate, thicken, wrap), evaluated top to bottom.
- Why: until applied the original mesh is untouched ("non-destructive"); order changes the result.
- Where: the wrench tab.

**Base mesh vs evaluated geometry**
- What: the base mesh is what you edit; evaluated geometry is the result after all modifiers.
- Why: R03 checks both. A final Triangulate modifier can hide n-gons that still exist in the base mesh.

**Procedural / generative source**
- What: the program or rules that generate a model, e.g. our `lamb_*.py`.
- Why: change a number and rebuild; reuse the rules for new animals. Keep its role distinct from the delivered `.blend` and FBX.

**Metaball**
- What: each element is a field; fields add up and the surface is drawn where the sum equals the threshold, so nearby elements fuse.
- Lamb: wool, hood and neck. Measured surface size is 0.574 x the set radius (stiffness 2), so scripts divide by that factor.
- Key settings: Threshold, Radius, Stiffness (higher = crisper edge), Negative (subtracts nearby volume).

**Curve + bevel**
- What: a path given thickness becomes a tube; each point's radius scales the thickness there.
- Lamb: horns, the smiling mouth, the cape's gold cords.

**Shrinkwrap**
- What: pushes a mesh's points onto another object's surface.
- Lamb: the cape. `OUTSIDE` mode only pushes points that are inside the target, so the draft must start smaller than the body.

**Solidify**
- What: gives a thin sheet thickness.
- Lamb: cape and collar.

**Decimate**
- What: reduces faces automatically; Collapse merges where the shape changes least.
- Lamb: wool from about 20,000 to 2,300–3,000 triangles.

**Boolean**
- What: add, subtract or intersect one object with another, e.g. to cut a hole.
- Caution: results often have messy topology; R03 requires cleanup before delivery.

---

## 3. Topology

**Vertex / edge / face**
- What: the three mesh elements. Vertices form edges; edges bound faces.
- Where: in Edit Mode, `1` / `2` / `3` switch selection type.

**Triangle / quad / n-gon**
- What: faces with three, four, or five or more vertices.
- Why: engines split everything into triangles; n-gons split unpredictably and shade badly. R03: no n-gons in delivered meshes.
- Lamb: default cylinder and cone caps are n-gons; the finalize script turns them into small centre fans.

**Face count vs triangle count**
- What: one quad is one face but two triangles.
- Why: always state which you mean. This project's budgets use triangles.

**Topology**
- What: how vertices, edges and faces connect — separate from the outer shape. The same shape can have good or bad topology.
- Why: good topology is easy to edit, deforms naturally and shades smoothly.

**Edge loop / edge ring**
- What: a chain of edges going around (loop) or a band of parallel edges (ring).
- Why: bending areas (joints, mouth corners) need loops to deform cleanly.
- Where: `Alt+click` in Edit Mode.

**Edge flow**
- What: edges following the direction of the form and muscles.
- Why: good flow avoids creases and dents when subdividing or deforming.

**Pole**
- What: a vertex with a number of edges other than four (3, or 5+).
- Why: poles cause shading artefacts; place them where they are hidden and do not deform. A UV sphere's tips are poles.

**Triangle fan**
- What: many triangles sharing one vertex, like a fan.
- Why: R03 forbids long fans from one boundary vertex (slivers, bad shading). A small fan from the centre of a small cap is much less harmful.

**Sliver triangle**
- What: a very thin, long triangle.
- Why: shading and bake errors, wasted triangles.

**Grid fill / O-grid**
- What: filling a circle or hole with an ordered quad grid inside a ring.
- Why: R03's preferred way to build round caps and openings.

**Manifold / non-manifold**
- What: manifold means closed like a balloon with no holes. Non-manifold means holes, an edge shared by three or more faces, or faces touching only at a point.
- Why: needed for 3D printing and some operations; but sheets like a cape are legitimately open, so R03 judges case by case.

**Open boundary**
- What: edges used by only one face — the mesh's edge or a hole.

**Duplicate faces / zero-area faces / loose vertices**
- What: overlapping faces, faces with no area, vertices attached to nothing.
- Why: flicker, bake errors, waste. Clean before delivery.
- Where: Edit Mode → Mesh → Clean Up; Merge by Distance.

**Self-intersection / interpenetration**
- What: faces passing through each other.
- Lamb: parts intentionally overlap (legs into body) to avoid visible seams — common for low-poly characters — as long as nothing pokes out visibly.

**Subdivision**
- What: splitting every face into smaller faces to make the surface smoother.
- Why: it magnifies bad topology.

**Retopology**
- What: drawing a new clean, low-poly mesh over a high-poly surface.
- Lamb: replaced by Decimate because the shapes are cartoon and barely deform; joints may need manual retopology once rigged.

**High poly / low poly**
- What: many faces with detail, used for baking; few faces, used in the game.

**LOD (level of detail)**
- What: several versions of a model at decreasing triangle counts for increasing distance.
- This project: one beast at a fixed distance, so no LODs for now.

**Deformation**
- What: bending and squashing when driven by a rig.
- Why: deforming areas need loops; rigid parts can be very cheap.

**Triangulation / evaluation diagonal**
- What: a quad can be split along either diagonal.
- Why: different splits shade differently; bake and game must use the same split or normal maps break.

---

## 4. UVs

**UV / UV map**
- What: a table that flattens the 3D surface onto a 2D plane, telling the renderer which texture pixel each surface point uses. U and V are the 2D axes (X/Y are taken by 3D).
- Why: no UVs, no textures. R03: every mesh has UVs, in NPR and PBR modes.
- Lamb: colours use vertex colours today, but the growth pattern must be painted across the wool, which needs UVs.

**Unwrap**
- What: creating UVs, like flattening a cardboard box.
- Where: Edit Mode, select all → `U` → Unwrap or Smart UV Project.

**Seam**
- What: an edge cut open during unwrapping.
- Why: textures break at seams; hide them (underarms, back).

**UV island**
- What: a connected piece of the unwrapped layout.

**Stretch / distortion**
- What: areas stretched or squashed when flattened, distorting the texture.
- Check: apply a checker texture; squares should be square and even.

**Overlap**
- What: islands on top of each other share texture pixels.
- Why: non-overlapping is the default (bakes fail otherwise). Deliberate overlap (e.g. mirrored halves) is confirmed and recorded.

**Mirrored / stacked UVs**
- What: left/right halves or repeated parts stacked to save texture space.
- Cost: both sides are identical; no unique baked lighting.

**Texel density**
- What: texture pixels per unit of surface.
- Why: uneven density means sharp here, blurry there. Important areas like the face may get more.

**Padding / margin**
- What: space between islands and colour extended past island edges.
- Why: when a texture is shrunk (mipmaps), neighbouring islands bleed into each other; too little padding shows coloured seams.

**0–1 space**
- What: the unit square of UV space that maps to one whole texture.

**Atlas / UV sheet**
- What: several parts sharing one texture layout.
- Note: number of atlases is not the number of channels; one atlas can have BaseColor, Normal and more.

**Square resolution, power of two**
- What: textures at 512, 1024, 2048... with equal width and height.
- Why: most efficient for GPU compression and mipmaps. This project: at most 1024², pattern mask at most 512².

**UDIM**
- What: UVs spread over many tiles (1001, 1002...), each with its own texture.
- Use: high-resolution film assets; rarely needed for mobile games.

**Lightmap UV**
- What: a second, fully non-overlapping UV set used by the engine to bake static lighting.
- Why: needed by Unreal for static lighting; Unity can generate one on import (R12).

**Smart UV Project**
- What: Blender's automatic unwrap that cuts seams by face angle.
- This project: the finalize script uses it for every mesh; refine seams by hand when painting detailed patterns.

---

## 5. Materials and shading (both modes)

**Material / shader**
- What: settings that decide how a surface looks; the shader is the program computing colour and light.
- Why: the same mesh can look plastic, metal, realistic or cartoon depending on the material.

**Material slot / draw call**
- What: an object can have several materials; each usually costs one GPU draw call.
- Why: fewer draw calls run better on phones, hence the single-material rule in the GDD.

**Shader Editor / node**
- What: the editor that builds materials from boxes and wires; each node does one thing.
- R01: left to right (coordinates → textures → adjustments → BSDF → output), framed, named, not overlapping.
- Where: Shading workspace, lower half.

**Node group, Frame, Reroute**
- What: a group packs nodes into one; a frame is a labelled area; a reroute bends wires neatly.

**Texture Coordinate → Mapping → Image Texture**
- What: the standard texture chain: get coordinates (usually UV), transform them with Mapping, then read the image.
- R01: every image goes through Mapping; aligned channels share one Mapping.
- Where: with the Node Wrangler add-on, `Ctrl+T` on an image node builds it.

**Colour space: sRGB / Non-Color / Linear**
- What: how numbers are interpreted. sRGB is colour for human eyes; Non-Color is raw data.
- Why: BaseColor uses sRGB; Normal, Roughness, Metallic and masks use Non-Color. A wrong setting silently changes values.
- Lamb: the re-imported FBX converted fixed colours, making ivory look darker — this is why.

**Vertex colour / colour attribute**
- What: colour stored directly on each vertex (or face corner), no texture needed.
- Lamb: the `Mask` attribute.

**Mask**
- What: data that marks regions rather than final colour.
- Lamb: with A=1, R/G/B mean primary/secondary/accent; with A=0, RGB is a fixed colour. Lining uses 0.45, i.e. 45% of the slot colour.

---

## 6. PBR mode

**PBR (physically based rendering)**
- What: computing how light reflects and absorbs using rules close to real physics.
- Why: a material looks plausible under any light — the standard for realistic games and film.

**BSDF / Principled BSDF**
- What: a function describing where light scatters after hitting a surface. Principled BSDF is Blender's all-in-one PBR node.
- "Full BSDF thinking": describe materials with colour, roughness, metalness and normals, not painted lighting.

**BaseColor / albedo**
- What: the surface's own colour, **without lighting, highlights or shadows**.
- Common mistake: using a photo directly freezes its lighting into the colour.

**Normal map**
- What: an RGB image storing the surface direction per pixel, faking bumps without adding faces.
- Tangent space: the common type, relative to the surface, so it survives deformation.
- OpenGL / DirectX: opposite green channels. Blender and Unity use OpenGL (Y+); Unreal uses DirectX (Y−) — flip green or set it on import.
- Use Non-Color and a Normal Map node.

**Roughness**
- What: 0 is mirror-smooth, 1 is fully matte.
- Tip: subtle roughness variation (fingerprints, wear) sells realism more than colour variation.

**Metallic / metalness**
- What: whether a surface is metal; usually 0 or 1, with in-between values only at transitions such as rust edges.
- R02: a fully non-metal object may ship an all-black (Metallic=0) map.

**ORM channel packing**
- What: Occlusion, Roughness and Metallic stored in the R, G, B channels of one image.
- R02: keep the four editable source maps even when the engine wants ORM.

**Emission, alpha**
- What: self-illumination; transparency.
- R02: an alpha channel may carry an emission mask but must not automatically drive transparency.

**Displacement / height / bump**
- What: displacement moves vertices and changes the silhouette; bump and normal only change shading.

**Transmission, subsurface, coating / clearcoat**
- What: light through glass; light scattering inside skin or wax; the glossy layer on car paint.

**Procedural material**
- What: a material computed from mathematical nodes (noise, gradients), not images.
- Why: easy to tweak, but engines cannot read Blender nodes, so it is baked to images for delivery.

**Bake**
- What: saving a computed result into an image.
- Distinguish (R02): same-geometry material bake (procedural → image) versus high-to-low projection (high-poly detail onto a low-poly normal map).

**Cage / ray distance**
- What: in high-to-low baking, rays are cast from a slightly inflated low mesh (the cage) to find the high surface.
- Wrong settings: rays hit neighbouring parts or miss, giving holes or wrong detail.

**Bake proxy**
- What: a copy of the mesh prepared only for baking (e.g. parts separated to avoid cross-projection).
- R02: the proxy must keep the same normals and triangulation as the delivered mesh.

**Tangent basis**
- What: the per-point surface coordinate frame used to read a normal map.
- Why: a different basis at bake and display time causes strange shading.

---

## 7. Smoothing and normals

**Normal**
- What: the direction a surface faces at a point; shading uses the angle between normal and light.
- Lamb: in lesson 2 the eyes were rotated 22° so they matched the face's normal.

**Shade Smooth / Shade Flat**
- What: smooth averages neighbouring normals for a rounded look; flat gives each face one direction so facets show.
- Note: shading only; triangle count does not change.
- Where: right-click an object → Shade Smooth / Shade Flat.

**Auto Smooth / Smooth by Angle**
- What: edges below an angle shade smooth, above it stay sharp.
- Why: hard-surface objects need flat faces with crisp edges while curves stay smooth.

**Sharp edge / hard edge**
- What: an edge marked as not smoothed.

**Split normals / custom normals**
- What: one vertex can have different normals on different faces, keeping both sides of a sharp edge correct; custom normals are set by hand.
- NPR: split normals open gaps in normal-extruded outlines, so a separate smoothed outline normal is needed.

**Weighted Normal**
- What: area-weighted normals that keep large faces flatter.
- R02: optional polish; it does not replace deciding where edges are sharp.

---

## 8. NPR / toon mode

**NPR (non-photorealistic rendering)**
- What: styles that deliberately avoid realism: cartoon, hand-drawn, watercolour.
- This project: the spirit beasts use NPR toon mode (see `art/ART_PROFILE.md`).

**Toon shading / cel shading**
- What: continuous shading cut into a few hard-edged bands, like animation cels.
- Why: clean, cute, readable and cheap to render.

**Ramp / bands**
- What: the lookup that decides which brightness becomes light or shadow, usually 2–3 bands.
- Where: Color Ramp node with interpolation Constant.

**Shader to RGB**
- What: an EEVEE-only node that turns the lit result into a colour so a Color Ramp can band it. Cycles does not have it.

**Toon thinking**
- What: express the character through shape and flat colour regions rather than detail and painted lighting; spend triangles on the silhouette and let the engine make the bands.

**Outline**
- What: the dark line around a cartoon character. Three common methods:
  - **Inverted hull:** a slightly inflated copy with flipped normals, drawing only back faces, so it shows as a rim. In Blender: Solidify (Flip Normals) plus backface culling.
  - **Shader pass:** an extra pass in the shader pushing vertices out along normals; common in Unity URP.
  - **Post-process edge detection:** after the frame is rendered, find edges from depth/normal changes and draw lines; common in Unreal.
- Why: without an outline, cartoon characters blur into the background.

**Back-face culling**
- What: not drawing faces that point away from the camera. Inverted-hull outlines depend on it.

**Averaged / smoothed outline normals**
- What: normals at the same position averaged into one direction, stored in a vertex colour or spare UV channel for the outline only.
- Why: prevents outline gaps and spikes at sharp edges and part joins.

**Freestyle**
- What: Blender's built-in line renderer for drawing lines at render time. Blender-only, so it is just a preview for games.

**Palette swap**
- What: changing only colour parameters on the same model to make colour variants.
- Lamb: the eight palettes come from the colour mask plus material parameters, with no new textures.

**Palette texture / gradient atlas**
- What: another NPR colour method: a tiny swatch image, with each part's UVs shrunk onto its colour cell.

---

## 9. Rig and animation

**Rig**
- What: the whole control system that lets a model be posed and animated: skeleton, controls, limits.

**Armature / bone**
- What: an armature is a set of bones; bones move or deform the mesh.
- R10: animator-facing controls are armature bones used in Pose Mode, not Object Mode empties.

**Pose Mode / Edit Mode (armature) / rest pose**
- What: Edit Mode sets bones' original placement; Pose Mode poses and keys them; the rest pose is the default stance.

**Pose bone / control bone vs deform bone**
- What: deform bones move the mesh; control bones are handles that drive deform bones via constraints.

**Custom shape**
- What: makes a control bone display as a circle, arrow etc. R10: display only; the bone is still what you operate.

**Constraint / driver**
- What: a constraint is a rule like "A follows B" or "rotation ≤ 30°"; a driver links one value to another with an expression (lift the cap → the cap rotates).

**Keyframe**
- What: a value recorded at a time; the computer interpolates between keys.
- Where: hover a field and press `I`.

**Transform lock vs selection lock**
- What: a transform lock stops movement on an axis; a selection lock makes the object unselectable.
- R06/R10: use transform locks for limits, but never deliver selection locks.

**Local / world space**
- What: axes relative to the object or to the whole world.

**Weight paint / skinning**
- What: how much each bone influences each vertex.
- This project: the GDD plans one shared quadruped skeleton for lamb and lion, so clean weights let animations transfer.

**Shape key / blend shape**
- What: an alternative mesh shape blended with a slider; good for expressions like blinking or opening the mouth. Unity calls it a Blend Shape.

---

## 10. Delivery and game engines

**.blend**
- What: Blender's native file containing the whole scene.
- This project (R11): deliver a verified versioned `.blend`. Do not put it inside Unity's `Assets/`, or Unity will try to import it through Blender.

**FBX**
- What: the most common 3D exchange format for game engines; Unity and Unreal both support it. Carries mesh, UVs, vertex colours, skeleton, animation.

**glTF / GLB**
- What: an open-standard 3D format common on the web. Unreal 5 imports it directly; Unity needs a package.

**Axis conversion (forward / up)**
- What: Blender is Z-up; Unity is Y-up; Unreal is Z-up with X forward. Exports set matching axes.
- Lamb: faces −Y in Blender; exported with Forward −Z, Up Y it faces forward in Unity.

**Unit scale**
- What: 1 unit is 1 metre in Blender and Unity, 1 centimetre in Unreal.
- Why: a mistake makes models 100 times too big or small.

**Apply transform on export (bake space transform)**
- What: baking the axis conversion into the mesh at export.
- Why: otherwise the root gets an extra −90° X rotation in Unity — a classic beginner trap.

**Smoothing groups**
- What: information telling the engine which faces shade smoothly together.
- Why: export Smoothing as Face so Unreal does not warn about missing smoothing information.

**Vertex colour import**
- What: whether the engine keeps vertex colours. Unity reads them by default; in Unreal set the import option to Replace.

**Import test**
- What: putting the export into the engine to check facing, scale, colours, triangle count, outline.
- R12: without an actual import, record NOT RUN.

**Selection / overlays / Extras (R06)**
- What: in the delivered file every object and collection is selectable, and 3D View overlays and Extras (lights, cameras) are visible.
- Why: whoever opens the file must not find unselectable objects or missing lights.

**Pack / relative path**
- What: packing embeds external textures in the `.blend`; relative paths store textures relative to the `.blend`.
- Why: textures survive moving to another computer. R09 organises textures into object-category folders.

---

## 11. Blender interface

**Object Mode / Edit Mode**
- What: Object Mode works on whole objects; Edit Mode edits vertices, edges, faces. `Tab` toggles.

**Viewport shading: Wireframe / Solid / Material Preview / Rendered**
- What: the four spheres at the top right.
- Lamb: work in Solid with Object colour; after the finalize script, use Material Preview to see the colour mask's real result.

**EEVEE / Cycles**
- What: Blender's two render engines. EEVEE is fast and real-time and supports Shader to RGB (toon); Cycles is path-traced, realistic and slower.

**Workspace / screen**
- What: the Layout, Shading, Scripting... tabs. Each has its own 3D View and settings.
- Lamb: scripts once changed only the Scripting tab's view, so Layout showed no colours.

**Outliner**
- What: the object list at the top right for selecting, renaming, hiding and organising collections.

**Statistics**
- What: enable it in the Overlays menu to show vertex, face and triangle counts at the top left; used for budget checks.
