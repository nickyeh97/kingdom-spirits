# 小獅（成體，階段 3）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Lion_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# 設計（2026-10-12 組長確認，見 art/briefs/Lion_Adult.md）：
#  - 比例與腿的位置跟小羊成體完全相同 → 成體這一階共用同一套四足骨架
#  - 臉沿用小獅幼體 v003，全部經過 face() 換算（小羊成體學過的「相對座標」）
#  - 少年獅的短鬃毛：一圈蓬毛框住臉＋胸前一撮（大鬃毛留給小領袖）
#  - 虎斑貓紋路：額頭 M 字紋、背上橫紋、尾巴末端環紋（比皮深的同色系）；身上的斑點拿掉
#  - S 形尾巴＋較大的尾端毛球
import bpy, math
from mathutils import Vector, Quaternion, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.96, 0.70, 0.32, 1)   # 主色：身體的皮
FLESH = (1.00, 0.82, 0.74, 1)   # 副色：可愛的肉色
FUR   = (0.82, 0.48, 0.22, 1)   # 點綴色：鬃毛、尾巴毛球
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：肉球
ROSE  = (0.42, 0.24, 0.24, 1)   # 固定色：鼻子
STRIPE = (0.80, 0.55, 0.25, 1)  # 虎斑紋（主色的深色）
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_PINK   = (0.96, 0.60, 0.65, 0)
MASK_STRIPE = (0.72, 0, 0, 1)        # 主色的 72%：比皮深一點，換配色時跟著變（跟幼體斑點同一招）
MASK_MARK   = (0.30, 0.18, 0.16, 0)  # 淚痕
MASK_ROSE   = (0.42, 0.24, 0.24, 0)

# ---------- 比例：跟小羊成體一樣（共用骨架） ----------
#                          幼體                       成體
HEAD_SCALE = 0.92                                  # 1.0 → 0.92
BABY_HEAD_C = Vector((0, -0.30, 0.72))             # 幼體的頭中心（臉的零件以它為基準寫座標）
HEAD_C = Vector((0, -0.46, 1.10))                  # 抬高、往前：有了脖子
HEAD_HALF = Vector((0.30, 0.276, 0.285)) * HEAD_SCALE
BODY_C = Vector((0, 0.10, 0.66))
BODY_HALF = Vector((0.30, 0.48, 0.28))             # 比小羊成體的毛團瘦：獅子的輪廓就是身體本身
LEG_X, LEG_Y = 0.18, (-0.22, 0.38)                 # ← 跟小羊成體完全相同
LEG_R, LEG_LEN = 0.075, 0.42
# ------------------------------------------------------

f = HEAD_SCALE
def face(x, y, z):
    """幼體臉上的「絕對座標」→ 成體頭上的位置：先換成相對幼體頭中心，再縮放、搬到成體的頭。"""
    return HEAD_C + (Vector((x, y, z)) - BABY_HEAD_C) * f

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Lion_Adult"
bpy.context.scene["wool_tri_target"] = 1500        # 鬃毛（metaball）減到多少面（1900 時全身 8,356，超過預算）

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

def cylinder(name, loc, radius, depth, color, mask=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=depth, location=loc)
    return put(bpy.context.active_object, name, (1, 1, 1), (0, 0, 0), color, mask)

def curve(name, pts, radii, bevel, color, round_steps=1, mask=None):
    """曲線＋倒角：pts 是路徑，radii 是每一點的粗細倍率。"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = round_steps
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for i, (p, r) in enumerate(zip(pts, radii)):
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = r
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    o.color = color
    if mask:
        o["mask"] = mask
    return o

def on_ellipsoid(c, h, d, sink=1.0):
    """橢球在方向 d 上的表面點與法線（法線 = (x/a², y/b², z/c²) 正規化）。"""
    d = Vector(d).normalized()
    p = c + Vector((h.x * d.x, h.y * d.y, h.z * d.z)) * sink
    n = Vector((d.x / h.x, d.y / h.y, d.z / h.z)).normalized()
    return p, n

# ---------- 頭與臉（數字跟幼體 v003 一樣，經過 face() 換算） ----------
sphere("Head", HEAD_C, HEAD_HALF, color=SKIN, seg=24, rings=12, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Eye",      face(0.12 * s,         -0.545, 0.74),  Vector((0.055, 0.03, 0.075)) * f, (0, 0, 22 * s), INK)
    sphere("EyeShine", face(0.12 * s - 0.025, -0.575, 0.775), Vector((0.02, 0.012, 0.02)) * f,  (0, 0, 22 * s), WHITE, seg=10, rings=6)
    sphere("Ear",      face(0.225 * s, -0.25, 0.955), Vector((0.11, 0.045, 0.10)) * f, (0, 28 * s, -10 * s), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("EarInner", face(0.225 * s, -0.285, 0.95), Vector((0.075, 0.02, 0.065)) * f, (0, 28 * s, -10 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)
    tear = [face(0.088 * s, -0.562, 0.705), face(0.072 * s, -0.592, 0.682), face(0.058 * s, -0.622, 0.668)]
    curve("TearMark", tear, [1.0, 0.8, 0.5], 0.0055 * f, ROSE, mask=MASK_MARK)

MZ_FRONT = -0.635
sphere("Snout", face(0, -0.565, 0.668), Vector((0.095, 0.07, 0.072)) * f, color=SKIN, seg=16, rings=8, mask=MASK_PRIMARY)
bridge = [face(0, -0.548 - 0.068 * (i / 6) ** 1.3, 0.800 - 0.115 * (i / 6)) for i in range(7)]
curve("Bridge", bridge, [0.45, 0.6, 0.72, 0.84, 0.95, 1.0, 0.55], 0.040 * f, SKIN, round_steps=3, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Muzzle", face(0.046 * s, MZ_FRONT + 0.022, 0.640), Vector((0.055, 0.042, 0.044)) * f, (0, 0, 18 * s), FLESH, seg=12, rings=6)
sphere("Chin", face(0, MZ_FRONT + 0.035, 0.592), Vector((0.04, 0.032, 0.03)) * f, color=FLESH, seg=10, rings=6)

bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.052 * f, radius2=0.022 * f, depth=0.03 * f,
                                location=face(0, MZ_FRONT - 0.004, 0.684))
nose = put(bpy.context.active_object, "Nose", (0.95, 0.7, 1.2), (0, 0, 0), ROSE, mask=MASK_ROSE)
nose.rotation_mode = 'QUATERNION'
nose.rotation_quaternion = Quaternion((1, 0, 0), math.radians(18)) @ Euler([math.radians(a) for a in (90, 90, 0)]).to_quaternion()

# 嘴：ω 形，獨立物件、原點在嘴中央
origin = face(0, MZ_FRONT + 0.012, 0.612)
pts, radii = [], []
for i in range(13):
    u = -1 + 2 * i / 12
    pts.append(Vector((0.042 * u, 0.018 * u * u, -0.014 * math.sin(math.pi * abs(u)))) * f)
    radii.append(1.0 - 0.35 * abs(u))
curve("Mouth", pts, radii, 0.0065 * f, INK).location = origin

# ---------- 新技巧：額頭的 M 字紋 ----------
# 先在一張「平面草稿紙」上畫 M（x 左右、z 上下，單位跟頭一樣），
# 再把每一點「投影」到頭的表面上：給定 x、z，用橢球方程式算出表面的 y。
def onto_head(x, z, lift=-0.006):
    h = HEAD_HALF
    k = max(0.0, 1 - (x / h.x) ** 2 - (z / h.z) ** 2)
    y = -h.y * math.sqrt(k)                     # 臉在 −Y 那一側
    p = HEAD_C + Vector((x, y, z))
    n = Vector((x / h.x ** 2, y / h.y ** 2, z / h.z ** 2)).normalized()
    return p + n * lift                         # 沿法線「往裡」推：圓管大部分埋在皮裡，只露出一條扁扁的色帶

M = [(-0.075, 0.105), (-0.055, 0.175), (-0.025, 0.125), (0.0, 0.165),
     (0.025, 0.125), (0.055, 0.175), (0.075, 0.105)]           # M 的五個轉折
m_pts, m_r = [], []
for i in range(len(M) - 1):                                     # 每一段再細分，讓曲線貼著頭的弧度
    for j in range(3):
        t = j / 3
        x = M[i][0] + (M[i + 1][0] - M[i][0]) * t
        z = M[i][1] + (M[i + 1][1] - M[i][1]) * t
        m_pts.append(onto_head(x, z)); m_r.append(1.0)
m_pts.append(onto_head(*M[-1])); m_r.append(1.0)
m_r[0] = m_r[-1] = 0.5                                          # 兩端收細
curve("Stripe", m_pts, m_r, 0.012, STRIPE, round_steps=1, mask=MASK_STRIPE)

# ---------- 脖子與身體 ----------
neck_from = BODY_C + Vector((0, -BODY_HALF.y * 0.62, BODY_HALF.z * 0.45))
neck_to = HEAD_C + Vector((0, 0.10, -0.12))
mid = (neck_from + neck_to) / 2
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=mid)
neck = put(bpy.context.active_object, "Neck", (0.15, 0.15, (neck_to - neck_from).length * 0.65), (0, 0, 0), SKIN, mask=MASK_PRIMARY)
neck.rotation_mode = 'QUATERNION'
neck.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(neck_to - neck_from)

sphere("Body", BODY_C, BODY_HALF, color=SKIN, seg=20, rings=10, mask=MASK_PRIMARY)
sphere("Belly", BODY_C + Vector((0, -0.10, -0.08)), (0.22, 0.38, 0.19), color=FLESH, seg=16, rings=8)

# 背上的虎斑紋：每一條是繞過背脊的一段弧，從左側腰繞到右側腰，點都在身體表面上
for yf in (-0.30, -0.08, 0.14, 0.36, 0.56):
    pts = []
    for k in range(9):
        a = math.radians(-62 + k * (124 / 8))                  # 從左側 −62° 繞過背頂到右側 +62°
        rr = math.sqrt(max(0.0, 1 - yf * yf))
        d = Vector((rr * math.sin(a), yf, rr * math.cos(a)))
        p, n = on_ellipsoid(BODY_C, BODY_HALF, d)
        pts.append(p - n * 0.011)               # 圓管往皮裡推，只露出薄薄一條（像畫上去的紋，不是凸起的肋骨）
    w = 1.0 if abs(yf) < 0.45 else 0.8
    curve("Stripe", pts, [0.4, 0.8, 1, 1, 1, 1, 1, 0.8, 0.4], 0.018 * w, STRIPE, mask=MASK_STRIPE)

# ---------- 腳（位置跟小羊成體相同）＋圓腳掌＋肉球 ----------
for s in (1, -1):
    for y in LEG_Y:
        cylinder("Leg", (LEG_X * s, y, LEG_LEN / 2 + 0.03 + 0.06), LEG_R, LEG_LEN + 0.12, SKIN, mask=MASK_PRIMARY)
        thigh = (0.10, 0.12, 0.12) if y > 0 else (0.095, 0.105, 0.11)
        sphere("Haunch", (LEG_X * s, y, 0.50), thigh, color=SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
        paw_c = Vector((LEG_X * s, y - 0.02, 0.055))
        sphere("Paw", paw_c, (0.09, 0.10, 0.055), color=FLESH, seg=12, rings=6)
        sphere("Pad", paw_c + Vector((0, 0.014, -0.051)), (0.04, 0.033, 0.009), color=PINK, seg=8, rings=4, mask=MASK_PINK)
        for dx in (-0.036, 0.0, 0.036):
            sphere("Pad", paw_c + Vector((dx, -0.053 + abs(dx) * 0.4, -0.045)), (0.017, 0.017, 0.009),
                   color=PINK, seg=8, rings=4, mask=MASK_PINK)

# ---------- S 形尾巴 ----------
# 先往後下垂，再往上翹：z 方向用「一個往下的彎 + 一個往上的彎」疊起來就是 S
tail_pts, tail_r = [], []
start = BODY_C + Vector((0, BODY_HALF.y * 0.93, 0.05))
N = 16
for i in range(N):
    t = i / (N - 1)
    y = 0.38 * t
    z = -0.12 * math.sin(math.pi * t) + 0.22 * t ** 2.2
    tail_pts.append(start + Vector((0, y, z)))
    tail_r.append(1.0 - 0.3 * t)
curve("Tail", tail_pts, tail_r, 0.042, SKIN, round_steps=2, mask=MASK_PRIMARY)
tail_tip = tail_pts[-1]

# 尾巴末端的環紋：沿著尾巴切線方向套兩個細圓環
for t_idx in (N - 5, N - 3):
    p0, p1 = tail_pts[t_idx], tail_pts[t_idx + 1]
    r = 0.042 * tail_r[t_idx]
    bpy.ops.mesh.primitive_torus_add(major_segments=12, minor_segments=4, major_radius=r, minor_radius=0.009, location=p0)
    ring = put(bpy.context.active_object, "Stripe", (1, 1, 1), (0, 0, 0), STRIPE, mask=MASK_STRIPE)
    ring.rotation_mode = 'QUATERNION'
    ring.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(p1 - p0)

# ---------- 鬃毛（metaball，點綴色） ----------
mb = bpy.data.metaballs.new("ManeCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.022, 0.018, 0.6
mane = bpy.data.objects.new("ManeCloud", mb)
mane["mesh_name"] = "Fur"
bpy.context.scene.collection.objects.link(mane)
mane.color = FUR
K = 0.574

def ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0

# 鬃毛：兩圈「花邊」框住臉。角度 0° 在頭頂、往兩側繞到下巴。
# 頭頂留空給耳朵和頭頂的一撮毛；用「間距 ÷ 半徑 ≈ 2.4」決定顆數，毛球才一顆一顆分明。
def mane_ring(radius, y_off, r, skip_deg, offset=0.0):
    circ = 2 * math.pi * radius
    n = max(8, round(circ / (2.4 * r)))
    for i in range(n):
        a = 2 * math.pi * (i + offset) / n
        deg = (math.degrees(a) + 180) % 360 - 180            # −180…180，0 在頭頂
        if abs(deg) < skip_deg:
            continue
        ball(HEAD_C + Vector((radius * math.sin(a), y_off, radius * 0.95 * math.cos(a))), r)

mane_ring(HEAD_HALF.x * 1.02, 0.02, 0.065, 52)               # 前圈：貼著臉的邊
mane_ring(HEAD_HALF.x * 1.22, 0.10, 0.075, 40, offset=0.5)   # 後圈：大一點、往後，錯開半格

# 頭頂一撮（像幼體的瀏海，稍微大一點）
top = HEAD_C + Vector((0, 0.03, HEAD_HALF.z * 0.90))
for co, r in ((top, 0.065), (top + Vector((0, -0.065, 0.025)), 0.055), (top + Vector((0, -0.12, 0.01)), 0.042)):
    ball(co, r)

# 胸前一撮：下巴下方三顆大毛球排成倒三角（v1 用九顆小的，結果像腹肌）
chest = HEAD_C + Vector((0, 0.0, -HEAD_HALF.z * 1.05))
for co, r in ((chest, 0.085), (chest + Vector((0.075, 0.03, -0.02)), 0.07), (chest + Vector((-0.075, 0.03, -0.02)), 0.07),
              (chest + Vector((0, 0.05, -0.10)), 0.065)):
    ball(co, r)

# 後腦與後頸：鬃毛是從後面包住頭的（v1 後面是禿的）。
# 頭的後半球上撒一圈毛球，再往脖子後面延伸兩顆
for i in range(7):
    a = math.radians(-75 + i * 25)                         # 從左耳後繞到右耳後
    for zf, r in ((0.35, 0.075), (-0.15, 0.08)):
        d = Vector((math.sin(a), 0.75 + 0.25 * math.cos(a), zf))
        p, n = on_ellipsoid(HEAD_C, HEAD_HALF, d)
        ball(p + n * 0.01, r)
for k in range(2):
    ball(HEAD_C + Vector((0, 0.24 + 0.08 * k, -0.18 - 0.08 * k)), 0.085 - 0.01 * k)

# 尾端毛球：比幼體大
for co, r in ((tail_tip, 0.07), (tail_tip + Vector((0, 0.04, 0.03)), 0.05), (tail_tip + Vector((0, -0.01, 0.05)), 0.045)):
    ball(co, r)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅成體完成")
