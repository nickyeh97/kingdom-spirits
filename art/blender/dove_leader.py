# 小鴿（小領袖，階段 4）完整腳本 —— v002
# 用法（命令列，在 repo 根目錄）：
#   blender -b --python art/blender/dove_leader.py --python art/blender/finalize_export.py -- art/models/Dove --unreal
# 用法（Blender 介面）：Scripting → Open 這個檔案（不要用貼上的：它要找同一個資料夾裡的 dove_adult.py）→ ▶
#
# 做法：跟小獅小領袖一樣，先「整支執行」成體腳本 dove_adult.py 蓋出成體，再加上小領袖的東西。
# 小領袖（簡報 Q5，組長 2026-10-21 確認）：頭上戴橄欖葉冠（創世記 8:11，和平）；共用的光環另做，不在這裡。
# 另外尾巴多兩根長尾羽（簡報：小領袖的尾巴更長）。
# v002（組長 2026-10-29）：胸前加一件配件——金項鍊＋圓墜子，墜子正面一枝小橄欖（跟葉冠呼應；小獅是紅寶石）。
import bpy, os, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ---------- 1) 先蓋出成體 ----------
try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                                   # 在 Blender 文字編輯器裡貼上執行時沒有 __file__
    HERE = bpy.path.abspath("//")
ADULT = os.path.join(HERE, "dove_adult.py")
exec(compile(open(ADULT, encoding="utf-8").read(), ADULT, "exec"))
# exec 之後，成體腳本裡的變數都能直接用：HEAD_C、HEAD_HALF、BODY_C、sphere()、along()…

scene = bpy.context.scene
scene["spirit_name"] = "Dove_Leader"
scene["wool_tri_target"] = 1400                     # 身體 metaball 減面減多一點，把預算讓給葉冠、長尾羽、項鍊（身體很圓滑，看不太出差別）

GOLD_C  = (0.95, 0.76, 0.30, 1)
OLIVE_C = (0.42, 0.55, 0.28, 1)
MASK_GOLD  = (0.95, 0.76, 0.30, 0)                  # 固定金色（跟小羊、小獅小領袖的金色同一個值）
MASK_OLIVE = (0.42, 0.55, 0.28, 0)                  # 固定橄欖綠：葉子不跟著配色換，永遠是橄欖葉

def curve(name, pts, bevel, color, mask):
    """曲線＋倒角：沿著 pts 走的一條圓管（finalize 會轉成網格）。"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 1
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = color
    o["mask"] = mask
    return o

# ---------- 2) 橄欖葉冠：一圈金色藤蔓＋兩排橄欖葉＋正前方兩顆金色橄欖 ----------
# 葉冠戴在頭頂偏上，往前傾一點點。位置用「射線」找：
# 從圈圈外面往圓心打射線，打到頭的表面就是葉冠該貼的位置（小獅項鍊同一招）→ 不會穿進頭也不會浮著。
bpy.context.view_layer.update()
head = bpy.data.objects["Head"]
mwi = head.matrix_world.inverted()
TILT = math.radians(12)                             # 往前傾（前低後高）
RING_UP = Vector((0, math.sin(TILT), math.cos(TILT)))        # 圈圈平面的法線（往上、稍微往後）
RING_C = HEAD_C + RING_UP * HEAD_HALF.z * 0.62               # 圈圈中心：頭中心往上約六成
FWD = Vector((0, -math.cos(TILT), math.sin(TILT)))           # 圈圈平面上的「正前方」
SIDE = Vector((1, 0, 0))

def on_head(a):
    """圈圈上角度 a（0 = 正前方）的點 → 頭表面上的位置與法線。"""
    radial = (FWD * math.cos(a) + SIDE * math.sin(a)).normalized()
    start = RING_C + radial * 1.0
    ok, loc, nor, _ = head.ray_cast(mwi @ start, mwi.to_3x3() @ -radial)
    p = head.matrix_world @ loc
    n = (head.matrix_world.to_3x3() @ nor).normalized()
    return p, n

# 藤蔓：繞頭一整圈的細金管
N = 22
vine = [on_head(2 * math.pi * i / N) for i in range(N)]
pts = [p + n * 0.012 for p, n in vine]
curve("WreathVine", pts + [pts[0]], 0.013, GOLD_C, MASK_GOLD)

# 葉子：從後腦開始，左右兩邊各一串往前長，前面留一個小缺口放金橄欖（月桂冠的樣子）。
# 每個位置上下各一片，葉尖朝前、上面那片往上翹、下面那片往下翹。
def leaf(p, n, tangent, lift):
    """在頭表面 p（法線 n）放一片葉子：長軸沿 tangent 再往上／下偏 lift 度，扁的那面貼著頭。"""
    up = n.cross(tangent).normalized()              # 沿著頭表面、垂直於藤蔓的方向
    if up.z < 0:
        up = -up
    long = (tangent * math.cos(math.radians(lift)) + up * math.sin(math.radians(lift))).normalized()
    side = n.cross(long).normalized()
    rot = Matrix((side, long, n)).transposed().to_quaternion()
    o = sphere("WreathLeaf", p + n * 0.028 + long * 0.048, (0.030, 0.068, 0.011),
               color=OLIVE_C, seg=6, rings=3, mask=MASK_OLIVE)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = rot

STEPS = 5                                           # 每邊幾組葉子
for s in (1, -1):
    for k in range(STEPS):
        a = math.pi - s * (k + 0.5) * (math.pi * 0.86) / STEPS     # 從後腦（π）往前長，停在前面留缺口
        p, n = on_head(a)
        p2, _ = on_head(a - s * 0.05)
        tangent = (p2 - p).normalized()             # 往前的方向（沿著藤蔓）
        leaf(p, n, tangent, 34)
        leaf(p, n, tangent, -34)

# 正前方兩顆金色橄欖
for s in (1, -1):
    p, n = on_head(s * 0.16)
    sphere("WreathOlive", p + n * 0.032, (0.030, 0.030, 0.036), color=GOLD_C, seg=8, rings=4, mask=MASK_GOLD)

# ---------- 3) 長尾羽：成體的五根尾羽中間，再多兩根更長的（副色＋尾端深色帶） ----------
for yaw in (-7, 7):
    rot = (-6, 0, yaw)
    base = BODY_C + Vector((0, BODY_HALF.y * 0.78, -0.01))
    sphere("TailFeather", base + along(rot, (0, 0.30, 0)), (0.046, 0.33, 0.017), rot, WING, seg=10, rings=6, mask=MASK_SECONDARY)
    sphere("TailTip", base + along(rot, (0, 0.58, 0)), (0.048, 0.08, 0.020), rot, BAND, seg=10, rings=6, mask=MASK_ACCENT)

# ---------- 4) 胸前配件：金項鍊＋圓墜子（正面一枝小橄欖） ----------
# 鍊子是一個斜放的圓圈：後面高（脖子後面、頭的下緣）、前面低（胸口）。
# 圓圈上每一點從外面往圓心打射線，打到身體表面就是鍊子的位置（小獅項鍊同一招）。
# 身體是 metaball，不能直接打射線 → 先用它「算出來的網格」建一個射線用的 BVH 樹。
dg = bpy.context.evaluated_depsgraph_get()
torso_eval = torso.evaluated_get(dg)
torso_mesh = torso_eval.to_mesh()
bvh = BVHTree.FromPolygons([torso.matrix_world @ v.co for v in torso_mesh.vertices],
                           [tuple(p.vertices) for p in torso_mesh.polygons])
torso_eval.to_mesh_clear()

FRONT, BACK = Vector((0, -0.44, 0.70)), Vector((0, -0.18, 0.95))
C = (FRONT + BACK) / 2
hn = (FRONT - C).normalized()                       # 圓圈平面上「往前下」的方向
side = Vector((1, 0, 0))
chain, normals = [], []
N = 20
for i in range(N + 1):
    a = 2 * math.pi * i / N                         # a = 0 在正前方（墜子的位置）
    radial = (hn * math.cos(a) + side * math.sin(a)).normalized()
    hit, nor, _, _ = bvh.ray_cast(C + radial * 1.0, -radial)
    if hit is None:
        continue
    chain.append(hit + nor * 0.012)
    normals.append(nor)
chain[-1] = chain[0]                                # 頭尾接起來成一圈
curve("Necklace", chain, 0.011, GOLD_C, MASK_GOLD)

# 墜子：金色圓牌，掛在鍊子最低點下面，面朝外；中間一枝小橄欖（綠葉＋金色枝）
p0, n0 = chain[0], normals[0]
pend_c = p0 + Vector((0, 0, -0.075)) + n0 * 0.012
face = Vector((0, 0, 1)).rotation_difference(n0)    # 讓物件的 +Z 朝外（圓牌的正面）
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.068, depth=0.018, location=pend_c)
pend = put(bpy.context.active_object, "Pendant", (1, 1, 1), (0, 0, 0), GOLD_C, mask=MASK_GOLD)
pend.rotation_mode = 'QUATERNION'; pend.rotation_quaternion = face
# 掛環：連接鍊子和圓牌
sphere("Pendant", (p0 + pend_c) / 2 + n0 * 0.006, (0.014, 0.014, 0.024), color=GOLD_C, seg=8, rings=4, mask=MASK_GOLD)

# 橄欖枝：圓牌正面一條斜斜的金色細枝，兩側各一片、頂端一片橄欖葉（固定橄欖綠），從正面看得出是一枝葉子
up = Vector((0, 0, 1)) - n0 * n0.z                  # 圓牌面上的「上」
up.normalize()
right = up.cross(n0).normalized()
front = pend_c + n0 * 0.012                         # 圓牌正面
stem_dir = (up * math.cos(math.radians(25)) + right * math.sin(math.radians(25))).normalized()
stem = [front - stem_dir * 0.045, front + stem_dir * 0.040]
curve("OliveStem", stem, 0.005, GOLD_C, MASK_GOLD)
def emblem_leaf(at, direction):
    side_ = n0.cross(direction).normalized()
    rot = Matrix((side_, direction, n0)).transposed().to_quaternion()
    o = sphere("OliveLeaf", at + direction * 0.018 + n0 * 0.004, (0.010, 0.022, 0.005), color=OLIVE_C, seg=6, rings=3, mask=MASK_OLIVE)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = rot
for t, sign in ((-0.015, 1), (0.005, -1), (0.022, 1)):
    base = front + stem_dir * t
    leaf_dir = (stem_dir * 0.6 + right * 0.8 * sign).normalized()
    emblem_leaf(base, leaf_dir)
emblem_leaf(front + stem_dir * 0.035, stem_dir)    # 頂端那片

print("小鴿小領袖 v002 完成")
