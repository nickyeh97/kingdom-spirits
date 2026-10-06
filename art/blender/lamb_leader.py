# 小羊（小領袖，最終進化）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Lamb_Leader.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 以成體為底：臉完全不變（還是同一隻），改的是「姿態、毛的整齊度、角的份量」三件事。
import bpy, math
from mathutils import Vector

# ---------- 顏色（與幼體相同） ----------
WOOL  = (0.96, 0.93, 0.86, 1)
FACE  = (1.00, 0.95, 0.90, 1)
BLUSH = (0.96, 0.68, 0.72, 1)   # 腮紅：比幼體淡
CAPE  = (0.62, 0.16, 0.22, 1)   # 披風（視窗用；匯出後吃「點綴色」槽，可隨配色換）
GOLD  = (0.95, 0.76, 0.30, 1)   # 披風扣環、角環
INNER = (0.92, 0.55, 0.60, 1)
HORN  = (0.94, 0.86, 0.66, 1)   # 光滑的象牙色
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
bpy.context.scene["wool_tri_target"] = 2500        # 多了披風和角環，羊毛少用 500 面，全身才能維持在 8000 以內   # 給收尾腳本用的輸出名稱

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
    # 成熟的眼神：可愛風的大眼是「直立的橢圓」（高 > 寬）；
    # 改成「橫向的橢圓」（寬 > 高），眼睛就從好奇圓睜變成沉著、專注。反光也縮小一點。
    # （試過加眼瞼，但眼瞼的陰影會被看成皺眉，反而像在生氣——簡單的形狀改變更有效。）
    sphere("Eye",      face(0.12 * s,         -0.245, 0.02),  Vector((0.062, 0.03, 0.050)) * f, (0, 0, 22 * s), INK)
    sphere("EyeShine", face(0.12 * s - 0.024, -0.276, 0.034), Vector((0.016, 0.008, 0.015)) * f, (0, 0, 22 * s), WHITE)
    # 腮紅：更小、更扁、更淡，往外下方移——仍然溫暖，但不再是「小寶寶的紅臉頰」
    sphere("Cheek",    face(0.215 * s,        -0.19, -0.095), Vector((0.038, 0.012, 0.022)) * f, (0, 0, 45 * s), BLUSH)
    sphere("Ear",      face(0.40 * s, -0.12, -0.10),  Vector((0.15, 0.07, 0.06)) * f,  (0, 30 * s, -15 * s), FACE)
    sphere("EarInner", face(0.41 * s, -0.16, -0.11),  Vector((0.11, 0.03, 0.035)) * f, (0, 30 * s, -15 * s), INNER)
sphere("Nose",      face(0, -0.278, -0.052), Vector((0.032, 0.018, 0.020)) * f, color=INK)
sphere("MouthLine", face(0, -0.274, -0.075), Vector((0.005, 0.006, 0.018)) * f, color=INK)

# 嘴：從一條「一」改成溫和的微笑弧線（用曲線＋bevel，跟羊角同一招）。
# 仍是獨立的 Mouth 物件、原點在嘴中央 → 吃果子動畫一樣動 Scale Z。
def smile():
    cu = bpy.data.curves.new("Mouth", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.0065 * f
    cu.bevel_resolution = 1
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    N = 9
    sp.points.add(N - 1)
    origin = face(0, -0.270, -0.094)
    for i in range(N):
        u = -1 + 2 * i / (N - 1)                       # -1 … 1，左嘴角到右嘴角
        x = 0.040 * u
        z = 0.016 * u * u                               # 拋物線：嘴角上揚
        y = -0.270 + 0.02 * u * u                       # 嘴角順著臉往後
        p = face(x, y, -0.094 + z) - origin
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = 1.0 - 0.4 * abs(u)       # 嘴角收細
    o = bpy.data.objects.new("Mouth", cu)
    o.location = origin
    bpy.context.scene.collection.objects.link(o)
    o.color = INK
    return o
smile()

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

# ---------- 睿智的角：光滑、俐落、黃金螺旋 ----------
# 上一版的「年輪」稜紋看起來像老；聰明的感覺來自「秩序」：
#  - 表面光滑、尖端收得很細 → 精神、銳利
#  - 用「對數螺旋」：每轉一圈半徑按固定比例縮小（自然界的鸚鵡螺、向日葵），看起來特別和諧
#  - 角根套一圈金色角環 → 像戴了冠冕的徽記，代表被託付的責任
HORN_CENTER = (0.42, 0.22, 0.08)   # 螺旋中心（幼體臉座標）：頭側偏後
HORN_R0 = 0.22                     # 第一圈半徑
HORN_TURNS = 1.35                  # 捲幾圈
HORN_SHRINK = 0.30                 # 每轉一圈，半徑剩下多少比例（對數螺旋）

def horn_point(side, t):
    cx, cy, cz = HORN_CENTER
    theta = math.radians(150) - t * HORN_TURNS * 2 * math.pi
    r = HORN_R0 * HORN_SHRINK ** (t * HORN_TURNS)                # 對數螺旋：等比例縮小
    x = cx - 0.16 * (1 - t) ** 3 + 0.04 * t
    return face(x * side, cy + r * math.cos(theta), cz + r * math.sin(theta))

def horn(side):
    cu = bpy.data.curves.new("Horn", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.075 * f
    cu.bevel_resolution = 1
    cu.resolution_u = 2
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    N = 30
    sp.points.add(N - 1)
    for i in range(N):
        t = i / (N - 1)
        p = horn_point(side, t)
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = (1 - t) ** 0.8 * 0.95 + 0.05        # 一路俐落收尖
    o = bpy.data.objects.new("Horn", cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = HORN

    # 金色角環：在角根附近，沿著角的方向套一個圓環
    t0 = 0.10
    p0, p1 = horn_point(side, t0), horn_point(side, t0 + 0.02)
    bpy.ops.mesh.primitive_torus_add(major_segments=14, minor_segments=5,
                                     major_radius=0.07 * f, minor_radius=0.014 * f, location=p0)
    band = bpy.context.active_object
    band.rotation_mode = 'QUATERNION'
    band.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(p1 - p0)   # 圓環的軸 = 角的方向
    band.name = "HornBand"
    band.color = GOLD
    bpy.ops.object.shade_smooth()
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

# ---------- 領袖披風 ----------
# 原理：披風就是「貼著身體外側的一張布」。用參數 (u, v) 描述布上的每一點：
#   v：從肩膀（0）往尾巴（1）
#   u：從左側（-1）越過背脊到右側（+1）→ 換成繞著身體的角度 φ
# 每一點 = 身體橢球表面再往外推一點（蓋過毛球），最後給布一點厚度（Solidify）。
import bmesh
CAPE_FROM, CAPE_TO = -0.55, 0.70     # 披在身體上的範圍（沿長軸：-1 前、+1 後）
CAPE_SPREAD = 95                      # 從背脊往兩側蓋多少度（越大越往下垂）
NU, NV = 12, 9
neck_c = neck_from.lerp(neck_to, 0.10)                               # 披風的領口繞在脖子根部

def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

bm = bmesh.new()
grid = []
for j in range(NV + 1):
    v = j / NV
    yf = CAPE_FROM + (CAPE_TO - CAPE_FROM) * v
    spread = math.radians(CAPE_SPREAD * (0.8 + 0.3 * v))            # 越往後越張開（下襬散開）
    row = []
    for i in range(NU + 1):
        u = -1 + 2 * i / NU
        phi = u * spread
        ring_r = math.sqrt(max(0.05, 1 - yf * yf))                   # 橢球在這個長度位置的截面大小
        out = 1.32 + 0.05 * v                                        # 推出身體表面，蓋過毛球
        wave = 0.03 * math.sin(u * 3 * math.pi) * v                  # 下襬輕輕的波浪
        on_body = BODY_C + Vector((BODY_HALF.x * out * ring_r * math.sin(phi),
                                   BODY_HALF.y * 1.05 * yf,
                                   BODY_HALF.z * out * ring_r * math.cos(phi)))
        on_body += Vector((math.sin(phi), 0, math.cos(phi))) * wave
        # 領口：第一排繞著脖子；往後幾排慢慢「過渡」到貼著身體
        collar_phi = u * math.radians(115)
        at_neck = neck_c + Vector((0.34 * math.sin(collar_phi), 0.04, 0.31 * math.cos(collar_phi)))   # 套在毛領「外面」
        p = at_neck.lerp(on_body, smoothstep(v / 0.35))
        row.append(bm.verts.new(p))
    grid.append(row)
for j in range(NV):
    for i in range(NU):
        bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Cape")
bm.to_mesh(me); bm.free()
cape = bpy.data.objects.new("Cape", me)
bpy.context.scene.collection.objects.link(cape)
cape.color = CAPE
bpy.ops.object.select_all(action='DESELECT')
cape.select_set(True); bpy.context.view_layer.objects.active = cape
sol = cape.modifiers.new("Solidify", 'SOLIDIFY')
sol.thickness = 0.025
sol.offset = 1.0
bpy.ops.object.modifier_apply(modifier=sol.name)                     # 直接套用：之後要合併網格，modifier 不能留著
bpy.ops.object.shade_smooth()

# 扣環：披風前緣、胸口正上方的一顆金扣，加一條繞過胸前的領帶
clasp_p = neck_c + Vector((0, -0.31, -0.06))
sphere("Clasp", clasp_p, Vector((0.055, 0.03, 0.055)), color=GOLD)
for s in (1, -1):                                                     # 兩條細帶：從扣環連到披風前角
    a_ = clasp_p
    b_ = neck_c + Vector((0.34 * math.sin(math.radians(115)) * s, 0.04, 0.31 * math.cos(math.radians(115))))
    mid = (a_ + b_) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.018, depth=(b_ - a_).length, location=mid)
    st = bpy.context.active_object
    st.rotation_mode = 'QUATERNION'
    st.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b_ - a_)
    st.name = "CapeStrap"; st.color = CAPE
    bpy.ops.object.shade_smooth()

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小羊・小領袖完成")
