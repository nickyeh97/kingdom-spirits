# 小獅（成體，階段 3）完整腳本 —— v007（v006 + 肉球露出來、尾巴接縫）
# 用法：先 File → Save As 另存新檔（例如 Lion_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# v005（組長決定：風格回到 Q 版；輪廓與毛色照 Meshy Lion Cub 參考，見 docs/art-worklog/2026-10-12_010）：
#  - 身體：從參考模型「量出來」的側面輪廓表（每一段的背高、肚子高、寬度），換算成 Q 版比例後，
#          用「放樣（Loft）」一圈一圈接成身體 → 輪廓的順序跟參考一樣：胸口深、肩膀最高、背平、屁股稍低
#  - 臉：沿用組長驗收過的小獅幼體的臉（整組放大 1.1 倍），表情語言一致
#  - 腿：保留 v002/v003 組長說像的腿（貓科前直後 Z），按 Q 版縮短
# v006（組長回饋）：臉頰毛改成成獅的一圈鬃毛；拿掉脖子那顆（接縫一圈很怪）→ 脖子直接放樣進身體；
#  淺色的喉嚨、胸口、肚子改成一條連續漸層；胸口、肩膀加寬、腰收細、前腳加粗 → 雄偉有力
#  - 毛色：自然獅子毛色——背脊較深（shade 漸層）、胸口與肚子較淺（副色）、耳背與尾巴毛球較深，
#          加上往下梳的毛流紋理（finalize 烘成花紋遮罩貼圖）；沒有斑點、沒有條紋
import bpy, bmesh, math
from mathutils import Vector, Quaternion, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.90, 0.64, 0.36, 1)   # 主色：身體（自然的黃褐色）
FLESH = (1.00, 0.86, 0.72, 1)   # 副色：淺色區（口鼻、下巴、胸口、肚子、腳掌、內耳）
FUR   = (0.70, 0.40, 0.20, 1)   # 點綴色：深色的毛（尾巴毛球）
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：肉球
ROSE  = (0.42, 0.24, 0.24, 1)   # 固定色：鼻子
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_EARBACK   = (0.6, 0, 0, 1)      # 耳背：主色的 60%（參考模型的耳背是深色）
MASK_TUFT      = (0, 0, 0.6, 1)      # 尾巴毛球：點綴色的 60%（深色）
MASK_PINK = (0.96, 0.60, 0.65, 0)
MASK_ROSE = (0.42, 0.24, 0.24, 0)
MASK_MARK = (0.30, 0.18, 0.16, 0)    # 固定色：淚痕

# ---------- 比例 ----------
LEG_X = 0.17
FRONT_Y, HIND_Y = -0.22, 0.38                      # ← 腳掌落地的位置跟小羊成體相同（共用骨架）
HEAD_C = Vector((0, -0.52, 1.10))                  # 頭在胸口前上方（參考：頭頂比肩膀高、往前伸）
S = 1.1                                            # 臉：幼體的臉整組放大 1.1 倍
BABY_HC = Vector((0, -0.30, 0.72))                 # 幼體腳本的頭中心（臉的座標都以它為基準）
HEAD_HALF = Vector((0.30, 0.276, 0.285)) * S
# ------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
for me in list(bpy.data.meshes):
    if me.users == 0:
        bpy.data.meshes.remove(me)
scene = bpy.context.scene
scene["spirit_name"] = "Lion_Adult"
scene["wool_tri_target"] = 1500                    # 鬃毛圈（metaball）減到多少面
scene["preview_palette"] = [SKIN, FLESH, FUR]      # finalize 預覽材質用的配色
# 毛流紋理：雜訊在上下方向（z）拉長 → 像往下梳的毛；0.82–1.0 ＝ 最多暗 18%，淡淡的
scene["pattern"] = {"size": 512, "scale": (26.0, 26.0, 6.0), "low": 0.82, "high": 1.0, "detail": 3}

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

def F(x, y, z):
    """幼體臉上的座標 → 成體頭上的座標（以頭中心為基準放大 S 倍）。"""
    return HEAD_C + (Vector((x, y, z)) - BABY_HC) * S

# ---------- 身體：放樣（Loft） ----------
# 參考模型（轉正、身高 1.42 m）每隔一段量一次：(前後位置 y, 背的高度, 肚子的高度, 半寬)
REF_PROFILE = [
    (-0.72, 1.30, 0.80, 0.17),   # v006：脖子（參考模型胸口往上接到頭的那段）直接放樣進身體 → 沒有一圈接縫
    (-0.67, 1.24, 0.68, 0.20),
    (-0.62, 1.16, 0.60, 0.23),   # 胸口最前面
    (-0.575, 1.20, 0.52, 0.26),
    (-0.50, 1.22, 0.47, 0.29),   # 肩膀最高
    (-0.425, 1.20, 0.45, 0.30),
    (-0.35, 1.16, 0.43, 0.30),   # 胸口最深
    (-0.275, 1.12, 0.42, 0.30),
    (-0.20, 1.07, 0.42, 0.29),
    (-0.125, 1.04, 0.41, 0.27),
    (-0.05, 1.02, 0.40, 0.26),   # 背是平的
    (0.025, 1.02, 0.40, 0.25),   # 腰只細一點點
    (0.10, 1.02, 0.41, 0.25),
    (0.175, 1.03, 0.42, 0.26),
    (0.25, 1.04, 0.43, 0.28),
    (0.325, 1.04, 0.44, 0.29),   # 臀部
    (0.40, 1.03, 0.47, 0.29),
    (0.475, 1.01, 0.52, 0.27),
    (0.55, 0.97, 0.60, 0.23),    # 屁股稍低、往下收
    (0.62, 0.89, 0.70, 0.16),
]
# 換算成 Q 版：前後縮短（腳距要跟共用骨架一樣）、腿變短（整個身體往下）、身體稍微胖一點
# v006「雄偉有力」：獅子的力量感來自寬厚的胸口和肩膀、收細的腰、結實的臀 → 寬度依前後位置加倍率
def power_w(y):
    pts = [(-0.75, 1.10), (-0.30, 1.22), (-0.05, 0.98), (0.15, 0.98), (0.35, 1.10), (0.65, 1.0)]
    for (y0, f0), (y1, f1) in zip(pts, pts[1:]):
        if y <= y1:
            t = max(0.0, (y - y0) / (y1 - y0))
            return f0 + (f1 - f0) * t
    return pts[-1][1]
def to_q(y, top, bot, w):
    return (0.08 + (y + 0.04) * 0.68, 0.30 + (top - 0.40) * 0.85, 0.30 + (bot - 0.40) * 0.85, w * 0.95 * power_w(y))
PROFILE = [to_q(*r) for r in REF_PROFILE]

def loft(name, profile, ring_n=28, power=2.6):
    """放樣：每一列輪廓做成一圈點（圓角方形的截面），相鄰兩圈之間接成四邊形；頭尾各收成一個尖點。
    power 越大截面越方（2 = 橢圓）：獅子的身體截面是上寬下圓的「蛋形方塊」。"""
    verts, faces = [], []
    rows = list(profile)
    # 頭尾各多加一圈縮小的，讓兩端圓圓地收起來（不是平平的切口）
    y0, t0, b0, w0 = rows[0]; y1, t1, b1, w1 = rows[-1]
    zc0, zc1 = (t0 + b0) / 2, (t1 + b1) / 2
    rows = [(y0 - 0.035, zc0 + (t0 - zc0) * 0.6, zc0 - (zc0 - b0) * 0.6, w0 * 0.6)] + rows + \
           [(y1 + 0.035, zc1 + (t1 - zc1) * 0.6, zc1 - (zc1 - b1) * 0.6, w1 * 0.6)]
    for y, top, bot, w in rows:
        zc, h = (top + bot) / 2, (top - bot) / 2
        for k in range(ring_n):
            a = 2 * math.pi * k / ring_n
            c, s = math.cos(a), math.sin(a)
            x = w * math.copysign(abs(c) ** (2 / power), c)
            z = zc + h * math.copysign(abs(s) ** (2 / power), s)
            verts.append((x, y, z))
    n_rows = len(rows)
    for r in range(n_rows - 1):
        for k in range(ring_n):
            a, b = r * ring_n + k, r * ring_n + (k + 1) % ring_n
            faces.append((a, b, b + ring_n, a + ring_n))
    # 兩端的尖點（三角扇形，從中心放射）
    for end, r in ((0, 0), (1, n_rows - 1)):
        y, top, bot, w = rows[r]
        verts.append((0, y + (-0.02 if end == 0 else 0.02), (top + bot) / 2))
        pole = len(verts) - 1
        for k in range(ring_n):
            a, b = r * ring_n + k, r * ring_n + (k + 1) % ring_n
            faces.append((b, a, pole) if end == 0 else (a, b, pole))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    # 統一法線朝外（Ctrl+N）：面的頂點順序決定法線方向，手排的順序可能整個朝內。
    # 朝內的話，引擎會把它當背面剔除（看不到身體），用法線算的深淺也會上下顛倒（v005 就是這樣）
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    return o

body = loft("Body", PROFILE)
put(body, "Body", (1, 1, 1), (0, 0, 0), SKIN, mask=MASK_PRIMARY)
# 背脊比較深：朝上的面 shade 小一點（finalize 會把色槽通道乘上它）
shade = body.data.attributes.new("shade", 'FLOAT', 'POINT')
for v in body.data.vertices:
    t = max(0.0, min(1.0, (v.normal.z - 0.3) / 0.6))
    shade.data[v.index].value = 1.0 - 0.15 * t * t * (3 - 2 * t)
# 淺色的下巴、喉嚨、胸口、肚子：一條連續的漸層（v005 用兩顆橢球，變成「白－橘－白」斷成兩半）
# light = 0 用原本的色槽、1 = 副色（finalize 會混合）。朝下的面、和胸口前面偏下的面變淺
light = body.data.attributes.new("light", 'FLOAT', 'POINT')
def sstep(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)
for v in body.data.vertices:
    n, co = v.normal, v.co
    under = sstep(-0.15, -0.6, n.z)
    front = sstep(-0.3, -0.75, n.y) * sstep(1.0, 0.8, co.z)
    light.data[v.index].value = max(under, front)

# ---------- 腿：曲線＋倒角，經過關節點（保留 v002 的腿，按 Q 版縮短） ----------
def leg(side, ctrl, radii, bevel):
    pts = smooth_path([Vector((c[0] * side, c[1], c[2])) for c in ctrl], n_per=3)
    rr = []
    for i in range(len(pts)):
        u = i / (len(pts) - 1) * (len(radii) - 1)
        k = min(int(u), len(radii) - 2)
        rr.append(radii[k] + (radii[k + 1] - radii[k]) * (u - k))
    rr[0] *= 0.6                                    # 最上端收小：藏在身體裡
    return curve("Leg", pts, rr, bevel, SKIN, round_steps=3, mask=MASK_PRIMARY)

for s in (1, -1):
    # 前腳：肩（藏在胸裡）→ 肘 → 腕 → 腳掌，幾乎直直往下
    leg(s, [(LEG_X, -0.24, 0.55), (LEG_X, -0.24, 0.36), (LEG_X, -0.22, 0.15), (LEG_X, FRONT_Y - 0.02, 0.07)],
        [1.45, 1.15, 0.92, 0.86], 0.10)                 # v006：前腳更粗（獅子的前腳最有力）
    # 後腳：髖 → 膝（往前）→ 踝（往後）→ 腳掌：貓科後腳的「Z 字」
    leg(s, [(LEG_X, 0.36, 0.56), (LEG_X, 0.30, 0.38), (LEG_X, 0.44, 0.20), (LEG_X, HIND_Y + 0.02, 0.07)],
        [1.7, 1.2, 0.88, 0.84], 0.10)
    # 肩膀、大腿的肌肉：參考模型最明顯的起伏，也把腿頂包住 → 身體和腿沒有縫
    # v006：肩膀更大、往外往前頂出（肩胛骨的隆起），大腿更厚 → 看得出肌肉
    sphere("Haunch", (LEG_X * 1.1 * s, -0.25, 0.53), (0.14, 0.16, 0.19), (0, -10 * s, 0), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("Haunch", (LEG_X * 1.05 * s, 0.36, 0.53), (0.15, 0.19, 0.19), color=SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    for y in (FRONT_Y, HIND_Y):
        # v007：v006 把腳掌放大，但肉球還用舊的高度 → 整顆埋進腳掌裡看不到。
        # 肉球的高度改成「跟著腳掌的大小算」：放在橢球腳底的表面上（橢球公式算出該前後位置的底部高度）
        PAW = Vector((0.105, 0.12, 0.065))
        paw_c = Vector((LEG_X * s, y - 0.03, PAW.z))           # 腳底剛好貼地（Z = 0）
        def sole(dx, dy):
            return paw_c + Vector((dx, dy, -PAW.z * math.sqrt(max(0.0, 1 - (dx / PAW.x) ** 2 - (dy / PAW.y) ** 2)) + 0.002))
        sphere("Paw", paw_c, PAW, color=FLESH, seg=12, rings=6, mask=MASK_SECONDARY)
        sphere("Pad", sole(0, 0.018), (0.04, 0.036, 0.009), color=PINK, seg=6, rings=3, mask=MASK_PINK)
        for dx in (-0.033, 0.0, 0.033):
            sphere("Pad", sole(dx, -0.055 + abs(dx) * 0.4), (0.017, 0.017, 0.009),
                   color=PINK, seg=6, rings=3, mask=MASK_PINK)

# ---------- 尾巴：細長往下垂、末端深色毛球（參考模型） ----------
# v007：尾巴根部往身體裡多插一截（v006 的起點剛好在屁股表面外面，看得到縫）
tail = smooth_path([Vector((0, 0.44, 0.70)), Vector((0, 0.52, 0.74)), Vector((0, 0.62, 0.62)), Vector((0, 0.68, 0.42)), Vector((0, 0.74, 0.30))], n_per=4)
curve("Tail", tail, [1.0 - 0.4 * i / (len(tail) - 1) for i in range(len(tail))], 0.034, SKIN, round_steps=2, mask=MASK_PRIMARY)
sphere("TailTuft", tail[-1] + Vector((0, 0.015, -0.015)), (0.05, 0.065, 0.06), (20, 0, 0), FUR, seg=10, rings=6, mask=MASK_TUFT)

# ---------- 頭：幼體的臉 × 1.1 ----------
sphere("Head", HEAD_C, HEAD_HALF, color=SKIN, seg=24, rings=12, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Eye",      F(0.12 * s, -0.545, 0.74), Vector((0.055, 0.03, 0.075)) * S, (0, 0, 22 * s), INK)
    sphere("EyeShine", F(0.12 * s - 0.025, -0.575, 0.775), Vector((0.02, 0.012, 0.02)) * S, (0, 0, 22 * s), WHITE, seg=10, rings=6)
    # 大圓耳（耳背深色）＋淺色內耳
    sphere("Ear",      F(0.225 * s, -0.25, 0.955), Vector((0.11, 0.045, 0.10)) * S, (0, 28 * s, -10 * s), SKIN, seg=12, rings=6, mask=MASK_EARBACK)
    sphere("EarInner", F(0.225 * s, -0.285, 0.95), Vector((0.075, 0.02, 0.065)) * S, (0, 28 * s, -10 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)
    tear = [F(0.088 * s, -0.562, 0.705), F(0.072 * s, -0.592, 0.682), F(0.058 * s, -0.622, 0.668)]
    curve("TearMark", tear, [1.0, 0.8, 0.5], 0.0055 * S, ROSE, mask=MASK_MARK)

MZ_FRONT = -0.635
sphere("Snout", F(0, -0.565, 0.668), Vector((0.115, 0.072, 0.074)) * S, color=SKIN, seg=16, rings=8, mask=MASK_PRIMARY)  # 參考：口鼻寬
bridge = [F(0, -0.548 - 0.068 * (i / 6) ** 1.3, 0.800 - 0.115 * (i / 6)) for i in range(7)]
curve("Bridge", bridge, [0.45, 0.6, 0.72, 0.84, 0.95, 1.0, 0.55], 0.040 * S, SKIN, round_steps=3, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Muzzle", F(0.052 * s, MZ_FRONT + 0.022, 0.640), Vector((0.064, 0.044, 0.046)) * S, (0, 0, 18 * s), FLESH, seg=12, rings=6, mask=MASK_SECONDARY)
sphere("Chin", F(0, MZ_FRONT + 0.035, 0.592), Vector((0.045, 0.032, 0.03)) * S, color=FLESH, seg=10, rings=6, mask=MASK_SECONDARY)
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.052 * S, radius2=0.022 * S, depth=0.03 * S, location=F(0, MZ_FRONT - 0.004, 0.684))
nose = put(bpy.context.active_object, "Nose", (0.95, 0.7, 1.2), (0, 0, 0), ROSE, mask=MASK_ROSE)
nose.rotation_mode = 'QUATERNION'
nose.rotation_quaternion = Quaternion((1, 0, 0), math.radians(18)) @ Euler([math.radians(a) for a in (90, 90, 0)]).to_quaternion()

# 嘴：ω 形，獨立物件（吃果子動畫）
W, D = 0.042 * S, 0.014 * S
pts, radii = [], []
for i in range(13):
    u = -1 + 2 * i / 12
    pts.append(Vector((W * u, 0.018 * S * u * u, -D * math.sin(math.pi * abs(u)))))
    radii.append(1.0 - 0.35 * abs(u))
curve("Mouth", pts, radii, 0.0065 * S, INK).location = F(0, MZ_FRONT + 0.012, 0.612)

# ---------- v006 鬃毛圈：成獅那一圈毛茸茸的毛，框住整張臉（metaball，點綴色＝較深的毛） ----------
# 只在臉的周圍一圈，不包後腦和後頸（v001 包住後腦，組長說很醜）。
# 圈放在耳朵根部後面一點：從正面看，耳朵從鬃毛圈上冒出來。
# 毛球間距 ÷ 半徑 ≈ 1.7：比羊毛的 2.4 密 → 毛球融成一圈、但邊緣還是一團一團的蓬鬆感。
mb = bpy.data.metaballs.new("ManeCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.024, 0.02, 0.6
mane = bpy.data.objects.new("ManeCloud", mb)
mane["mesh_name"] = "Mane"
mane["mask"] = (0, 0, 1, 1)
bpy.context.scene.collection.objects.link(mane)
mane.color = FUR
K = 0.574
def ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0
MANE_Y = HEAD_C.y + 0.10                           # 圈的位置：頭中心往後 10 公分
for row, (grow, r0, dy) in enumerate(((1.0, 0.085, 0.0), (1.13, 0.068, 0.07))):   # 內圈大毛球、外圈往後一點的小毛球
    rx, rz = 0.33 * grow, 0.31 * grow
    n = round(2 * math.pi * (rx + rz) / 2 / (r0 * 1.7))
    for k in range(n):
        a = 2 * math.pi * (k + 0.5 * row) / n       # 外圈錯開半格 → 毛球交錯
        r = r0 * (1.0 if k % 2 == 0 else 0.85)      # 大小交錯 → 不會像一圈整齊的珠子
        ball(Vector((rx * math.sin(a), MANE_Y + dy, HEAD_C.z + rz * math.cos(a))), r)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅成體 v006 完成")
