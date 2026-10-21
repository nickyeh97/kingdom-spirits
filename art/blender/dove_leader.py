# 小鴿（小領袖，階段 4）完整腳本 —— v001
# 用法（命令列，在 repo 根目錄）：
#   blender -b --python art/blender/dove_leader.py --python art/blender/finalize_export.py -- art/models/Dove --unreal
# 用法（Blender 介面）：Scripting → Open 這個檔案（不要用貼上的：它要找同一個資料夾裡的 dove_adult.py）→ ▶
#
# 做法：跟小獅小領袖一樣，先「整支執行」成體腳本 dove_adult.py 蓋出成體，再加上小領袖的東西。
# 小領袖（簡報 Q5，組長 2026-10-21 確認）：頭上戴橄欖葉冠（創世記 8:11，和平）；共用的光環另做，不在這裡。
# 另外尾巴多兩根長尾羽（簡報：小領袖的尾巴更長）。
import bpy, os, math
from mathutils import Vector, Matrix

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
scene["wool_tri_target"] = 1600                     # 身體 metaball 減面減多一點，把預算讓給葉冠和長尾羽（身體很圓滑，看不太出差別）

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

print("小鴿小領袖 v001 完成")
