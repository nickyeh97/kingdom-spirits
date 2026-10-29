# 骨架與動作的驗證（blendsmith R10）：用全新的 Blender 程序重開存好的 .blend，逐格檢查每個動作。
# 用法：blender -b <檔案>.blend --python-exit-code 1 --python art/blender/verify_rig.py
# 檢查「不要過於異常扭曲、要符合 IK」（組長 2026-10-29）：
#   ⓪ 休息姿勢網格不變形（約束、權重設錯會先變形）
#   ① 腳掌貼地時不滑步：腳掌在地上（離地 < 2 公分）的影格之間，水平位置差 < 1 公分
#   ② 關節不反折：肘、膝只往原本微彎的方向彎（跟休息姿勢的彎曲方向同號）
#   ③ 骨頭旋轉不超過限制：每根骨頭相對休息姿勢的轉角 < 45°（root 除外）
#   ④ 網格不被拉爆：每一格網格的大小（外框）跟休息姿勢比，不超過 ±25%
#   ⑤ 循環動作（Idle）頭尾一致：第 0 格與最後一格的姿勢相同
import bpy, math, sys
from mathutils import Vector

results = []
def check(name, ok, evidence):
    results.append((name, "PASS" if ok else "FAIL", evidence))

rig = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
check("Armature present", rig is not None, rig.name if rig else "none")
body = next((o for o in bpy.data.objects if o.type == 'MESH' and o.parent is rig and o.parent_type == 'OBJECT'), None) if rig else None
check("Skinned mesh parented to the armature", body is not None and any(m.type == 'ARMATURE' for m in body.modifiers),
      body.name if body else "none")
LOOPING = {"Idle", "Sleep"}
FEET = [b for b in ("paw.L", "paw.R", "foot.L", "foot.R") if rig and b in rig.pose.bones]
JOINTS = [(u, l) for u, l in (("upper_arm.L", "forearm.L"), ("upper_arm.R", "forearm.R"), ("thigh.L", "shin.L"), ("thigh.R", "shin.R"))
          if rig and u in rig.pose.bones]
check("IK on every leg", rig is not None and all(any(c.type == 'IK' for c in rig.pose.bones[l].constraints) for _, l in JOINTS) and len(JOINTS) == 4,
      f"{len(JOINTS)} legs")

def bend(u, l):
    """肘／膝的彎曲角（有正負號）：上段與下段在骨架的 YZ 平面（側面）上的夾角。"""
    a = rig.pose.bones[u]; b = rig.pose.bones[l]
    d1 = (a.tail - a.head); d2 = (b.tail - b.head)
    return math.degrees(math.atan2(d1.y * d2.z - d1.z * d2.y, d1.y * d2.y + d1.z * d2.z))

def bbox():
    dg = bpy.context.evaluated_depsgraph_get()
    m = body.evaluated_get(dg).to_mesh()
    pts = [body.matrix_world @ v.co for v in m.vertices]
    body.evaluated_get(dg).to_mesh_clear()
    return Vector([max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)])

if rig and body:
    sc = bpy.context.scene
    rig.animation_data.action = None
    sc.frame_set(0)
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    rest_bend = {l: bend(u, l) for u, l in JOINTS}
    # ⓪ 休息姿勢（沒有動作、約束都開著）網格要跟沒綁骨架時一模一樣：
    #    約束或權重設錯時，還沒動網格就先變形（試做時腳掌整個翻過去，就是這項抓的）
    dg = bpy.context.evaluated_depsgraph_get()
    m = body.evaluated_get(dg).to_mesh()
    moved = max(((v.co - body.data.vertices[i].co).length for i, v in enumerate(m.vertices)), default=0.0)
    body.evaluated_get(dg).to_mesh_clear()
    check("Rest pose leaves the mesh unchanged (< 2 mm)", moved < 0.002, f"max vertex offset {moved * 1000:.2f} mm")
    rest_size = bbox()
    acts = [a for a in bpy.data.actions if a.users or a.use_fake_user]
    check("Clips present", len(acts) > 0, ", ".join(a.name for a in acts))
    for act in acts:
        rig.animation_data.action = act
        f0, f1 = (int(x) for x in act.frame_range)
        planted, worst_slide, worst_rot, worst_bend_flip, worst_size = {}, 0.0, (0.0, ""), [], 0.0
        first_pose = None
        for f in range(f0, f1 + 1):
            sc.frame_set(f)
            pose = []
            for b in FEET:
                p = rig.matrix_world @ rig.pose.bones[b].head
                if p.z < 0.07:                               # 腳掌在地上（休息時腳掌關節約 5 公分高）
                    if b in planted:
                        worst_slide = max(worst_slide, (Vector((p.x, p.y)) - planted[b]).length)
                    else:
                        planted[b] = Vector((p.x, p.y))
                else:
                    planted.pop(b, None)                     # 離地之後再落地，重新算
            for u, l in JOINTS:
                if bend(u, l) * rest_bend[l] < 0 and abs(bend(u, l)) > 2:
                    worst_bend_flip.append(f"{l}@{f}")
            for pb in rig.pose.bones:
                if pb.name in ("root", "toy") or pb.name.endswith("_ik.L") or pb.name.endswith("_ik.R"):   # 根骨、IK 控制骨、會滾的球不算
                    continue
                ang = math.degrees((pb.matrix_basis.to_quaternion()).angle)
                if ang > worst_rot[0]:
                    worst_rot = (ang, f"{pb.name}@{f}")
                pose.append(tuple(round(x, 4) for x in pb.matrix_basis.col[3][:3]) + tuple(round(x, 4) for x in pb.matrix_basis.to_quaternion()))
            if f in (f0, (f0 + f1) // 2, f1) or f % 5 == 0:
                s = bbox()
                worst_size = max(worst_size, max(abs(s[i] / rest_size[i] - 1) for i in range(3)))
            if f == f0:
                first_pose = pose
        check(f"{act.name}: planted paws do not slide (< 1 cm)", worst_slide < 0.01, f"max slide {worst_slide * 100:.2f} cm")
        check(f"{act.name}: elbows/knees never bend backwards", not worst_bend_flip, ", ".join(worst_bend_flip[:6]) or "none")
        check(f"{act.name}: no bone rotates more than 45°", worst_rot[0] < 45, f"max {worst_rot[0]:.1f}° ({worst_rot[1]})")
        check(f"{act.name}: mesh size stays within ±25%", worst_size < 0.25, f"max change {worst_size * 100:.1f}%")
        if act.name in LOOPING:
            check(f"{act.name}: loops seamlessly (first = last frame)", pose == first_pose, f"frames {f0}–{f1}")

print(f"\nVERIFY RIG {bpy.path.basename(bpy.data.filepath)}  Blender {bpy.app.version_string}")
for name, status, evidence in results:
    print(f"{status:5s} | {name} | {evidence}")
failed = [r for r in results if r[1] == "FAIL"]
print(f"SUMMARY: {len(results) - len(failed)} PASS, {len(failed)} FAIL")
if failed:
    raise SystemExit(1)
