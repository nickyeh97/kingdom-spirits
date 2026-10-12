# 小獅（成體，階段 3）完整腳本 —— v003
# 用法：先 File → Save As 另存新檔（例如 Lion_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# v003（組長回饋）：腿保留 v002；其他照參考圖（寫實的大幼獅 3D 模型）重做：
#  - 沒有鬃毛：寬寬的頭、兩頰往外蓬的短毛、大圓耳、寬口鼻＋白下巴
#  - 身體圓潤厚實（不是細腰），肩膀和臀部的肌肉直接長在身體上，把腿頂包住 → 身體和腿沒有縫
#  - 花紋：淡淡的斑點（參考圖的幼獅斑），不再用虎斑條紋
#  - 尾巴往下垂、末端微微上勾，小毛球
import bpy, bmesh, math
from mathutils import Vector, Quaternion, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.96, 0.70, 0.32, 1)   # 主色：身體的皮
FLESH = (1.00, 0.82, 0.74, 1)   # 副色：可愛的肉色
FUR   = (0.82, 0.48, 0.22, 1)   # 點綴色：尾巴毛球
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：肉球
ROSE  = (0.42, 0.24, 0.24, 1)   # 固定色：鼻子
SPOT  = (0.80, 0.55, 0.25, 1)   # 斑點（主色的淡深色）
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_PINK   = (0.96, 0.60, 0.65, 0)
MASK_SPOT = (0.78, 0, 0, 1)          # 斑點：主色的 78%，淡淡的（參考圖的幼獅斑）
MASK_ROSE   = (0.42, 0.24, 0.24, 0)

# ---------- 比例 ----------
HEAD_SCALE = 1.0                                   # Q 版：大頭
HEAD_C = Vector((0, -0.56, 1.10))                  # 頭在胸口前上方
HEAD_HALF = Vector((0.33, 0.28, 0.27))             # 參考圖：頭寬、頭頂偏平 → 寬度 > 高度
LEG_X = 0.17
FRONT_Y, HIND_Y = -0.22, 0.38                      # ← 腳掌落地的位置跟小羊成體相同
# ------------------------------------------------------


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Lion_Adult"
bpy.context.scene["wool_tri_target"] = 700        # 臉頰蓬毛（metaball）減到多少面

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
# 每一顆：(沿背脊的位置 y, 高度 z, 半徑)。參考圖的幼獅身體圓潤厚實，胸和臀差不多粗、腰只細一點點
SPINE = [(-0.36, 0.74, 0.25), (-0.24, 0.73, 0.27), (-0.12, 0.73, 0.27), (0.0, 0.75, 0.26),
         (0.12, 0.77, 0.25), (0.24, 0.78, 0.26), (0.36, 0.77, 0.26), (0.45, 0.75, 0.22)]
NECK = [(-0.44, 0.84, 0.21), (-0.50, 0.94, 0.19)]          # 粗短的脖子
# 肩膀與臀部的肌肉：直接長在身體裡、包住腿的最上端 → 身體和腿之間不會有縫
MUSCLE = [(LEG_X * 0.9, -0.24, 0.62, 0.15), (LEG_X * 0.9, 0.36, 0.64, 0.17)]
K = 0.574                                          # metaball 實際大小 = 半徑 × 0.574（小羊時實測）
mb = bpy.data.metaballs.new("TorsoCloud")
mb.resolution = 0.03
mb.threshold = 0.6
torso = bpy.data.objects.new("TorsoCloud", mb)
bpy.context.scene.collection.objects.link(torso)
def tball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K * 0.8, 2.0
for y, z, r in SPINE + NECK:
    tball((0, y, z), r)
for x, y, z, r in MUSCLE:
    for s in (1, -1):
        tball((x * s, y, z), r)

bpy.ops.object.select_all(action='DESELECT')
torso.select_set(True); bpy.context.view_layer.objects.active = torso
bpy.ops.object.convert(target='MESH')
body = bpy.context.active_object
body.scale = (0.9, 1, 1)                           # 左右稍微壓窄
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
dec = body.modifiers.new("Decimate", 'DECIMATE')
dec.ratio = 1500 / (len(body.data.polygons) * 2)
bpy.ops.object.modifier_apply(modifier=dec.name)
put(body, "Body", (1, 1, 1), (0, 0, 0), SKIN, mask=MASK_PRIMARY)

# 肚子與胸口：淺色（參考圖的肚子、胸口、下巴是淺的）
sphere("Belly", (0, -0.08, 0.53), (0.17, 0.32, 0.10), color=FLESH, seg=16, rings=8)
sphere("Chest", (0, -0.42, 0.74), (0.13, 0.08, 0.15), color=FLESH, seg=12, rings=6)

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

# ---------- 尾巴：往下垂、末端微微上勾（參考圖） ----------
tail = smooth_path([Vector((0, 0.50, 0.82)), Vector((0, 0.62, 0.64)), Vector((0, 0.68, 0.42)), Vector((0, 0.76, 0.32))], n_per=4)
curve("Tail", tail, [1.0 - 0.4 * i / (len(tail) - 1) for i in range(len(tail))], 0.038, SKIN, round_steps=2, mask=MASK_PRIMARY)
sphere("TailTuft", tail[-1] + Vector((0, 0.015, -0.01)), (0.045, 0.06, 0.05), (20, 0, 0), FUR, seg=10, rings=6, mask=(0, 0, 1, 1))

# ---------- 頭：寬寬的頭殼＋往前的寬口鼻＋白下巴 ----------
hc = HEAD_C
h = HEAD_HALF
sphere("Head", hc, h, color=SKIN, seg=24, rings=12, mask=MASK_PRIMARY)
# 額頭到口鼻：一塊往前、往下的「口鼻台」，比頭窄一些（參考圖的口鼻很寬、方方的）
sphere("Snout", hc + Vector((0, -0.22, -0.08)), (0.15, 0.13, 0.10), color=SKIN, seg=16, rings=8, mask=MASK_PRIMARY)
# 鼻樑：從兩眼之間往下的稜線（曲線＋倒角，上窄下寬）
bridge = [hc + Vector((0, -0.24 - 0.10 * (i / 6) ** 1.2, 0.05 - 0.09 * (i / 6))) for i in range(7)]
curve("Bridge", bridge, [0.45, 0.6, 0.72, 0.84, 0.95, 1.0, 0.55], 0.045, SKIN, round_steps=3, mask=MASK_PRIMARY)
# 白色的口鼻兩側（鬍鬚肉墊）與下巴
for s in (1, -1):
    sphere("Muzzle", hc + Vector((0.055 * s, -0.33, -0.12)), (0.07, 0.05, 0.055), (0, 0, 18 * s), FLESH, seg=12, rings=6)
sphere("Chin", hc + Vector((0, -0.29, -0.185)), (0.06, 0.05, 0.04), color=FLESH, seg=10, rings=6)
# 鼻子：寬的倒三角，順著鼻樑往下傾
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.055, radius2=0.024, depth=0.03, location=hc + Vector((0, -0.365, -0.06)))
nose = put(bpy.context.active_object, "Nose", (0.95, 0.7, 1.2), (0, 0, 0), ROSE, mask=MASK_ROSE)
nose.rotation_mode = 'QUATERNION'
nose.rotation_quaternion = Quaternion((1, 0, 0), math.radians(18)) @ Euler([math.radians(a) for a in (90, 90, 0)]).to_quaternion()
# 嘴：ω 形，獨立物件
origin = hc + Vector((0, -0.355, -0.135))
pts, radii = [], []
for i in range(13):
    u = -1 + 2 * i / 12
    pts.append(Vector((0.05 * u, 0.02 * u * u, -0.016 * math.sin(math.pi * abs(u)))))
    radii.append(1.0 - 0.35 * abs(u))
curve("Mouth", pts, radii, 0.007, INK).location = origin

for s in (1, -1):
    # 眼睛：杏仁形（橫向橢圓、外眼角微微上揚），在口鼻台兩側上方
    sphere("Eye",      hc + Vector((0.13 * s, -0.235, 0.03)), (0.06, 0.03, 0.05), (0, -6 * s, 25 * s), INK, seg=12, rings=7)
    sphere("EyeShine", hc + Vector((0.13 * s - 0.022, -0.262, 0.045)), (0.016, 0.01, 0.016), (0, 0, 25 * s), WHITE, seg=10, rings=6)
    # 眼睛下方的白色眼眶（參考圖眼睛下緣是淺色）
    sphere("EyeRim",   hc + Vector((0.13 * s, -0.226, -0.005)), (0.062, 0.022, 0.03), (0, -6 * s, 25 * s), FLESH, seg=10, rings=5, mask=MASK_SECONDARY)
    # 大圓耳：長在頭頂兩側、稍微往外
    sphere("Ear",      hc + Vector((0.25 * s, 0.02, 0.20)), (0.11, 0.05, 0.11), (0, 35 * s, -8 * s), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("EarInner", hc + Vector((0.25 * s, -0.015, 0.195)), (0.075, 0.02, 0.075), (0, 35 * s, -8 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)

# ---------- 兩頰往外蓬的短毛（metaball）：參考圖的臉頰毛是往兩側、往後翹的 ----------
mb2 = bpy.data.metaballs.new("CheekCloud")
mb2.resolution, mb2.render_resolution, mb2.threshold = 0.022, 0.018, 0.6
cheek = bpy.data.objects.new("CheekCloud", mb2)
cheek["mesh_name"] = "Cheek"
cheek["mask"] = MASK_PRIMARY                        # 跟皮同色（參考圖臉頰毛不是另一個顏色）
bpy.context.scene.collection.objects.link(cheek)
cheek.color = SKIN
def ball(co, r):
    e = mb2.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0
for s in (1, -1):
    # 貼著頭的兩側、往後下方漸小（v003 初版放太外面，像兩片翅膀）
    for co, r in (((0.24, -0.12, -0.10), 0.075), ((0.28, -0.05, -0.12), 0.065), ((0.30, 0.02, -0.15), 0.05)):
        ball(hc + Vector((co[0] * s, co[1], co[2])), r)

# ---------- 淡淡的斑點：吸附到身體表面 ----------
bpy.context.view_layer.update()
def surf(obj, p):
    mw = obj.matrix_world
    ok, loc, nor, _ = obj.closest_point_on_mesh(mw.inverted() @ p)
    return mw @ loc, (mw.to_3x3().inverted().transposed() @ nor).normalized()

def spot(p_sketch, r):
    """從身體側面外面往中心打射線，打到的點就是斑點的位置
    （用「最近點」的話，點會擠到臀部那一團——上一版就是這樣）。"""
    mw = body.matrix_world
    start = Vector((2.0 if p_sketch.x > 0 else -2.0, p_sketch.y, p_sketch.z))
    ok, loc, nor, _ = body.ray_cast(mw.inverted() @ start, Vector((-1 if p_sketch.x > 0 else 1, 0, 0)))
    if not ok:
        return None
    q = mw @ loc
    n = (mw.to_3x3().inverted().transposed() @ nor).normalized()
    q -= n * 0.004                                    # 一半埋進皮裡：看起來是平的花紋，不是突起
    bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=3, radius=1, location=q)
    o = put(bpy.context.active_object, "Spot", (r, r * 1.3, 0.008), (0, 0, 0), SPOT, mask=MASK_SPOT)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(n)
    return o

# 側腹、臀部一排一排的斑（左右不完全對稱，看起來比較自然）
# 參考圖的斑點：側腹、臀部、肩膀後方，一排一排錯開；越靠背越密、越往肚子越淡越小
import random
random.seed(5)
for s in (1, -1):
    for row, z in enumerate((0.88, 0.80, 0.72, 0.64)):
        for k in range(6):
            y = -0.20 + k * 0.13 + (0.065 if row % 2 else 0) + random.uniform(-0.02, 0.02)
            spot(Vector((0.6 * s, y, z + random.uniform(-0.02, 0.02))), (0.032 - 0.004 * row) * random.uniform(0.85, 1.1))

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅成體 v003 完成")
