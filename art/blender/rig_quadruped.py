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
        "style": "lively",
    },
}
J = JOINTS.get(NAME)
if J is None:
    raise SystemExit(f"rig_quadruped.py 還沒有 {NAME} 的關節位置，請在 JOINTS 加一筆")

body = bpy.data.objects[NAME]
mouth = bpy.data.objects.get("Mouth")

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
        b.ik_min_x, b.ik_max_x = math.radians(-60), math.radians(60)
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
    if m.sum() < 250:
        W[m] = W[m].mean(axis=0)

for i, n in enumerate(names):
    vg = body.vertex_groups.new(name=n)
    for v in np.nonzero(W[:, i] > 0.01)[0]:
        vg.add([int(v)], float(W[v, i]), 'REPLACE')
mod = body.modifiers.new("Armature", 'ARMATURE'); mod.object = rig
body.parent = rig
# 嘴巴是獨立物件：直接掛在頭骨上（跟著頭動，吃果子時另外張嘴）
if mouth:
    mw = mouth.matrix_world.copy()
    mouth.parent = rig; mouth.parent_type = 'BONE'; mouth.parent_bone = "head"
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
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_euler = (0, 0, 0); pb.scale = (1, 1, 1)

def key(frame, **poses):
    """poses：骨頭名 = {"loc": (x,y,z), "rot": (度,度,度)}；沒寫到的頻道維持前一個關鍵影格的值。"""
    for bname, p in poses.items():
        pb = rig.pose.bones[bname]
        if "loc" in p:
            pb.location = p["loc"]; pb.keyframe_insert("location", frame=frame)
        if "rot" in p:
            pb.rotation_euler = [math.radians(a) for a in p["rot"]]; pb.keyframe_insert("rotation_euler", frame=frame)

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
        hips={"loc": (0, 0, 0.012 * breathe * AMP)},                      # 骨盆下沉一點點＝吸氣（腳靠 IK 自己彎）
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
        "root": {"loc": (0, 0, jump * up)},
        "hips": {"loc": (0, 0, -0.04 * crouch * AMP)},
        "spine": {"rot": (-4 * up * AMP, 0, 0)},
        "head": {"rot": (-10 * look * AMP, 0, 0)},
        "tail.1": {"rot": (0, 0, 25 * wag * AMP)}, "tail.2": {"rot": (0, 0, 15 * wag * AMP)},
    }
    for c in FEET:                                   # 在空中時腳掌往身體收一點（不會僵直地垂著）
        poses[c] = {"loc": (0, 0, tuck * tk)}
    key(f, **poses)
smooth(act)

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
