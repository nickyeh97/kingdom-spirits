# 小獅（幼體，階段 1–2）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Lion_Baby.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# 設計（2026-10-12 組長確認，見 art/briefs/Lion_Baby.md）：
#  - 跟小羊幼體並排出現（GDD S1）→ 頭、身體中心、身高、眼睛都跟小羊幼體一樣
#  - 四條腿的位置跟小羊幼體完全相同 → 之後兩隻共用同一套四足骨架
#  - 還沒有鬃毛：頭頂一撮蓬毛＋兩頰柔軟的毛（點綴色）
#  - 主色＝身體的「皮」；副色＝可愛的肉色（口鼻、肚子、腳掌、內耳）
#  - 腳底有肉球（固定粉紅），揮手打招呼時看得到
#  - 斑點是階段 2 的花紋（之後用 UV 上的花紋遮罩貼圖做，不在這支腳本）
import bpy, math
from mathutils import Vector

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.96, 0.70, 0.32, 1)   # 主色：身體的皮（金黃）
FLESH = (1.00, 0.82, 0.74, 1)   # 副色：可愛的肉色
FUR   = (0.82, 0.48, 0.22, 1)   # 點綴色：頭頂毛、兩頰毛、尾巴毛球
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：腮紅、肉球
ROSE  = (0.55, 0.30, 0.32, 1)   # 固定色：鼻子
INK   = (0.12, 0.12, 0.18, 1)   # 固定色：眼睛、嘴
WHITE = (1, 1, 1, 1)

# 配色遮罩（finalize_export.py 讀 o["mask"]）：A=0 表示固定色，RGB 就是顏色本身
# 注意：Head、Leg、Ear、EarInner 這些名字在小羊身上是「臉的顏色／點綴色」，
# 小獅要的是主色（皮）與副色（肉色），所以在物件上直接指定，不靠名稱對照表
MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_PINK = (0.96, 0.60, 0.65, 0)
MASK_ROSE = (0.55, 0.30, 0.32, 0)

# ---------- 比例：跟小羊幼體一樣（並排、共用骨架） ----------
HEAD_C = Vector((0, -0.30, 0.72))
HEAD_HALF = Vector((0.30, 0.276, 0.285))
BODY_C = Vector((0, 0.06, 0.40))
BODY_HALF = Vector((0.27, 0.35, 0.25))     # 小獅沒有羊毛，身體本身就是輪廓，比小羊的毛團瘦一點
LEG_X, LEG_Y = 0.15, (-0.08, 0.20)         # ← 跟小羊幼體完全相同（共用骨架的關鍵）
LEG_R, LEG_LEN, LEG_Z = 0.06, 0.20, 0.12
# ------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Lion_Baby"     # 給收尾腳本用的輸出名稱
bpy.context.scene["wool_tri_target"] = 1400        # 毛（metaball）減到多少面

def put(o, name, scale, rot_deg, color, mask=None):
    o.name = name
    o.scale = scale
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    o.color = color
    if mask:
        o["mask"] = mask
    bpy.ops.object.shade_smooth()
    return o

def sphere(name, loc, scale, rot_deg=(0, 0, 0), color=WHITE, seg=16, rings=8, mask=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1, location=loc)
    return put(bpy.context.active_object, name, scale, rot_deg, color, mask)

def cylinder(name, loc, radius, depth, color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=depth, location=loc)
    return put(bpy.context.active_object, name, (1, 1, 1), (0, 0, 0), color)

def curve(name, pts, radii, bevel, color):
    """曲線＋倒角（跟小羊的角同一招）：pts 是路徑，radii 是每一點的粗細倍率。"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = 1
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, (p, r) in enumerate(zip(pts, radii)):
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = r
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = color
    return o

# ---------- 頭 ----------
sphere("Head", HEAD_C, HEAD_HALF, color=SKIN, seg=24, rings=12, mask=MASK_PRIMARY)

for s in (1, -1):
    # 眼睛：跟小羊幼體一模一樣（三隻並排時是同一個世界的夥伴）
    sphere("Eye",      (0.12 * s,         -0.545, 0.74),  (0.055, 0.03, 0.075), (0, 0, 22 * s), INK)
    sphere("EyeShine", (0.12 * s - 0.025, -0.575, 0.775), (0.02, 0.012, 0.02),  (0, 0, 22 * s), WHITE, seg=10, rings=6)
    # 腮紅：固定粉紅（不跟著配色換）
    sphere("Blush",    (0.20 * s, -0.50, 0.64), (0.05, 0.015, 0.035), (0, 0, 42 * s), PINK, seg=10, rings=6, mask=MASK_PINK)
    # 圓耳朵：真實幼獅的耳朵小而圓；長在頭頂兩側，稍微往外傾
    sphere("Ear",      (0.20 * s, -0.24, 0.96), (0.085, 0.04, 0.08), (0, 22 * s, -12 * s), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("EarInner", (0.20 * s, -0.27, 0.955), (0.055, 0.02, 0.05), (0, 22 * s, -12 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)
    # 鬍鬚肉墊：兩顆小圓墊（貓科的口鼻），不是往前凸出的豬鼻子
    sphere("Muzzle",   (0.045 * s, -0.565, 0.655), (0.055, 0.035, 0.045), (0, 0, 15 * s), FLESH, seg=12, rings=6)

sphere("Chin", (0, -0.548, 0.605), (0.04, 0.03, 0.03), color=FLESH, seg=10, rings=6)

# 鼻子：倒三角形。圓錐只給 3 個頂點就是三角形；轉 90° 讓它面向前方，再轉 180° 讓尖角朝下
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.034, radius2=0.012, depth=0.022,
                                location=(0, -0.592, 0.692))
nose = put(bpy.context.active_object, "Nose", (1, 0.7, 1), (90, 0, 180), ROSE, mask=MASK_ROSE)

# 嘴：貓科的「ω」形（兩個往下的小彎）。獨立物件、原點在嘴中央 → 吃果子動畫動 Scale Z 就會張嘴
W, D = 0.042, 0.014
origin = Vector((0, -0.586, 0.622))
pts, radii = [], []
for i in range(13):
    u = -1 + 2 * i / 12                     # -1 … 1
    x = W * u
    z = -D * math.sin(math.pi * abs(u))     # 中間、兩端在上，左右各一個往下的彎 → ω
    y = 0.018 * u * u                       # 嘴角順著臉往後
    pts.append(Vector((x, y, z)))
    radii.append(1.0 - 0.35 * abs(u))
mouth = curve("Mouth", pts, radii, 0.0065, INK)
mouth.location = origin

# ---------- 身體 ----------
sphere("Body", BODY_C, BODY_HALF, color=SKIN, seg=20, rings=10)
# 肚子與胸口：肉色的一塊，從胸口延伸到肚子下面
sphere("Belly", BODY_C + Vector((0, -0.08, -0.07)), (0.20, 0.27, 0.17), color=FLESH, seg=16, rings=8)

# ---------- 腳（位置跟小羊幼體相同）＋ 圓腳掌＋肉球 ----------
for s in (1, -1):
    for y in LEG_Y:
        cylinder("Leg", (LEG_X * s, y, LEG_Z), LEG_R, LEG_LEN, SKIN)["mask"] = MASK_PRIMARY
        # 圓腳掌：比腿粗一點、往前一點，底部貼地
        paw_c = Vector((LEG_X * s, y - 0.015, 0.05))
        sphere("Paw", paw_c, (0.075, 0.085, 0.05), color=FLESH, seg=12, rings=6)
        # 肉球：腳底一顆大的掌墊＋前面三顆小趾墊。揮手時腳底朝前，就看得到
        sphere("Pad", paw_c + Vector((0, 0.012, -0.046)), (0.034, 0.028, 0.008),
               color=PINK, seg=8, rings=4, mask=MASK_PINK)
        for dx in (-0.03, 0.0, 0.03):
            sphere("Pad", paw_c + Vector((dx, -0.045 + abs(dx) * 0.4, -0.04)), (0.014, 0.014, 0.008),
                   color=PINK, seg=8, rings=4, mask=MASK_PINK)

# ---------- 尾巴：細長的曲線，輕輕往上翹 ----------
tail_pts, tail_r = [], []
for i in range(10):
    t = i / 9
    tail_pts.append(BODY_C + Vector((0.0,
                                     BODY_HALF.y * 0.9 + 0.26 * t,
                                     0.02 + 0.30 * t ** 1.6 + 0.05 * math.sin(math.pi * t))))
    tail_r.append(1.0 - 0.3 * t)
curve("Tail", tail_pts, tail_r, 0.032, SKIN)
tail_tip = tail_pts[-1]

# ---------- 毛（metaball，點綴色）：頭頂一撮、兩頰軟毛、尾巴毛球 ----------
mb = bpy.data.metaballs.new("FurCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.02, 0.016, 0.6
fur = bpy.data.objects.new("FurCloud", mb)
fur["mesh_name"] = "Fur"                     # 轉成網格後叫 Fur（finalize 用）
bpy.context.scene.collection.objects.link(fur)
fur.color = FUR
K = 0.574                                    # metaball 實際大小 = 半徑 × 0.574（小羊時實測）

def ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0

# 頭頂一撮：像睡醒翹起的一小撮毛（往前捲），不是往上長的角。
# 毛球放在頭頂表面附近、越前面越低越小 → 看起來是「一簇往前垂」的瀏海
top = HEAD_C + Vector((0, 0.03, HEAD_HALF.z * 0.90))
for co, r in ((top, 0.07),
              (top + Vector((0, -0.07, 0.03)), 0.06),
              (top + Vector((0, -0.13, 0.015)), 0.045),
              (top + Vector((0.065, 0.0, -0.01)), 0.05),
              (top + Vector((-0.065, 0.0, -0.01)), 0.05)):
    ball(co, r)

# 兩頰軟毛：一圈「花邊」框住臉的下半部，從耳朵下方繞過下巴。
# 用小羊學到的「間距 ÷ 半徑 ≈ 2.4」：毛球小、間距夠，才會一顆一顆分明，不會糊成兩大塊。
RUFF_R = 0.045
for k in range(13):
    a = math.radians(-110 + k * (220 / 12))   # 0° 是正下方（下巴），±110° 到耳朵下方
    p = HEAD_C + Vector((HEAD_HALF.x * 0.95 * math.sin(a),
                         -HEAD_HALF.y * 0.35,                     # 稍微偏臉的前方
                         -HEAD_HALF.z * 0.93 * math.cos(a)))
    if abs(math.degrees(a)) < 25:                                  # 正下巴留給肉墊和嘴
        continue
    ball(p, RUFF_R * (1.15 if abs(math.degrees(a)) > 60 else 1.0))

# 尾巴毛球
for co, r in ((tail_tip, 0.06), (tail_tip + Vector((0, 0.03, 0.04)), 0.045)):
    ball(co, r)

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅幼體完成")
