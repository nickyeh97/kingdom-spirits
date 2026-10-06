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
GOLD  = (0.95, 0.76, 0.30, 1)   # 披風扣子、飾繩、角環
LINING = (0.70, 0.12, 0.16, 1)  # 立領內裡：對比的紅
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
bpy.context.scene["spirit_name"] = "Lamb_Leader"   # 給收尾腳本用的輸出名稱
bpy.context.scene["wool_tri_target"] = 2400        # 多了披風和角環，羊毛少用 600 面，全身才能維持在 8000 以內
# 小零件（金扣、反光、腮紅、鼻子）用低解析度球（seg=10, rings=6）：手機上看不出差別，一顆省 124 面

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
    sphere("EyeShine", face(0.12 * s - 0.024, -0.276, 0.034), Vector((0.016, 0.008, 0.015)) * f, (0, 0, 22 * s), WHITE, seg=10, rings=6)
    # 腮紅：更小、更扁、更淡，往外下方移——仍然溫暖，但不再是「小寶寶的紅臉頰」
    sphere("Cheek",    face(0.215 * s,        -0.19, -0.095), Vector((0.038, 0.012, 0.022)) * f, (0, 0, 45 * s), BLUSH, seg=10, rings=6)
    sphere("Ear",      face(0.40 * s, -0.12, -0.10),  Vector((0.15, 0.07, 0.06)) * f,  (0, 30 * s, -15 * s), FACE)
    sphere("EarInner", face(0.41 * s, -0.16, -0.11),  Vector((0.11, 0.03, 0.035)) * f, (0, 30 * s, -15 * s), INNER)
sphere("Nose",      face(0, -0.278, -0.052), Vector((0.032, 0.018, 0.020)) * f, color=INK, seg=10, rings=6)
sphere("MouthLine", face(0, -0.274, -0.075), Vector((0.005, 0.006, 0.018)) * f, color=INK, seg=10, rings=6)

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
    bpy.ops.mesh.primitive_torus_add(major_segments=10, minor_segments=4,
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

# ---------- 領袖披風（參考學院制服短披風：肩披＋立領＋金色飾繩） ----------
# 新技巧：Shrinkwrap（收縮包覆）。
#   1. 先做一個「大概形狀」的布：從脖子往下張開的錐形，正面留開口。
#   2. 再做一個看不見的「外殼」＝身體＋毛的輪廓（用 metaball 做，轉成網格）。
#   3. Shrinkwrap 把「跑進外殼裡面」的布點推到外殼表面上 → 布自然貼著身體垂下來。
#   之後換別的動物，只要換外殼，同一套披風就能穿上去。
import bmesh
neck_c = neck_from.lerp(neck_to, 0.10)                  # 披風掛在脖子根部
OPEN = 34          # 正面開口的半角（度）：0 = 整圈包住，越大胸口露越多
CAPE_DROP = 0.42   # 披風垂多長

def collar_ring(phi, r):
    """脖子根部的一圈：phi=0 在背後（+Y），±180 在正前方。"""
    return neck_c + Vector((r * 0.95 * math.sin(phi), r * math.cos(phi), 0.02))

def drape(name, v_max, offset, nu=18, nv=7):
    bm = bmesh.new()
    grid = []
    lim = math.radians(180 - OPEN)
    for j in range(nv + 1):
        v = v_max * j / nv
        row = []
        for i in range(nu + 1):
            phi = -lim + 2 * lim * i / nu
            back = (1 + math.cos(phi)) / 2                       # 背後 1、正面 0：背後拖得比較長
            # 關鍵：布的「草稿」故意做得比身體小（在外殼裡面），
            # Shrinkwrap 才會把每一點都推到表面上 → 整片貼身。
            # 若草稿張得比外殼大，那些點在外面不會被推，就會像翅膀一樣翹出去。
            reach = 0.22 + 0.22 * v
            p = collar_ring(phi, reach)
            p.z -= CAPE_DROP * v * (1.0 - 0.3 * back)            # 正面兩片垂得比較直
            p.y += 0.55 * v * back                               # 背後的布沿著背往尾巴方向蓋
            row.append(bm.verts.new(p))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    sw = o.modifiers.new("Shrinkwrap", 'SHRINKWRAP')            # 貼著外殼
    sw.target = hull
    sw.wrap_method = 'NEAREST_SURFACEPOINT'
    sw.wrap_mode = 'OUTSIDE'                                     # 只推「跑進去」的點，外面的點不動
    sw.offset = offset
    sm = o.modifiers.new("Smooth", 'SMOOTH')                     # 推完會有點皺，抹平一下
    sm.iterations = 4
    so = o.modifiers.new("Solidify", 'SOLIDIFY')                 # 給布厚度
    so.thickness = 0.022
    so.offset = 1.0
    for m in list(o.modifiers):                                  # 之後要合併網格，modifier 直接套用
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.shade_smooth()
    return o

# 外殼：身體＋毛的輪廓（只拿來包覆，用完就刪）
hmb = bpy.data.metaballs.new("Hull")
hmb.resolution = 0.05
hmb.threshold = 0.6
e = hmb.elements.new(type='ELLIPSOID')
e.co, e.radius, e.stiffness = BODY_C, 0.3, 2.0
e.size_x, e.size_y, e.size_z = (BODY_HALF + Vector((0.13, 0.13, 0.13))) / (0.3 * K)
e = hmb.elements.new(type='BALL')
e.co, e.radius = neck_c, 0.30 / K                                # 脖子＋毛領
hull = bpy.data.objects.new("Hull", hmb)
bpy.context.scene.collection.objects.link(hull)
bpy.ops.object.select_all(action='DESELECT')
hull.select_set(True); bpy.context.view_layer.objects.active = hull
bpy.ops.object.convert(target='MESH')
hull = bpy.context.active_object

cape = drape("Cape", 1.0, 0.015)                                 # 主披風
cape.color = CAPE
capelet = drape("Capelet", 0.32, 0.05, nv=3)                     # 肩披：短的第二層，疊在主披風上
capelet.color = CAPE
bpy.data.objects.remove(hull)

# 立領：脖子根部一圈短短的布，內裡用對比色（參考圖的紅色立領）
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.31, radius2=0.35, depth=0.10,
                                end_fill_type='NOTHING', location=neck_c + Vector((0, 0.0, 0.08)))
col = bpy.context.active_object
col.rotation_euler = (math.radians(-18), 0, 0)                   # 跟著脖子往前傾
col.name = "CapeCollar"; col.color = LINING
so = col.modifiers.new("Solidify", 'SOLIDIFY'); so.thickness = 0.02
bpy.ops.object.modifier_apply(modifier=so.name)
bpy.ops.object.shade_smooth()

# 金扣＋飾繩：開口兩側各一顆金扣，中間垂一條弧形的金繩，右邊再掛兩條流蘇
lim = math.radians(180 - OPEN)
btn = [collar_ring(lim * s, 0.36) + Vector((0, -0.03, -0.10)) for s in (1, -1)]
for p in btn:
    sphere("Clasp", p, Vector((0.035, 0.022, 0.035)), color=GOLD, seg=10, rings=6)

def cord(name, pts, thick):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = thick
    cu.bevel_resolution = 1
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = GOLD
    return o

for sag in (0.10, 0.16):                                         # 兩條垂度不同的金繩（懸鏈的樣子）
    pts = []
    for i in range(11):
        t = i / 10
        p = btn[0].lerp(btn[1], t)
        p.z -= sag * 4 * t * (1 - t)                             # 拋物線：中間最低
        p.y -= 0.06 * 4 * t * (1 - t)                            # 中間往前一點，不要穿進胸口
        pts.append(p)
    cord("CapeCord", pts, 0.009)
for dx in (0.0, 0.035):                                          # 流蘇：從右邊的扣子垂下來
    top = btn[1] + Vector((dx, -0.02, -0.02))
    cord("CapeCord", [top, top + Vector((0, -0.01, -0.16))], 0.007)
    sphere("Clasp", top + Vector((0, -0.01, -0.18)), Vector((0.016, 0.016, 0.03)), color=GOLD, seg=10, rings=6)

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小羊・小領袖完成")
