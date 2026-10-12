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
from mathutils import Vector, Quaternion, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
SKIN  = (0.96, 0.70, 0.32, 1)   # 主色：身體的皮（金黃）
FLESH = (1.00, 0.82, 0.74, 1)   # 副色：可愛的肉色
FUR   = (0.82, 0.48, 0.22, 1)   # 點綴色：頭頂毛、兩頰毛、尾巴毛球
PINK  = (0.96, 0.60, 0.65, 1)   # 固定色：腮紅、肉球
ROSE  = (0.42, 0.24, 0.24, 1)   # 固定色：鼻子（參考照片：深色、寬寬的）
SPOT  = (0.80, 0.55, 0.25, 1)   # 斑點（主色的深色）
INK   = (0.12, 0.12, 0.18, 1)   # 固定色：眼睛、嘴
WHITE = (1, 1, 1, 1)

# 配色遮罩（finalize_export.py 讀 o["mask"]）：A=0 表示固定色，RGB 就是顏色本身
# 注意：Head、Leg、Ear、EarInner 這些名字在小羊身上是「臉的顏色／點綴色」，
# 小獅要的是主色（皮）與副色（肉色），所以在物件上直接指定，不靠名稱對照表
MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_PINK = (0.96, 0.60, 0.65, 0)
# 斑點：主色通道給 0.72 ＝「皮的顏色的 72% 亮度」→ 比皮深一點，換配色時跟著變（跟披風內襯同一招）
MASK_SPOT = (0.72, 0, 0, 1)
MASK_MARK = (0.30, 0.18, 0.16, 0)   # 固定色：淚痕（眼角往下的深色線）
MASK_ROSE = (0.42, 0.24, 0.24, 0)

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

def curve(name, pts, radii, bevel, color, round_steps=1):
    """曲線＋倒角（跟小羊的角同一招）：pts 是路徑，radii 是每一點的粗細倍率。"""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = bevel
    cu.bevel_resolution = round_steps        # 截面的圓滑度（1 = 六角形，3 = 接近圓）
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
    # （v003 拿掉腮紅：組長要求）
    # 大圓耳：參考照片的幼獅耳朵又大又圓、長在頭頂兩側偏外 → 比 v001 大一圈、往外移
    sphere("Ear",      (0.225 * s, -0.25, 0.955), (0.11, 0.045, 0.10), (0, 28 * s, -10 * s), SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
    sphere("EarInner", (0.225 * s, -0.285, 0.95), (0.075, 0.02, 0.065), (0, 28 * s, -10 * s), FLESH, seg=10, rings=6, mask=MASK_SECONDARY)
    # 淚痕：從內眼角往下、沿著鼻樑兩側一路到肉墊上方的深色細線——幼獅臉上最有辨識度的記號
    tear = [Vector((0.088 * s, -0.562, 0.705)), Vector((0.072 * s, -0.592, 0.682)), Vector((0.058 * s, -0.622, 0.668))]
    curve("TearMark", tear, [1.0, 0.8, 0.5], 0.0055, ROSE)["mask"] = MASK_MARK

# ---------- 口鼻的立體感（v003，參考照片的側面體積） ----------
# 照片裡的口鼻是一整塊往前凸的「台」：
#   鼻樑從兩眼之間開始，越往下越寬，一路接到鼻頭；鼻頭在台的最前端；
#   鼻子下面才分成左右兩顆肉墊，再往下是小下巴。
# 用三層來堆：①口鼻台（主體）②鼻樑（上面的稜線）③肉墊＋下巴（下面的兩顆圓）
MZ_FRONT = -0.635                     # 口鼻最前面的位置（臉的表面約在 −0.55，往前凸約 8.5 公分）

# ① 口鼻台：一顆前後拉長的橢球，從臉裡面長出來（主色＝皮，跟照片一樣是毛的顏色）
sphere("Snout", (0, -0.565, 0.668), (0.095, 0.07, 0.072), color=SKIN, seg=16, rings=8, mask=MASK_PRIMARY)

# ② 鼻樑：一條從兩眼之間往下、往前的稜線。用曲線＋倒角（跟羊角、尾巴同一招），
#    每一點的粗細從上往下變寬 → 上窄下寬，像照片裡的鼻樑接到寬寬的鼻頭
bridge = []
for i in range(7):
    t = i / 6
    bridge.append(Vector((0, -0.548 - 0.068 * t ** 1.3, 0.800 - 0.115 * t)))
# 粗細：上端細、往下變寬，最後一點收小 → 末端圓圓地收進鼻子後面，不會露出平平的切口
radii = [0.45, 0.6, 0.72, 0.84, 0.95, 1.0, 0.55]
curve("Bridge", bridge, radii, 0.040, SKIN, round_steps=3)["mask"] = MASK_PRIMARY

# ③ 鬍鬚肉墊：在鼻頭下方、口鼻台的前下側，左右兩顆蓬蓬的圓（副色＝肉色）
for s in (1, -1):
    sphere("Muzzle", (0.046 * s, MZ_FRONT + 0.022, 0.640), (0.055, 0.042, 0.044), (0, 0, 18 * s), FLESH, seg=12, rings=6)
sphere("Chin", (0, MZ_FRONT + 0.035, 0.592), (0.04, 0.032, 0.03), color=FLESH, seg=10, rings=6)

# 鼻子：寬寬的倒三角形，蓋在鼻樑最下端、口鼻台的最前面。
# 圓錐給 3 個頂點就是三角形。旋轉：先繞 X 轉 90° 讓圓錐的軸朝前（−Y），這時三角形有一個角朝 +X（側邊）；
# 再繞 Y 轉 90°，把那個角轉到正下方 → 倒三角。
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.052, radius2=0.022, depth=0.03,
                                location=(0, MZ_FRONT - 0.004, 0.684))
nose = put(bpy.context.active_object, "Nose", (0.95, 0.7, 1.2), (90, 90, 0), ROSE, mask=MASK_ROSE)
# 再整個繞世界 X 軸往下傾 18°，順著鼻樑的斜度。
# 注意不能直接把 90 改成 72：歐拉角是「依序」旋轉，先轉的會影響後轉的軸，結果鼻子會歪到側邊；
# 用四元數「在現有旋轉外面再乘一個旋轉」才是繞世界軸。
nose.rotation_mode = 'QUATERNION'
nose.rotation_quaternion = Quaternion((1, 0, 0), math.radians(18)) @ Euler([math.radians(a) for a in (90, 90, 0)]).to_quaternion()

# 額頭的小斑紋：照片裡幼獅額頭有一些深色的小點（點綴在毛帽前面）
# 跟身體的斑點同一招：算出頭表面上的點和法線，讓小圓片貼著皮（v002 初版直接寫座標，結果浮在頭前面）
def on_ellipsoid(c, h, d, sink=0.99):
    p = c + Vector((h.x * d.x, h.y * d.y, h.z * d.z)) * sink
    n = Vector((d.x / h.x, d.y / h.y, d.z / h.z)).normalized()
    return p, n

def spot(c, h, d, r):
    p, n = on_ellipsoid(c, h, Vector(d).normalized())
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=1, location=p)
    o = put(bpy.context.active_object, "Spot", (r, r, 0.007), (0, 0, 0), SPOT, mask=MASK_SPOT)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(n)   # 圓片的薄邊朝外 → 貼在皮上
    return o

for d, r in (((0.0, -0.55, 0.83), 0.016), ((-0.13, -0.58, 0.80), 0.013), ((0.13, -0.58, 0.80), 0.013),
             ((-0.06, -0.66, 0.74), 0.011), ((0.06, -0.66, 0.74), 0.011)):
    spot(HEAD_C, HEAD_HALF, d, r)

# 嘴：貓科的「ω」形（兩個往下的小彎）。獨立物件、原點在嘴中央 → 吃果子動畫動 Scale Z 就會張嘴
W, D = 0.042, 0.014
origin = Vector((0, MZ_FRONT + 0.012, 0.612))
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

# 身體的斑點：幼獅身上淡淡的斑點（比皮深一點的同色系）。
# 方法：在身體橢球表面上取點、放一顆壓扁的小圓片，讓它朝向表面的法線方向（第 2 課眼睛貼合臉的原理）。
# 橢球的法線 = (x/a², y/b², z/c²) 正規化 —— 寫在上面的 on_ellipsoid() 裡
SPOTS = [  # (方向 x, y, z, 大小) —— 左右錯開、不對稱，看起來比較自然
    (0.55, -0.20, 0.80, 0.040), (0.75, 0.25, 0.60, 0.034), (0.45, 0.55, 0.70, 0.030), (0.85, -0.15, 0.25, 0.028),
    (-0.50, -0.05, 0.85, 0.036), (-0.78, 0.35, 0.50, 0.032), (-0.40, 0.62, 0.66, 0.028), (-0.86, -0.25, 0.30, 0.026),
    (0.10, 0.30, 0.95, 0.030), (-0.15, 0.70, 0.70, 0.026),
]
for dx, dy, dz, r in SPOTS:
    spot(BODY_C, BODY_HALF, (dx, dy, dz), r)

# ---------- 腳（位置跟小羊幼體相同）＋ 圓腳掌＋肉球 ----------
for s in (1, -1):
    for y in LEG_Y:
        # 腿往上延伸插進身體裡（v001 腿頂剛好碰到身體表面，所以看得到接縫）。
        # 關節位置（腿的中心線、地面）不變，跟小羊共用骨架不受影響，只是網格多藏一截在身體裡。
        cylinder("Leg", (LEG_X * s, y, LEG_Z + 0.05), LEG_R, LEG_LEN + 0.10, SKIN)["mask"] = MASK_PRIMARY
        # 肩膀／大腿：腿頂一顆圓圓的肉，把腿和身體圓滑地接起來（前腿是肩膀、後腿是大腿）
        thigh = (0.095, 0.11, 0.10) if y > 0 else (0.085, 0.095, 0.095)
        sphere("Haunch", (LEG_X * s, y, 0.27), thigh, color=SKIN, seg=12, rings=6, mask=MASK_PRIMARY)
        # 圓腳掌：比腿粗一點、往前一點，底部貼地
        paw_c = Vector((LEG_X * s, y - 0.015, 0.05))
        sphere("Paw", paw_c, (0.075, 0.085, 0.05), color=FLESH, seg=12, rings=6)
        # 肉球：腳底一顆大的掌墊＋前面三顆小趾墊。揮手時腳底朝前，就看得到
        sphere("Pad", paw_c + Vector((0, 0.012, -0.046)), (0.034, 0.028, 0.008),
               color=PINK, seg=8, rings=4, mask=MASK_PINK)
        for dx in (-0.03, 0.0, 0.03):
            sphere("Pad", paw_c + Vector((dx, -0.045 + abs(dx) * 0.4, -0.04)), (0.014, 0.014, 0.008),
                   color=PINK, seg=8, rings=4, mask=MASK_PINK)

# ---------- 尾巴：Q 版的捲尾巴 ----------
# 像畫筆一樣「一邊走、一邊轉彎」：每一步往目前的方向走一小段，方向角 θ 一直增加，
# 步伐越走越短 → 先往後、往上翹，最後往前捲成一個小圈（像問號）。
tail_pts, tail_r = [], []
p = BODY_C + Vector((0, BODY_HALF.y * 0.92, 0.04))
theta = math.radians(-5)                    # 0° = 往後（+Y），90° = 往上（+Z）
N = 16
for i in range(N):
    t = i / (N - 1)
    tail_pts.append(p.copy())
    tail_r.append(1.0 - 0.25 * t)
    step = 0.045 * (1.0 - 0.45 * t)          # 越走越短 → 捲起來
    theta += math.radians(15)                # 每一步轉 15°，總共轉約 225°
    p += Vector((0, math.cos(theta), math.sin(theta))) * step
curve("Tail", tail_pts, tail_r, 0.036, SKIN)
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
for co, r in ((tail_tip, 0.055), (tail_tip + Vector((0, -0.025, -0.02)), 0.04)):
    ball(co, r)

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小獅幼體完成")
