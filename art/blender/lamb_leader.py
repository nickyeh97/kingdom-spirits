# 小羊（小領袖，最終進化）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Lamb_Leader.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 以成體為底：臉完全不變（還是同一隻），改的是「姿態、毛的整齊度、角的份量」三件事。
import bpy, math
from mathutils import Vector

# ---------- 顏色（與幼體相同） ----------
WOOL  = (0.96, 0.93, 0.86, 1)
FACE  = (1.00, 0.95, 0.90, 1)
BLUSH = (0.95, 0.55, 0.65, 1)
INNER = (0.92, 0.55, 0.60, 1)
HORN  = (0.90, 0.78, 0.52, 1)
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

# ---------- 比例：領袖風範 = 抬頭、挺胸、站得高 ----------
#                成體                        小領袖
HEAD_SCALE = 0.90                        # 0.92 → 0.90
HEAD_C = Vector((0, -0.50, 1.32))        # (0,-0.46,1.10) → 頭抬得更高：脖子直挺
BODY_C = Vector((0, 0.10, 0.76))         # (0,0.10,0.66)  → 整個身體再抬高
BODY_HALF = Vector((0.34, 0.50, 0.31))   # (0.36,0.50,0.33) → 稍微收窄：線條俐落、不再圓滾
LEG_LEN, LEG_R = 0.50, 0.068             # 0.42 → 0.50：腿更長，站姿挺拔
LEG_X, LEG_Y = 0.17, (-0.22, 0.40)
HOOD_PUFF = 1.13
FACE_WINDOW = 0.88
# ------------------------------------------

BASE_HEAD_HALF = Vector((0.30, 0.276, 0.285))   # 幼體的頭
HEAD_HALF = BASE_HEAD_HALF * HEAD_SCALE

def face(x, y, z):
    """幼體臉上的位置（相對於幼體頭中心）→ 換算成成體頭上的位置。"""
    return HEAD_C + Vector((x, y, z)) * HEAD_SCALE

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Lamb_Leader"
bpy.context.scene["wool_tri_target"] = 2800        # 角比較大，羊毛少用 200 面，全身才能維持在 8000 以內   # 給收尾腳本用的輸出名稱

def put(o, name, scale, rot_deg, color):
    o.name = name
    o.scale = scale
    o.rotation_euler = [math.radians(a) for a in rot_deg]
    o.color = color
    bpy.ops.object.shade_smooth()
    return o

def sphere(name, loc, scale, rot_deg=(0, 0, 0), color=WHITE, seg=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1, location=loc)
    return put(bpy.context.active_object, name, scale, rot_deg, color)

def cylinder(name, loc, radius, depth, color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=depth, location=loc)
    return put(bpy.context.active_object, name, (1, 1, 1), (0, 0, 0), color)

# ---------- 頭與五官：數字跟幼體一樣，只是全部經過 face() 換算 ----------
f = HEAD_SCALE
sphere("Head", HEAD_C, HEAD_HALF, color=FACE, seg=24, rings=12)
for s in (1, -1):
    sphere("Eye",      face(0.12 * s,         -0.245, 0.02),  Vector((0.055, 0.03, 0.075)) * f, (0, 0, 22 * s), INK)
    sphere("EyeShine", face(0.12 * s - 0.025, -0.275, 0.055), Vector((0.02, 0.012, 0.02)) * f,  (0, 0, 22 * s), WHITE)
    sphere("Cheek",    face(0.20 * s,         -0.20, -0.08),  Vector((0.05, 0.015, 0.035)) * f, (0, 0, 42 * s), BLUSH)
    sphere("Ear",      face(0.40 * s, -0.12, -0.10),  Vector((0.15, 0.07, 0.06)) * f,  (0, 30 * s, -15 * s), FACE)
    sphere("EarInner", face(0.41 * s, -0.16, -0.11),  Vector((0.11, 0.03, 0.035)) * f, (0, 30 * s, -15 * s), INNER)
sphere("Nose",      face(0, -0.278, -0.052), Vector((0.032, 0.018, 0.020)) * f, color=INK)
sphere("Mouth",     face(0, -0.268, -0.098), Vector((0.028, 0.012, 0.008)) * f, color=INK)
sphere("MouthLine", face(0, -0.274, -0.075), Vector((0.005, 0.006, 0.02)) * f,  color=INK)

# ---------- 腳：變長，而且有「形狀」 ----------
def cone(name, loc, r_bottom, r_top, depth, color):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=r_bottom, radius2=r_top, depth=depth, location=loc)
    return put(bpy.context.active_object, name, (1, 1, 1), (0, 0, 0), color)

for s in (1, -1):
    for y in LEG_Y:
        # 腿：上粗下細的錐形（大腿有肉、腳踝細），比直筒更有「長大」的感覺
        cone("Leg",  (LEG_X * s, y, LEG_LEN / 2 + 0.05), LEG_R * 0.78, LEG_R * 1.15, LEG_LEN, FACE)
        # 蹄：下寬上窄，站得穩
        cone("Hoof", (LEG_X * s, y, 0.04), LEG_R * 1.0, LEG_R * 0.8, 0.08, INK)

# ---------- 睿智的角：更大、多捲半圈、表面有「年輪」 ----------
# 真實的公羊角每年長一圈稜紋，稜紋越多越年長——這就是「睿智」的視覺語言。
HORN_CENTER = (0.42, 0.22, 0.06)   # 螺旋中心（幼體臉座標）：頭側偏後
HORN_R0 = 0.24                     # 比成體（0.19）大：角的份量感
HORN_TURNS = 1.6                   # 比成體（1.25）多捲：完整的螺旋
RIDGES = 9                         # 年輪（稜紋）的圈數
RIDGE_DEPTH = 0.22                 # 稜紋的深淺（佔粗細的比例）

def horn(side):
    """跟成體一樣是「螺旋曲線 + bevel 粗細」；
    差別在每個點的粗細多乘一個 sin 波 → 沿著角出現一圈一圈的稜紋。"""
    cu = bpy.data.curves.new("Horn", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.085 * f          # 角根更粗
    cu.bevel_resolution = 1              # 截面 6 邊形就夠圓（省面數）
    cu.resolution_u = 1                  # 點已經很密，曲線本身不必再細分（省面數）
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    N = 56                               # 稜紋需要較多的點：每圈稜紋約 6 個點
    sp.points.add(N - 1)
    cx, cy, cz = HORN_CENTER
    for i in range(N):
        t = i / (N - 1)
        theta = math.radians(150) - t * HORN_TURNS * 2 * math.pi   # 角根在頭頂偏前 → 往上往後拱 → 往下 → 往內捲
        r = HORN_R0 * (1 - 0.72 * t)
        x = cx - 0.16 * (1 - t) ** 3 + 0.05 * t                     # 角根接在毛帽上；越捲越往外，讓內圈也看得到
        p = face(x * side, cy + r * math.cos(theta), cz + r * math.sin(theta))
        sp.points[i].co = (p.x, p.y, p.z, 1)
        taper = 1.0 - 0.72 * t                                       # 越往末端越細
        ridge = 1.0 + RIDGE_DEPTH * math.sin(t * RIDGES * 2 * math.pi) * (1 - t)   # 年輪：角根明顯、尖端淡去
        sp.points[i].radius = taper * ridge
    o = bpy.data.objects.new("Horn", cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = HORN
    return o

for s in (1, -1):
    horn(s)

# ---------- 羊毛（metaball，同幼體的作法） ----------
mb = bpy.data.metaballs.new("WoolCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.025, 0.02, 0.6
wool = bpy.data.objects.new("WoolCloud", mb)
bpy.context.scene.collection.objects.link(wool)
wool.color = WOOL
K = 0.574

def ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0

def ellipsoid(co, half, negative=False, stiffness=2.0):
    e = mb.elements.new(type='ELLIPSOID')
    e.co, e.radius, e.stiffness = co, 0.3, stiffness
    e.size_x, e.size_y, e.size_z = half / (0.3 * K)
    e.use_negative = negative

def in_face_window(p):
    q = (p - HEAD_C) / f
    return q.y < -0.12 and (q.x / 0.24) ** 2 + ((q.z + 0.03) / 0.22) ** 2 < FACE_WINDOW ** 2

def ring(center, half, z_frac, count, r, offset=0.0):
    rr = math.sqrt(max(0.0, 1 - z_frac * z_frac))
    for i in range(count):
        a = 2 * math.pi * (i + offset) / count
        p = center + Vector((half.x * rr * math.cos(a), half.y * rr * math.sin(a), half.z * z_frac))
        if not in_face_window(p):
            ball(p, r)

# 1) 身體：乾淨俐落——毛「修剪」過：身體表面平順，只留三排整齊的半圓花邊；
#    stiffness 調高（2 → 3.5），每顆的邊界更銳利，像修過的毛，而不是蓬鬆的雲。
def crisp_ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / 0.66, 3.5     # stiffness 3.5 時實際大小 ≈ radius × 0.66（實測）

GAP = 2.2
BH = BODY_HALF * 1.0
ellipsoid(BODY_C, BH * 0.97)
for zf, r, off in ((0.62, 0.10, 0.0), (0.15, 0.11, 0.5), (-0.35, 0.10, 0.0)):
    rr = math.sqrt(1 - zf * zf)
    a_, b_ = BH.x * rr, BH.y * rr
    circ = math.pi * (3 * (a_ + b_) - math.sqrt((3 * a_ + b_) * (a_ + 3 * b_)))
    n = max(5, round(circ / (GAP * r)))
    for i in range(n):
        ang = 2 * math.pi * (i + off) / n
        crisp_ball(BODY_C + Vector((BH.x * rr * math.cos(ang), BH.y * rr * math.sin(ang), BH.z * zf)), r)
crisp_ball(BODY_C + Vector((0, BH.y * 1.02, 0.10)), 0.10)   # 尾巴

# 2) 領袖的披肩毛：胸前到肩膀一圈較大的毛領，像披風一樣——領袖感的主要來源
neck_from = BODY_C + Vector((0, -BODY_HALF.y * 0.62, BODY_HALF.z * 0.5))
neck_to = HEAD_C + Vector((0, 0.10, -0.12))
for i in range(5):                                           # 直挺的脖子
    t = i / 4
    ball(neck_from.lerp(neck_to, t), 0.15 - 0.02 * t)
# 毛領：繞著脖子根部一整圈，像披風的領口。
# 做法：先算出脖子的方向 d，再找兩個跟 d 垂直的方向 u、v，就能在「垂直於脖子的平面」上畫圓。
c = neck_from.lerp(neck_to, 0.15)
d = (neck_to - neck_from).normalized()
u = d.cross(Vector((1, 0, 0))).normalized()     # 垂直於脖子、指向前後上下的方向
v = d.cross(u).normalized()                     # 第三個方向（左右）
for k in range(12):
    a = 2 * math.pi * k / 12
    crisp_ball(c + (u * math.cos(a) + v * math.sin(a)) * 0.20, 0.10)

# 3) 毛帽（同幼體）
ellipsoid(HEAD_C, HEAD_HALF * HOOD_PUFF)
for zf, n, off in ((0.8, 6, 0.0), (0.45, 10, 0.5), (0.0, 12, 0.0), (-0.5, 10, 0.5)):
    ring(HEAD_C, HEAD_HALF * HOOD_PUFF, zf, n, 0.075 * f, off)
ellipsoid(face(0, -0.276, -0.03), Vector((0.24, 0.16, 0.22)) * FACE_WINDOW * f, negative=True, stiffness=4.0)

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小羊・小領袖完成")
