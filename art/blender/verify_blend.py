# 交付驗證（blendsmith R11）：用「全新的 Blender 程序」重新打開存好的 .blend，逐項檢查。
# 用法：blender -b <檔案>.blend --python-exit-code 1 --python verify_blend.py -- [三角形預算，預設 8000]
# 任何一項 FAIL 都會讓 Blender 以錯誤碼結束，方便在命令列或 CI 判斷。
import bpy, os, sys

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BUDGET = int(ARGS[0]) if ARGS else 8000
results = []

def check(name, ok, evidence):
    results.append((name, "PASS" if ok else "FAIL", evidence))

path = bpy.data.filepath
check("File exists, nonzero size", os.path.isfile(path) and os.path.getsize(path) > 0,
      f"{os.path.basename(path)} {os.path.getsize(path) if os.path.isfile(path) else 0} bytes")

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
check("Mesh objects present", len(meshes) >= 1, ", ".join(o.name for o in meshes))

dg = bpy.context.evaluated_depsgraph_get()
total = 0
for o in meshes:
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    total += len(me.loop_triangles)
    o.evaluated_get(dg).to_mesh_clear()
check(f"Triangle budget <= {BUDGET}", total <= BUDGET, f"{total} evaluated triangles")

for o in meshes:
    me = o.data
    ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
    check(f"{o.name}: no n-gons (R03)", ngons == 0, f"{ngons} n-gons in base mesh")
    uv = me.uv_layers.active
    if uv is None:
        check(f"{o.name}: UV map (R03)", False, "no UV map")
    else:
        coords = [d.uv for d in uv.data]
        finite = all(c.x == c.x and c.y == c.y for c in coords)
        spread = (max(c.x for c in coords) - min(c.x for c in coords)) * (max(c.y for c in coords) - min(c.y for c in coords))
        inside = all(-1e-4 <= c.x <= 1 + 1e-4 and -1e-4 <= c.y <= 1 + 1e-4 for c in coords)
        check(f"{o.name}: UV map unwrapped (R03)", finite and spread > 0.05 and inside,
              f"'{uv.name}', {len(coords)} loops, inside 0-1: {inside}")
    check(f"{o.name}: colour mask attribute", "Mask" in me.color_attributes, ", ".join(a.name for a in me.color_attributes))
    sx, sy, sz = o.scale
    check(f"{o.name}: scale applied", abs(sx - 1) < 1e-4 and abs(sy - 1) < 1e-4 and abs(sz - 1) < 1e-4, f"scale {tuple(round(v, 4) for v in o.scale)}")
    check(f"{o.name}: selectable (R06)", not o.hide_select, f"hide_select={o.hide_select}")

check("Collections selectable (R06)", all(not c.hide_select for c in bpy.data.collections),
      f"{len(bpy.data.collections)} collections")
views = [a.spaces.active for s in bpy.data.screens for a in s.areas if a.type == 'VIEW_3D']
check("Overlays and Extras on in every 3D View (R06)",
      bool(views) and all(v.overlay.show_overlays and v.overlay.show_extras for v in views), f"{len(views)} 3D Views")
mouth = bpy.data.objects.get("Mouth")
if bpy.context.scene.get("has_mouth", True):
    check("Mouth is a separate child object", mouth is not None and mouth.parent is not None,
          f"parent={mouth.parent.name if mouth and mouth.parent else None}")
else:
    results.append(("Mouth is a separate child object", "SKIP", "scene has_mouth = False (recorded deviation)"))
for o in meshes:
    if "albedo" in o:
        img = bpy.data.images.get(o["albedo"])
        check(f"{o.name}: albedo texture packed, <= 1024", img is not None and img.packed_file is not None
              and max(img.size) <= 1024, f"{img.name if img else None} {tuple(img.size) if img else ''}")
    if "pattern" in o:
        img = bpy.data.images.get(o["pattern"])
        check(f"{o.name}: pattern mask packed, <= 512", img is not None and img.packed_file is not None
              and max(img.size) <= 512, f"{img.name if img else None} {tuple(img.size) if img else ''}")

print(f"\nVERIFY {os.path.basename(path)}  Blender {bpy.app.version_string}  built with {bpy.context.scene.get('spirit_built_with')}")
for name, status, evidence in results:
    print(f"{status:5s} | {name} | {evidence}")
failed = [r for r in results if r[1] == "FAIL"]
skipped = [r for r in results if r[1] == "SKIP"]
print(f"SUMMARY: {len(results) - len(failed) - len(skipped)} PASS, {len(skipped)} SKIP, {len(failed)} FAIL")
if failed:
    raise SystemExit(1)
