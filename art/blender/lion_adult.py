# 小獅（成體，階段 3）完整腳本 —— v002
# 用法：先 File → Save As 另存新檔（例如 Lion_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# v002（組長回饋，參考圖：貓科獅子的修長身型）：
#  - 身型：深胸、細腰、臀部，身體水平；腿長、後腿有「膝蓋往前、腳踝往後」的彎折；長尾巴水平往後、末端毛球
#  - 鬃毛只框住臉（兩頰、下巴、頭頂）＋胸前，不包後腦
#  - 虎斑紋照真實虎斑貓：額頭 M 連到頭頂的條紋、外眼角的眼線、臉頰紋；背脊中線＋往兩側分岔的「魚骨紋」
#  - 共用骨架：腳掌落地的位置跟小羊成體一樣；骨頭長度不同沒關係（動畫存的是「旋轉」，同一套骨架名稱與階層就能共用）
#
# 新技巧：
#  - 身體用一串 metaball 沿著背脊排列、每顆大小不同 → 一次做出「胸大、腰細、臀圓」的流線身體
#  - 腿用「曲線＋倒角」：路徑經過肩／肘／腕或髖／膝／踝，粗細沿路變化 → 有關節彎折的腿
#  - 紋路用 closest_point_on_mesh：把草稿上的點「吸」到真正的身體表面，紋路就會貼合任何形狀
import bpy, bmesh, math
from mathutils import Vector, Quaternion, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.96, 0.70, 0.32, 1)   # 主色：身體的皮
FLESH = (1.00, 0.82, 0.74, 1)   # 副色：可愛的肉色
FUR   = (0.82, 0.48, 0.22, 1)   # 點綴色：鬃毛、尾巴毛球
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：肉球
ROSE  = (0.42, 0.24, 0.24, 1)   # 固定色：鼻子
STRIPE = (0.62, 0.38, 0.15, 1)  # 虎斑紋（主色的深色）
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_PINK   = (0.96, 0.60, 0.65, 0)
MASK_STRIPE = (0.55, 0, 0, 1)        # 主色的 55%：比幼體斑點（72%）深得多，紋路才讀得出來
MASK_ROSE   = (0.42, 0.24, 0.24, 0)

# ---------- 比例 ----------
HEAD_SCALE = 0.95                                  # Q 版：頭還是要夠大（0.86 時像真實比例，太小）
BABY_HEAD_C = Vector((0, -0.30, 0.72))             # 幼體的頭中心（臉的零件以它為基準寫座標）
HEAD_C = Vector((0, -0.58, 1.16))                  # 頭往前、往上：長脖子、抬頭
HEAD_HALF = Vector((0.30, 0.276, 0.285)) * HEAD_SCALE
LEG_X = 0.17
FRONT_Y, HIND_Y = -0.22, 0.38                      # ← 腳掌落地的位置跟小羊成體相同
# ------------------------------------------------------

f = HEAD_SCALE
def face(x, y, z, snout=1.0):
    """幼體臉上的「絕對座標」→ 成體頭上的位置。snout > 1 時把口鼻往前拉長（成獅的臉比較長）。"""
    off = Vector((x, y, z)) - BABY_HEAD_C
    if off.y < -0.20:                              # 只拉長臉的最前面（口鼻區）
        off.y = -0.20 + (off.y + 0.20) * snout
    return HEAD_C + off * f

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Lion_Adult"
bpy.context.scene["wool_tri_target"] = 1150        # 鬃毛（metaball）減到多少面

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

def smooth_path(ctrl, n_per=4):
    """把幾個控制點連成平滑的路徑（Catmull-Rom 樣條）：曲線會穿過每個控制點，轉角變圓。"""
    pts = []
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n_per):
            t = j / n_per
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(ctrl[-1])
    return pts

# ---------- 身體：一串沿著背脊排列的 metaball ----------
# 每一顆：(沿背脊的位置 y, 高度 z, 半徑)。胸最大、腰最細、臀部中等 → 貓科的流線身型
SPINE = [(-0.36, 0.76, 0.22), (-0.26, 0.74, 0.25), (-0.14, 0.72, 0.25), (-0.02, 0.74, 0.21),
         (0.10, 0.78, 0.18), (0.22, 0.80, 0.19), (0.34, 0.80, 0.21), (0.44, 0.78, 0.20)]
NECK = [(-0.44, 0.86, 0.17), (-0.50, 0.96, 0.15), (-0.54, 1.04, 0.14)]   # 脖子：從胸口往前上方接到頭
K = 0.574                                          # metaball 實際大小 = 半徑 × 0.574（小羊時實測）
mb = bpy.data.metaballs.new("TorsoCloud")
mb.resolution = 0.03
mb.threshold = 0.6
torso = bpy.data.objects.new("TorsoCloud", mb)
bpy.context.scene.collection.objects.link(torso)
for y, z, r in SPINE + NECK:
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = (0, y, z), r / K * 0.8, 2.0
# 胸口往下垂一點（深胸）：胸前下方多一顆
e = mb.elements.new(type='BALL'); e.co, e.radius = (0, -0.24, 0.60), 0.17 / K * 0.8

# 在這支腳本裡就把身體轉成網格、壓窄、減面——後面的紋路要「吸附」在真正的表面上
bpy.ops.object.select_all(action='DESELECT')
torso.select_set(True); bpy.context.view_layer.objects.active = torso
bpy.ops.object.convert(target='MESH')
body = bpy.context.active_object
body.name = "Body"
body.scale = (0.82, 1, 1)                          # 左右壓窄：貓科的身體是窄長的，不是圓筒
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
dec = body.modifiers.new("Decimate", 'DECIMATE')
dec.ratio = 1800 / (len(body.data.polygons) * 2)   # 減到約 1,800 個三角形（1,400 時臀部出現明顯的平面）
bpy.ops.object.modifier_apply(modifier=dec.name)
put(body, "Body", (1, 1, 1), (0, 0, 0), SKIN, mask=MASK_PRIMARY)

# 肚子：胸口到腹部下方一塊肉色（照片的淺色肚子）
sphere("Belly", (0, -0.16, 0.56), (0.15, 0.24, 0.10), color=FLESH, seg=16, rings=8)

# ---------- 腿：曲線＋倒角，經過關節點 ----------
def leg(side, ctrl, radii, bevel):
    pts = smooth_path([Vector((c[0] * side, c[1], c[2])) for c in ctrl], n_per=3)
    # 粗細也沿著路徑內插
    rr = []
    for i in range(len(pts)):
        u = i / (len(pts) - 1) * (len(radii) - 1)
        k = min(int(u), len(radii) - 2)
        rr.append(radii[k] + (radii[k + 1] - radii[k]) * (u - k))
    rr[0] *= 0.6                                    # 最上端收小：藏在身體裡，不會露出平平的切口
    return curve("Leg", pts, rr, bevel, SKIN, round_steps=3, mask=MASK_PRIMARY)   # 截面 3 段＝接近圓，看不出稜角

for s in (1, -1):
    # 前腳：肩（藏在胸裡）→ 肘 → 腕 → 腳掌，幾乎直直往下，腕部微微往前
    leg(s, [(LEG_X, -0.24, 0.68), (LEG_X, -0.24, 0.44), (LEG_X, -0.22, 0.18), (LEG_X, FRONT_Y - 0.02, 0.07)],
        [1.3, 1.0, 0.8, 0.75], 0.085)
    # 後腳：髖（藏在臀裡）→ 膝（往前）→ 踝（往後）→ 腳掌：貓科後腳的「Z 字」
    leg(s, [(LEG_X, 0.36, 0.70), (LEG_X, 0.28, 0.48), (LEG_X, 0.45, 0.24), (LEG_X, HIND_Y + 0.02, 0.07)],
        [1.6, 1.15, 0.8, 0.75], 0.085)
    for y in (FRONT_Y, HIND_Y):
        paw_c = Vector((LEG_X * s, y - 0.03, 0.05))
        sphere("Paw", paw_c, (0.085, 0.10, 0.055), color=FLESH, seg=10, rings=5)
        sphere("Pad", paw_c + Vector((0, 0.014, -0.046)), (0.034, 0.03, 0.008), color=PINK, seg=6, rings=3, mask=MASK_PINK)
        for dx in (-0.03, 0.0, 0.03):
            sphere("Pad", paw_c + Vector((dx, -0.05 + abs(dx) * 0.4, -0.041)), (0.014, 0.014, 0.008),
                   color=PINK, seg=6, rings=3, mask=MASK_PINK)

# ---------- 長尾巴：水平往後，先微微下垂再上揚（緩和的 S），末端毛球 ----------
tail = smooth_path([Vector((0, 0.50, 0.80)), Vector((0, 0.70, 0.74)), Vector((0, 0.90, 0.76)), Vector((0, 1.02, 0.86))], n_per=4)
curve("Tail", tail, [1.0 - 0.45 * i / (len(tail) - 1) for i in range(len(tail))], 0.032, SKIN, round_steps=2, mask=MASK_PRIMARY)
tail_tip = tail[-1]

# ---------- 頭與臉（幼體 v003 的臉，口鼻拉長 1.25 倍） ----------
SN = 1.25
sphere("Head", HEAD_C, HEAD_HALF, color=SKIN, seg=24, rings=12, mask=MASK_PRIMARY)
for s in (1, -1):
    # 成年的眼神：眼睛改成橫向的橢圓（小羊小領袖用過的做法），比幼體沉穩
    sphere("Eye",      face(0.12 * s,         -0.545, 0.745), Vector((0.058, 0.03, 0.055)) * f, (0, 0, 22 * s), INK, seg=12, rings=7)
    sphere("EyeShine", face(0.12 * s - 0.024, -0.574, 0.765), Vector((0.016, 0.01, 0.016)) * f, (0, 0, 22 * s), WHITE, seg=10, rings=6)
    sphere("Ear",      face(0.215 * s, -0.27, 0.965), Vector((0.10, 0.045, 0.095)) * f, (0, 28 * s, -10 * s), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("EarInner", face(0.215 * s, -0.305, 0.96), Vector((0.068, 0.02, 0.06)) * f, (0, 28 * s, -10 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)

MZ_FRONT = -0.635
sphere("Snout", face(0, -0.575, 0.668, SN), Vector((0.09, 0.09, 0.07)) * f, color=SKIN, seg=16, rings=8, mask=MASK_PRIMARY)
bridge = [face(0, -0.548 - 0.068 * (i / 6) ** 1.3, 0.800 - 0.115 * (i / 6), SN) for i in range(7)]
curve("Bridge", bridge, [0.45, 0.6, 0.72, 0.84, 0.95, 1.0, 0.55], 0.040 * f, SKIN, round_steps=3, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Muzzle", face(0.046 * s, MZ_FRONT + 0.022, 0.640, SN), Vector((0.052, 0.042, 0.042)) * f, (0, 0, 18 * s), FLESH, seg=12, rings=6)
sphere("Chin", face(0, MZ_FRONT + 0.035, 0.592, SN), Vector((0.04, 0.032, 0.03)) * f, color=FLESH, seg=10, rings=6)
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.052 * f, radius2=0.022 * f, depth=0.03 * f,
                                location=face(0, MZ_FRONT - 0.004, 0.684, SN))
nose = put(bpy.context.active_object, "Nose", (0.95, 0.7, 1.2), (0, 0, 0), ROSE, mask=MASK_ROSE)
nose.rotation_mode = 'QUATERNION'
nose.rotation_quaternion = Quaternion((1, 0, 0), math.radians(18)) @ Euler([math.radians(a) for a in (90, 90, 0)]).to_quaternion()

origin = face(0, MZ_FRONT + 0.012, 0.612, SN)
pts, radii = [], []
for i in range(13):
    u = -1 + 2 * i / 12
    pts.append(Vector((0.042 * u, 0.018 * u * u, -0.014 * math.sin(math.pi * abs(u)))) * f)
    radii.append(1.0 - 0.35 * abs(u))
curve("Mouth", pts, radii, 0.0065 * f, INK).location = origin

# ---------- 虎斑紋：用 closest_point_on_mesh 把紋路吸附到真正的表面 ----------
bpy.context.view_layer.update()
head = bpy.data.objects["Head"]

def surf(obj, p):
    """世界座標的點 p → obj 表面上最近的點與那裡的法線（世界座標）。"""
    mw = obj.matrix_world
    ok, loc, nor, _ = obj.closest_point_on_mesh(mw.inverted() @ p)
    return mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized()

def stripe(obj, sketch, width, sink=0.35):
    """sketch：草稿上的點（大概的位置就好）。每一點吸到表面，再沿法線往裡推 sink×width，只露出扁扁一條。"""
    pts = []
    for p in sketch:
        q, n = surf(obj, p)
        pts.append(q - n * width * sink)
    taper = [0.35] + [1.0] * (len(pts) - 2) + [0.35]
    # 截面 0 段＝菱形（4 個面）：紋路大部分埋在皮裡，只露出一條色帶，不需要圓（省面數）
    return curve("Stripe", pts, taper, width, STRIPE, round_steps=0, mask=MASK_STRIPE)

# 臉：額頭的 M（3～5 條直線組成）往上延伸越過頭頂——真實虎斑貓的 M 不是孤立的一個字
hc = HEAD_C
def H(x, y, z):                                    # 頭部的草稿座標（相對頭中心、以成體頭的大小為單位）
    return hc + Vector((x, y, z))
M_LINES = [  # 每條線從額頭（前下）往頭頂、往後
    [H(-0.075, -0.30, 0.06), H(-0.07, -0.25, 0.16), H(-0.06, -0.12, 0.25), H(-0.05, 0.02, 0.26)],
    [H(-0.03, -0.30, 0.11), H(-0.025, -0.24, 0.19), H(-0.02, -0.10, 0.26)],
    [H(0.0, -0.30, 0.07), H(0.0, -0.26, 0.17), H(0.0, -0.12, 0.27), H(0.0, 0.04, 0.27)],
    [H(0.03, -0.30, 0.11), H(0.025, -0.24, 0.19), H(0.02, -0.10, 0.26)],
    [H(0.075, -0.30, 0.06), H(0.07, -0.25, 0.16), H(0.06, -0.12, 0.25), H(0.05, 0.02, 0.26)],
]
for line in M_LINES:
    stripe(head, smooth_path(line, 2), 0.011)
for s in (1, -1):
    # 眼線：從外眼角往後、往耳朵下方拉
    stripe(head, smooth_path([H(0.135 * s, -0.24, 0.02), H(0.19 * s, -0.17, 0.03), H(0.23 * s, -0.07, 0.05)], 3), 0.01)
    # 臉頰紋：眼線下方一條彎彎的線
    stripe(head, smooth_path([H(0.13 * s, -0.24, -0.06), H(0.19 * s, -0.17, -0.05), H(0.23 * s, -0.08, -0.02)], 3), 0.009)

# 身體：背脊中線＋往兩側分岔的魚骨紋（越往下越細、越短）
def spine_top(y):
    """從正上方往下打一條射線（ray cast），打到的第一個點就是背的最高點。
    （用「最近點」的話，前面幾個點會被吸到脖子上，畫出一根懸空的棍子。）"""
    mw = body.matrix_world
    ok, loc, nor, _ = body.ray_cast(mw.inverted() @ Vector((0, y, 3.0)), Vector((0, 0, -1)))
    return mw @ loc
dorsal = [spine_top(y) for y in (-0.26, -0.14, -0.02, 0.10, 0.22, 0.34, 0.44)]
stripe(body, dorsal, 0.02)
for y in (-0.22, -0.09, 0.04, 0.17, 0.30, 0.41):
    top = spine_top(y)
    for s in (1, -1):
        # 草稿：從背頂沿著一個半徑 0.3 的圓弧往側邊、往下畫（大概是身體的截面），每步稍微往後斜
        sketch = []
        for k in range(6):
            a = math.radians(6 + k * 13)              # 0° 是正上方
            sketch.append(Vector((math.sin(a) * 0.30 * s, y + 0.015 * k, top.z - (1 - math.cos(a)) * 0.30)))
        o = stripe(body, sketch, 0.017)
        for i, pt in enumerate(o.data.splines[0].points):   # 越往下越細
            pt.radius = 0.35 if i == 0 else max(0.25, 1.0 - i / 5 * 0.75)

# ---------- 鬃毛（metaball，點綴色）：只框住臉＋胸前，不包後腦 ----------
mb2 = bpy.data.metaballs.new("ManeCloud")
mb2.resolution, mb2.render_resolution, mb2.threshold = 0.022, 0.018, 0.6
mane = bpy.data.objects.new("ManeCloud", mb2)
mane["mesh_name"] = "Fur"
bpy.context.scene.collection.objects.link(mane)
mane.color = FUR

def ball(co, r):
    e = mb2.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0

# 臉的外框：從一邊耳朵下方、繞過兩頰和下巴、到另一邊耳朵下方（頭頂留給耳朵和一撮毛）
R = HEAD_HALF.x * 1.0
n = 11
for i in range(n):
    a = math.radians(-125 + i * 250 / (n - 1))       # 0° 在正下方（下巴）
    p = hc + Vector((R * math.sin(a), -0.02, -HEAD_HALF.z * 0.98 * math.cos(a)))
    ball(p, 0.07 if abs(math.degrees(a)) > 40 else 0.06)
# 頭頂兩耳之間的一撮
top = hc + Vector((0, -0.04, HEAD_HALF.z * 0.92))
for co, r in ((top, 0.06), (top + Vector((0, -0.06, 0.02)), 0.05)):
    ball(co, r)
# 胸前：沿著脖子前面往下三顆，越下越小
for k in range(3):
    ball(hc + Vector((0, 0.04 + 0.05 * k, -HEAD_HALF.z * 1.05 - 0.09 * k)), 0.08 - 0.012 * k)
# 尾巴毛球
for co, r in ((tail_tip, 0.065), (tail_tip + Vector((0, 0.04, 0.02)), 0.05)):
    ball(co, r)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅成體 v002 完成")
