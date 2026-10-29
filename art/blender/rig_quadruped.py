# 四足靈獸的骨架＋動作（小羊、小獅共用同一套骨架名稱）—— 第 7 課（說明見 art/RIGGING.zh-TW.md）
# 用法（命令列，在 repo 根目錄）：先開「收尾完成的 .blend」，再跑這支：
#   blender -b art/models/Lion/Lion_Baby_v004.blend --python art/blender/rig_quadruped.py -- art/models/Lion --unreal
# 會存成下一個版本（例如 Lion_Baby_v005.blend），並重新匯出帶動畫的 FBX。
# 之後用 verify_blend.py（模型）＋ verify_rig.py（骨架與動作）重新開檔驗證。
#
# 設計（組長 2026-10-29，見 art/briefs/Rig_Animation.md）：
#  - 腳用 IK（反向動力學）：每隻腳一根「IK 控制骨」，動身體時腳掌留在原地、膝蓋只往正確方向彎
#  - 動作溫和或活潑依物種（小獅活潑；小羊、鴿子溫和）
#  - 只用「旋轉」做動作（共用骨架、骨頭長度各模型不同），根骨可以上下移動（跳）
import bpy, sys, os, math
from mathutils import Vector, Euler, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = next((a for a in ARGS if not a.startswith("--")), None) or bpy.path.abspath("//")
UNREAL = "--unreal" in ARGS
NAME = bpy.context.scene.get("spirit_name") or os.path.basename(bpy.data.filepath).split("_v")[0]
FPS = 30

# ---------- 1) 每個模型的關節位置（公尺，Blender 座標：−Y 是前面、+Z 是上面） ----------
# 從造型腳本的比例算來（例如 lion_baby.py 的 HEAD_C、BODY_C、LEG_X、LEG_Y、尾巴路徑）。
# 骨頭名稱所有四足模型都一樣 → Unity 裡同一組動作可以共用；位置與長度每個模型不同。
JOINTS = {
    "Lion_Baby": {
        "hips":  ((0, 0.22, 0.40), (0, 0.06, 0.42)),     # 骨盆：從屁股往前
        "spine": ((0, 0.06, 0.42), (0, -0.10, 0.46)),    # 背
        "neck":  ((0, -0.10, 0.46), (0, -0.22, 0.60)),   # 脖子（Q 版很短）
        "head":  ((0, -0.22, 0.60), (0, -0.30, 1.00)),   # 頭：往上指，頭頂在末端
        "ear":   ((0.20, -0.25, 0.88), (0.25, -0.25, 1.02)),
        "tail":  [(0, 0.382, 0.44), (0, 0.535, 0.564), (0, 0.468, 0.716), (0, 0.335, 0.696)],   # 捲尾巴三節
        # 腿：肩／髖 → 肘／膝 → 腳掌 → 腳尖。前腳肘往後、後腳膝往前（這個微彎決定 IK 往哪邊彎）
        "front": [(0.15, -0.08, 0.34), (0.15, -0.055, 0.19), (0.15, -0.085, 0.05), (0.15, -0.15, 0.03)],
        "hind":  [(0.15, 0.20, 0.34), (0.15, 0.175, 0.19), (0.15, 0.205, 0.05), (0.15, 0.14, 0.03)],
        "head_center": (0, -0.30, 0.72), "head_radii": (0.33, 0.31, 0.31),   # 頭的範圍（含鬃毛），整塊跟頭骨走
        "eye": (0.12, -0.545, 0.74), "eye_radii": (0.075, 0.05, 0.095),      # 眼睛（lion_baby.py 的 Eye；含反光點）
        "mouth": (0, -0.623, 0.612),                                          # 嘴巴物件的原點（張嘴繞這裡縮放）
        "toy": (0, -0.24, 0.07), "toy_radius": 0.07,                          # 玩具球：前腳前面的地上（頭的正下方）
        "style": "lively",
    },
}
J = JOINTS.get(NAME)
if J is None:
    raise SystemExit(f"rig_quadruped.py 還沒有 {NAME} 的關節位置，請在 JOINTS 加一筆")

body = bpy.data.objects[NAME]
mouth = bpy.data.objects.get("Mouth")

# ---------- 1b) 額外零件：閉眼弧線、玩具球 ----------
# 都併進身體網格（同一個材質，符合美術設定檔），各自掛一根骨頭；
# 平常把它們「縮成一個點」藏在眼睛／地上，動作需要時用骨頭的縮放放大出來（睡覺時閉眼、玩玩具時出現球）。
import bmesh
HIDDEN = 0.01                                   # 平常的大小（1%）；動作裡骨頭放大 100 倍＝原尺寸
INK = (0.02, 0.02, 0.03, 0)                     # 固定色：跟眼睛同一個深色
BALL = (0.88, 0.25, 0.25, 0)                    # 固定色：紅色小球
BAND = (1.0, 0.85, 0.35, 0)                     # 固定色：球上的黃色帶（滾動時看得出在轉）
N_BODY = len(body.data.vertices)                # 併進去之前的頂點數：之後的頂點都是這裡加的零件

def finish_part(o, mask, group, center):
    """設遮罩顏色、縮成一個點、放進頂點群組（權重 1，跟那根骨頭走）。"""
    bpy.context.view_layer.update()
    me = o.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    attr = me.color_attributes.new("Mask", 'FLOAT_COLOR', 'CORNER')
    for c in attr.data:
        c.color = mask
    c0 = Vector(center)
    for v in me.vertices:
        v.co = c0 + (o.matrix_world @ v.co - c0) * HIDDEN - o.matrix_world.translation
    o.data.update()
    vg = o.vertex_groups.new(name=group)
    vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    return o

def tube(name, pts, radius):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    for x in bpy.context.view_layer.objects:
        x.select_set(x is o)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH')
    return bpy.context.active_object

extras = []
ex, ey, ez = J["eye"]
for side, sx in (("L", 1), ("R", -1)):
    # 閉眼：一道往下彎的弧線「︶」，貼在眼睛的位置（眼睛縮小後露出頭的表面，弧線就在上面）
    pts = []
    for i in range(9):
        u = -1 + 2 * i / 8
        pts.append(Vector((sx * ex + 0.045 * u, ey - 0.012 - 0.01 * (1 - u * u), ez - 0.018 * (1 - u * u))))
    extras.append(finish_part(tube(f"Lid.{side}", pts, 0.008), INK, f"lid.{side}", (sx * ex, ey, ez)))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=J["toy_radius"], location=J["toy"])
ball = bpy.context.active_object; ball.name = "Toy"
extras.append(finish_part(ball, BALL, "toy", J["toy"]))
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=J["toy_radius"] * 1.03, depth=J["toy_radius"] * 0.5,
                                    location=J["toy"], rotation=(0, math.radians(90), 0))
band = bpy.context.active_object; band.name = "ToyBand"
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
extras.append(finish_part(band, BAND, "toy", J["toy"]))
for x in bpy.context.view_layer.objects:
    x.select_set(x is body or x in extras)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
# 圓柱的蓋子是 n-gon：跟收尾腳本一樣 poke 成三角形（R03）
bm = bmesh.new(); bm.from_mesh(body.data)
ngons = [f for f in bm.faces if len(f.verts) > 4]
if ngons:
    bmesh.ops.poke(bm, faces=ngons)
bm.to_mesh(body.data); bm.free()

# ---------- 2) 建骨架（Edit Mode 放骨頭） ----------
arm = bpy.data.armatures.new("Rig")
rig = bpy.data.objects.new("Rig", arm)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
for o in bpy.context.view_layer.objects:
    o.select_set(o is rig)
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.edit_bones

def bone(name, head, tail, parent=None, deform=True, connect=False):
    b = eb.new(name)
    b.head, b.tail = Vector(head), Vector(tail)
    b.roll = 0.0
    if parent:
        b.parent = eb[parent]
        b.use_connect = connect
    b.use_deform = deform
    return b

def mirror(p):
    return (-p[0], p[1], p[2])

bone("root", (0, 0, 0), (0, 0.25, 0))                      # 根骨：整隻移動（跳）用；沒有網格跟它走
bone("hips", *J["hips"], parent="root")
bone("spine", *J["spine"], parent="hips", connect=True)
bone("neck", *J["neck"], parent="spine", connect=True)
bone("head", *J["head"], parent="neck", connect=True)
for side, f in (("L", lambda p: p), ("R", mirror)):
    bone(f"ear.{side}", f(J["ear"][0]), f(J["ear"][1]), parent="head")
for side, f in (("L", lambda p: p), ("R", mirror)):
    e = f(J["eye"])
    bone(f"eye.{side}", e, (e[0], e[1], e[2] + 0.05), parent="head")     # 張開的眼睛（睡覺時縮小）
    bone(f"lid.{side}", e, (e[0], e[1], e[2] + 0.05), parent="head")     # 閉眼弧線（睡覺時放大）
m = J["mouth"]
bone("mouth", m, (m[0], m[1], m[2] + 0.04), parent="head")                # 嘴巴物件掛這裡：沿骨頭方向（上下）縮放＝張嘴
tc = J["toy"]
bone("toy", tc, (tc[0], tc[1], tc[2] + 0.1))                             # 玩具球：獨立的骨頭（不掛 root：小獅跳起來時球留在地上）
t = J["tail"]
bone("tail.1", t[0], t[1], parent="hips")
bone("tail.2", t[1], t[2], parent="tail.1", connect=True)
bone("tail.3", t[2], t[3], parent="tail.2", connect=True)

LEGS = {}   # 腿名 → (上段, 下段, 腳掌, IK 控制骨)
for side, f in (("L", lambda p: p), ("R", mirror)):
    for kind, attach, names in (("front", "spine", ("upper_arm", "forearm", "paw")),
                                ("hind", "hips", ("thigh", "shin", "foot"))):
        p = [f(q) for q in J[kind]]
        up, lo, end = (f"{n}.{side}" for n in names)
        bone(up, p[0], p[1], parent=attach)
        bone(lo, p[1], p[2], parent=up, connect=True)
        bone(end, p[2], p[3], parent=lo, connect=True)
        # IK 控制骨：跟腳掌骨「同位置、同方向」；掛在 root 底下（跳的時候跟著整隻一起動），不變形網格。
        # 方向一定要跟腳掌一樣：腳掌會「複製」控制骨的旋轉，方向不同的話休息姿勢就會整個翻過去（v001 試做時的錯）
        ctl = f"{'hand' if kind == 'front' else 'foot'}_ik.{side}"
        bone(ctl, p[2], p[3], parent="root", deform=False)
        LEGS[f"{kind}.{side}"] = (up, lo, end, ctl)
bpy.ops.object.mode_set(mode='POSE')

# ---------- 3) IK：下段骨加 IK 約束（往上算 2 節），腳掌跟著控制骨的方向 ----------
for leg, (up, lo, end, ctl) in LEGS.items():
    pb = rig.pose.bones[lo]
    ik = pb.constraints.new('IK')
    ik.target, ik.subtarget = rig, ctl
    ik.chain_count = 2
    # 只准繞 X 軸彎（像真的膝蓋、手肘），不能往旁邊扭；角度也限制在自然範圍
    for name in (up, lo):
        b = rig.pose.bones[name]
        b.lock_ik_y = b.lock_ik_z = True
        b.use_ik_limit_x = True
        # 前腳要能抬起來揮手、趴下時要能收起來 → 範圍大一點；反折另外由 verify_rig.py 檢查
        lim = 90 if leg.startswith("front") else 75
        b.ik_min_x, b.ik_max_x = math.radians(-lim), math.radians(lim)
    cr = rig.pose.bones[end].constraints.new('COPY_ROTATION')    # 腳掌平貼地面：跟控制骨同方向
    cr.target, cr.subtarget = rig, ctl
    # 控制骨只能移動、不能縮放（R10：動畫師用得到的頻道要清楚）
    c = rig.pose.bones[ctl]
    c.lock_scale = (True, True, True)
for name in ("root",):
    rig.pose.bones[name].lock_scale = (True, True, True)
for pb in rig.pose.bones:
    pb.rotation_mode = 'XYZ'
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- 4) 權重：每個頂點跟哪幾根骨頭走 ----------
# 自動權重（bone heat）遇到這種很多零件疊在一起的網格常常失敗，所以自己算：
#  ① 頭的範圍裡（含鬃毛、眼睛、耳朵）→ 跟頭骨（耳朵附近跟耳朵骨）
#  ② 其他頂點 → 離最近的兩根骨頭，越近權重越大（關節處平滑過渡）
#  ③ 小零件（眼睛、鼻子、肉球…）整塊用同一組權重 → 動的時候不會變形
import numpy as np
me = body.data
co = np.array([v.co[:] for v in me.vertices])
deform = [b for b in arm.bones if b.use_deform and b.name != "root"]
seg = [(np.array(b.head_local[:]), np.array(b.tail_local[:])) for b in deform]

def dist_to_segment(p, a, b):
    ab = b - a
    t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)

D = np.stack([dist_to_segment(co, a, b) for a, b in seg], axis=1)          # 頂點 × 骨頭的距離
W = np.zeros_like(D)
near = np.argsort(D, axis=1)[:, :2]
for k in range(2):
    idx = near[:, k]
    W[np.arange(len(co)), idx] = 1.0 / (D[np.arange(len(co)), idx] + 0.01) ** 4
W /= W.sum(axis=1, keepdims=True)

names = [b.name for b in deform]
hc, hr = np.array(J["head_center"]), np.array(J["head_radii"])
r = np.linalg.norm((co - hc) / hr, axis=1)
w_head = np.clip((1.1 - r) / 0.2, 0, 1)                                     # 頭裡面＝1，邊緣 0.2 的範圍平滑過渡
head_w = np.zeros(len(names)); head_w[names.index("head")] = 1
for side, f in (("L", lambda p: p), ("R", mirror)):
    ear_c = np.array(f(J["ear"][0])) + 0.5 * (np.array(f(J["ear"][1])) - np.array(f(J["ear"][0])))
    on_ear = np.linalg.norm(co - ear_c, axis=1) < 0.09
    W[on_ear] = 0; W[on_ear, names.index(f"ear.{side}")] = 1
    w_head[on_ear] = 0
W = W * (1 - w_head[:, None]) + head_w[None, :] * w_head[:, None]

# ③ 小零件整塊同一組權重（連在一起的頂點算一塊）
parent = list(range(len(co)))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
for e in me.edges:
    a, b = find(e.vertices[0]), find(e.vertices[1])
    if a != b: parent[a] = b
roots = np.array([find(i) for i in range(len(co))])
for rt in np.unique(roots):
    m = roots == rt
    if m.sum() < 250 and not m[N_BODY:].any():
        W[m] = W[m].mean(axis=0)

# ④ 眼睛（深色＋白色反光點，在眼睛範圍裡）→ 100% 跟 eye 骨（睡覺時整顆縮小）
col = me.color_attributes["Mask"].data
vcol = np.zeros((len(co), 4))
for li, loop in enumerate(me.loops):
    vcol[loop.vertex_index] = col[li].color[:]
fixed_dark_or_white = (vcol[:, 3] < 0.5) & ((vcol[:, :3].max(axis=1) < 0.1) | (vcol[:, :3].min(axis=1) > 0.9))
for side, f in (("L", lambda p: p), ("R", mirror)):
    on_eye = (np.linalg.norm((co - np.array(f(J["eye"]))) / np.array(J["eye_radii"]), axis=1) < 1.0) & fixed_dark_or_white
    on_eye[N_BODY:] = False
    W[on_eye] = 0; W[on_eye, names.index(f"eye.{side}")] = 1
# ⑤ 加進來的零件（閉眼弧線、球）已經有自己的頂點群組，這裡不重算
W[N_BODY:] = 0

for i, n in enumerate(names):
    if n in body.vertex_groups:            # 零件自己帶的群組（lid.*、toy）
        continue
    vg = body.vertex_groups.new(name=n)
    for v in np.nonzero(W[:, i] > 0.01)[0]:
        vg.add([int(v)], float(W[v, i]), 'REPLACE')
mod = body.modifiers.new("Armature", 'ARMATURE'); mod.object = rig
body.parent = rig
# 嘴巴是獨立物件：掛在 mouth 骨上（跟著頭動；吃果子時 mouth 骨上下放大＝張嘴）
if mouth:
    mw = mouth.matrix_world.copy()
    mouth.parent = rig; mouth.parent_type = 'BONE'; mouth.parent_bone = "mouth"
    mouth.matrix_world = mw

# ---------- 5) 動作 ----------
# 每個動作一個 Action，用「關鍵影格」記錄控制骨的位置／旋轉；Unity 端用名稱播放（Idle、Happy…）。
# 活潑（小獅）：幅度大、節奏快、有預備動作（蹲 → 跳）；溫和（小羊、鴿子）：幅度小、慢。
LIVELY = J["style"] == "lively"
AMP = 1.0 if LIVELY else 0.55

def action(name, frames):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True                          # 沒有掛在骨架上也會存檔
    rig.animation_data_create()
    rig.animation_data.action = act
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 0, frames
    return act

def rest_all():
    """所有骨頭回到休息姿勢，並在第 0 格把「每一根」骨頭都記一個關鍵影格。
    這樣每個動作都完整描述所有骨頭：沒用到的骨頭維持原樣，不會沿用上一個動作的姿勢
    （試做時「睡覺」的閉眼就這樣跑進了「玩玩具」）。"""
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)
        for path in ("location", "rotation_euler", "scale"):
            pb.keyframe_insert(path, frame=0)

def key(frame, **poses):
    """poses：骨頭名 = {"loc": (x,y,z), "wloc": (x,y,z), "rot": (度,度,度), "scale": (x,y,z)}；
    沒寫到的頻道維持前一個關鍵影格的值。
    loc 是「骨頭自己的座標」；wloc 是「世界座標」的位移（+Y 往後、−Y 往前、+Z 往上），自動換算成骨頭座標。
    控制骨（腳的 IK、根骨、玩具）一律用 wloc：骨頭是斜放的，自己的「上」不一定是世界的上
    （第一次試做時用 loc 抬腳，腳掌反而往地下鑽、往前滑了 3 公分，就是這個原因）。"""
    for bname, p in poses.items():
        pb = rig.pose.bones[bname]
        if "wloc" in p:
            p = dict(p, loc=tuple(rig.data.bones[bname].matrix_local.to_3x3().inverted() @ Vector(p["wloc"])))
        if "loc" in p:
            pb.location = p["loc"]; pb.keyframe_insert("location", frame=frame)
        if "rot" in p:
            pb.rotation_euler = [math.radians(a) for a in p["rot"]]; pb.keyframe_insert("rotation_euler", frame=frame)
        if "scale" in p:
            sc_ = p["scale"]
            pb.scale = (sc_, sc_, sc_) if isinstance(sc_, (int, float)) else sc_
            pb.keyframe_insert("scale", frame=frame)

def smooth(act, cyclic=False):
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
        if cyclic:
            fc.modifiers.new('CYCLES')

# 骨頭的旋轉是「在骨頭自己的座標」：X＝前後點頭／彎、Y＝沿著骨頭扭、Z＝左右擺
# （脊椎、尾巴、頭的骨頭是沿著身體方向放的，所以「左右擺」用 Z）
FEET = [c for (_, _, _, c) in LEGS.values()]

# Idle（待機，2 秒循環）：呼吸讓身體上下、頭左右輕晃、尾巴擺動、耳朵偶爾動一下；腳掌固定在地上（IK）
act = action("Idle", 60)
rest_all()
for f, breathe, sway, tail, ear in ((0, 0, 0, 0, 0), (15, -1, 1, 1, 0), (30, 0, 0, 0, 0), (40, -0.5, -0.5, -1, 1),
                                    (45, -1, -1, -1, 0.3), (60, 0, 0, 0, 0)):
    key(f,
        hips={"wloc": (0, 0, 0.012 * breathe * AMP)},                      # 骨盆下沉一點點＝吸氣（腳靠 IK 自己彎）
        spine={"rot": (2 * breathe * AMP, 0, 0)},
        head={"rot": (0, 0, 5 * sway * AMP)},
        **{"tail.1": {"rot": (0, 0, 14 * tail * AMP)}, "tail.2": {"rot": (0, 0, 10 * tail * AMP)},
           "tail.3": {"rot": (0, 0, 8 * tail * AMP)},
           "ear.L": {"rot": (18 * ear * AMP, 0, 0)}, "ear.R": {"rot": (0, 0, 0)}})
smooth(act, cyclic=True)

# Happy（開心，1 秒）：蹲下預備 → 跳起來（整隻＋腳一起，腳在空中微微縮）→ 落地緩衝 → 回到站姿；尾巴快速搖
act = action("Happy", 30)
rest_all()
jump = 0.16 * AMP
tuck = 0.03 * AMP
for f, crouch, up, tk, wag, look in ((0, 0, 0, 0, 0, 0), (6, 1, 0, 0, 1, -1), (12, 0, 1, 1, -1, 1), (16, 0, 0.85, 1, 1, 1),
                                     (20, 0.7, 0, 0, -1, 0), (25, 0, 0, 0, 1, 0), (30, 0, 0, 0, 0, 0)):
    poses = {
        "root": {"wloc": (0, 0, jump * up)},
        "hips": {"wloc": (0, 0, -0.04 * crouch * AMP)},
        "spine": {"rot": (-4 * up * AMP, 0, 0)},
        "head": {"rot": (-10 * look * AMP, 0, 0)},
        "tail.1": {"rot": (0, 0, 25 * wag * AMP)}, "tail.2": {"rot": (0, 0, 15 * wag * AMP)},
    }
    for c in FEET:                                   # 在空中時腳掌往身體收一點（不會僵直地垂著）
        poses[c] = {"wloc": (0, 0, tuck * tk)}
    key(f, **poses)
smooth(act)

# 控制骨的移動都用 wloc（世界座標）；玩具骨繞自己的 X 軸轉＝往前滾
OPEN, SHUT = 1.0, 1.0 / HIDDEN                  # 骨頭縮放：1＝原樣；1/HIDDEN＝把縮成點的零件放大回原尺寸

# Wave（揮手打招呼，1.5 秒，每次打開遊戲）：重心往後一點、抬起右前腳（肉球朝前）左右揮兩下、歪頭、搖尾巴
act = action("Wave", 45)
rest_all()
for f, lift, wave, lean, wag in ((0, 0, 0, 0, 0), (8, 1, 0, 1, 1), (15, 1, 1, 1, -1), (21, 1, -1, 1, 1),
                                 (27, 1, 1, 1, -1), (33, 1, -1, 1, 1), (39, 0.3, 0, 0.5, 0), (45, 0, 0, 0, 0)):
    key(f,
        **{"hand_ik.R": {"wloc": (0.035 * wave * AMP, -0.07 * lift, 0.17 * lift * (0.6 + 0.4 * AMP)),
                         "rot": (-60 * lift, 0, 0)},                 # 腳掌往上翻 → 肉球朝前
           "hips": {"wloc": (0, 0, -0.02 * lean * AMP)},
           "spine": {"rot": (-6 * lean * AMP, 0, 0)},               # 胸口抬起來
           "head": {"rot": (0, 0, 8 * lean * AMP)},
           "tail.1": {"rot": (0, 0, 20 * wag * AMP)}, "tail.2": {"rot": (0, 0, 12 * wag * AMP)}})
smooth(act)

# Eat（吃果子，1.5 秒）：低頭、張嘴咬兩下（嘴巴骨上下放大）、抬頭滿足地晃一下
act = action("Eat", 45)
rest_all()
for f, down, mouth_open, wag in ((0, 0, 0, 0), (8, 1, 1, 0), (13, 1, 0, 1), (18, 1, 1, -1), (23, 1, 0, 1),
                                 (30, 0.2, 0, -1), (37, 0, 0, 1), (45, 0, 0, 0)):
    key(f,
        neck={"rot": (16 * down, 0, 0)}, head={"rot": (12 * down, 0, 0)},
        mouth={"scale": (1, 1 + 1.6 * mouth_open, 1)},
        **{"tail.1": {"rot": (0, 0, 15 * wag * AMP)}})
smooth(act)

# Sleep（睡覺，4 秒循環）：趴下（腳由 IK 收起來、前腳往前伸）、頭靠下來、尾巴捲向身體、閉眼、慢慢呼吸
act = action("Sleep", 120)
rest_all()
for f, breathe in ((0, 0), (40, 1), (80, 0.3), (120, 0)):
    poses = {
        "hips": {"wloc": (0, 0, -0.12 + 0.006 * breathe)},
        "spine": {"rot": (2 + 2 * breathe, 0, 0)},
        "neck": {"rot": (14, 0, 0)}, "head": {"rot": (8, 0, 6)},
        "ear.L": {"rot": (-14, 0, 0)}, "ear.R": {"rot": (-14, 0, 0)},
        "tail.1": {"rot": (0, 0, 30)}, "tail.2": {"rot": (0, 0, 20)}, "tail.3": {"rot": (0, 0, 15)},
        "eye.L": {"scale": HIDDEN}, "eye.R": {"scale": HIDDEN},          # 張開的眼睛縮起來
        "lid.L": {"scale": SHUT}, "lid.R": {"scale": SHUT},              # 閉眼弧線放大出來
        "hand_ik.L": {"wloc": (0, -0.05, 0)}, "hand_ik.R": {"wloc": (0, -0.05, 0)},   # 前腳往前伸（整段都在同一位置，不會滑）
    }
    key(f, **poses)
smooth(act, cyclic=True)

# Play（玩玩具，2 秒）：小球出現 → 擺出「邀玩」姿勢（前低後高）→ 右前腳撥球、球往前滾 → 開心地小跳追過去 → 球收起來
act = action("Play", 60)
rest_all()
R = J["toy_radius"]
roll = 0.30                                      # 撥一下，球往前滾 30 公分（滾出頭的下面，看得到）
# 撥球的腳：先垂直抬起（17 格）→ 往前撥（20 格）→ 在空中收回來（23 格）→ 垂直放下（26 格）；
# 離地、落地都是直上直下，腳掌不會在地上拖著滑
for f, show, bow, bat_fwd, bat_up, rolled, hop, wag in (
        (0, 0, 0, 0, 0, 0, 0, 0), (6, 1, 0, 0, 0, 0, 0, 0), (14, 1, 1, 0, 0, 0, 0, 1),
        (17, 1, 1, 0, 0.7, 0, 0, 0), (20, 1, 1, 1, 1, 0, 0, -1), (23, 1, 1, 0, 1, 0.4, 0, 1), (26, 1, 1, 0, 0, 0.7, 0, -1), (32, 1, 0.5, 0, 0, 1, 0, 1),
        (38, 1, 0, 0, 0, 1, 1, -1), (44, 1, 0.3, 0, 0, 1, 0, 1), (54, 1, 0, 0, 0, 1, 0, 0), (60, 0, 0, 0, 0, 1, 0, 0)):
    key(f,
        toy={"scale": HIDDEN if not show else SHUT,
             "wloc": (0, -roll * rolled, 0), "rot": (math.degrees(roll * rolled / R), 0, 0)},
        root={"wloc": (0, 0, 0.07 * hop * AMP)},
        spine={"rot": (9 * bow * AMP, 0, 0)},                                   # 前低後高
        neck={"rot": (8 * bow, 0, 0)}, head={"rot": (6 * bow - 8 * hop, 0, 0)},
        **{"hand_ik.R": {"wloc": (0, -0.06 * bat_fwd, 0.07 * bat_up)},            # 抬腳往前撥
           "tail.1": {"rot": (0, 0, 28 * wag * AMP)}, "tail.2": {"rot": (0, 0, 18 * wag * AMP)}})
smooth(act)
# 球的出現／消失用「瞬間」切換（不要慢慢長大）：縮放曲線改成常數插值
for fc in act.fcurves:
    if fc.data_path == 'pose.bones["toy"].scale':
        for kp in fc.keyframe_points:
            kp.interpolation = 'CONSTANT'

# 預設顯示 Idle；回到第 0 格
rig.animation_data.action = bpy.data.actions["Idle"]
bpy.context.scene.frame_set(0)
bpy.context.scene.render.fps = FPS

# ---------- 6) R06：可選取、Extras ----------
for o in bpy.data.objects:
    o.hide_select = False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.overlay.show_overlays = True
            area.spaces.active.overlay.show_extras = True

# ---------- 7) R12：匯出帶骨架與動作的 FBX ----------
# 跟沒有骨架的模型差在：要包含骨架、只匯出會變形網格的骨頭（IK 控制骨的效果「烘」進骨頭裡）、
# 每個 Action 一段動畫；不用 bake_space_transform（對骨架與動畫不可靠），座標軸轉換交給 Unity。
def export_fbx(path, unity):
    bpy.ops.object.select_all(action='DESELECT')
    for o in (rig, body, mouth):
        if o: o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'ARMATURE', 'MESH'},
        colors_type='LINEAR', mesh_smooth_type='FACE', add_leaf_bones=False,
        use_armature_deform_only=True, armature_nodetype='NULL',
        bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0, bake_anim_step=1.0,
        apply_scale_options='FBX_SCALE_ALL' if unity else 'FBX_SCALE_NONE',
        axis_forward='-Z', axis_up='Y')
    print("已匯出：", path)

export_fbx(os.path.join(OUT_DIR, f"{NAME}.fbx"), True)
if UNREAL:
    export_fbx(os.path.join(OUT_DIR, f"{NAME}_UE.fbx"), False)

v = 1
while os.path.exists(os.path.join(OUT_DIR, f"{NAME}_v{v:03d}.blend")):
    v += 1
path = os.path.join(OUT_DIR, f"{NAME}_v{v:03d}.blend")
bpy.context.scene["spirit_built_with"] = bpy.app.version_string
bpy.context.scene["spirit_name"] = NAME
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
print("已存檔：", path)
