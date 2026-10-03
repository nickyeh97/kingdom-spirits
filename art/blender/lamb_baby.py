# 小羊（幼體）完整腳本 v3
# 用法：先 File → Save As 另存新檔；Scripting → New → 貼上 → ▶。會清空場景後重建。
import bpy, math
from mathutils import Vector

# ---------- 可調參數 ----------
WOOL  = (0.96, 0.93, 0.86, 1)   # 羊毛
FACE  = (1.00, 0.95, 0.90, 1)   # 臉、腳
BLUSH = (0.95, 0.55, 0.65, 1)   # 臉頰
INNER = (0.92, 0.55, 0.60, 1)   # 內耳
INK   = (0.12, 0.12, 0.18, 1)   # 眼睛、鼻子、嘴、蹄
WHITE = (1, 1, 1, 1)

HEAD_C = Vector((0, -0.30, 0.72))                # 頭（沿用第 1 課）
HEAD_HALF = Vector((0.30, 0.276, 0.285))
BODY_C = Vector((0, 0.06, 0.42))                 # 身體：比之前更圓
BODY_HALF = Vector((0.33, 0.36, 0.30))
HOOD_PUFF = 1.13       # 毛帽比頭大多少（包住臉的那一圈厚度）
FACE_WINDOW = 0.88     # 臉露出來的「窗口」大小（越大臉露越多）
# ------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)

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

# ---------- 頭與五官（眼睛、耳朵沿用第 2、3 課） ----------
sphere("Head", HEAD_C, HEAD_HALF, color=FACE, seg=24, rings=12)
for s in (1, -1):
    sphere("Eye",      (0.12 * s,         -0.545, 0.74),  (0.055, 0.03, 0.075), (0, 0, 22 * s), INK)
    sphere("EyeShine", (0.12 * s - 0.025, -0.575, 0.775), (0.02, 0.012, 0.02),  (0, 0, 22 * s), WHITE)
    sphere("Cheek",    (0.20 * s,         -0.50,  0.64),  (0.05, 0.015, 0.035), (0, 0, 42 * s), BLUSH)
    # 耳朵形狀與角度沿用第 3 課，只往外移，讓它從毛帽裡伸出來
    sphere("Ear",      (0.42 * s, -0.27, 0.76), (0.15, 0.07, 0.06),  (0, 30 * s, -15 * s), FACE)
    sphere("EarInner", (0.43 * s, -0.31, 0.75), (0.11, 0.03, 0.035), (0, 30 * s, -15 * s), INNER)

# 鼻子：小小的倒三角（羊的鼻子是 Y 字形，不是豬的圓盤）
sphere("Nose", (0, -0.578, 0.668), (0.032, 0.018, 0.020), color=INK)

# 嘴：獨立物件，原點就在嘴的位置 → 之後做「吃果子」動畫時，
#     只要把 Mouth 的 Scale Z 從 0.008 動到 0.04，嘴就會張開
mouth = sphere("Mouth", (0, -0.568, 0.622), (0.028, 0.012, 0.008), color=INK)
sphere("MouthLine", (0, -0.574, 0.645), (0.005, 0.006, 0.02), color=INK)   # 人中：鼻子連到嘴

# ---------- 腳 ----------
for s in (1, -1):
    for y in (-0.08, 0.20):
        cylinder("Leg",  (0.15 * s, y, 0.12), 0.06, 0.20, FACE)
        cylinder("Hoof", (0.15 * s, y, 0.03), 0.065, 0.06, INK)

# ---------- 羊毛（metaball） ----------
mb = bpy.data.metaballs.new("WoolCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.022, 0.018, 0.6
wool = bpy.data.objects.new("WoolCloud", mb)
bpy.context.scene.collection.objects.link(wool)
wool.color = WOOL

# Metaball 的「半徑」不等於看到的大小：threshold 0.6、stiffness 2 時，
# 實際表面只有 radius × 0.574（在容器裡實測）。所以下面都先除以 K，
# 讓我們寫的數字 = 眼睛看到的大小。
K = 0.574

def ball(co, r):
    e = mb.elements.new(type='BALL')
    e.co, e.radius, e.stiffness = co, r / K, 2.0
    return e

def ellipsoid(co, half, negative=False, stiffness=2.0):
    e = mb.elements.new(type='ELLIPSOID')
    e.co, e.radius, e.stiffness = co, 0.3, stiffness
    e.size_x, e.size_y, e.size_z = half / (0.3 * K)
    e.use_negative = negative          # 負元素 = 把附近的毛「挖掉」
    return e

def in_face_window(p):
    """p 是否落在臉的正前方（要露出臉的區域）。"""
    q = p - HEAD_C
    return q.y < -0.12 and (q.x / 0.24) ** 2 + ((q.z + 0.03) / 0.22) ** 2 < FACE_WINDOW ** 2

def ring(center, half, z_frac, count, r, offset=0.0):
    """在橢球某個高度（z_frac：-1 底、0 腰、+1 頂）繞一圈，等距放 count 顆毛球。"""
    rr = math.sqrt(max(0.0, 1 - z_frac * z_frac))
    for i in range(count):
        a = 2 * math.pi * (i + offset) / count
        p = center + Vector((half.x * rr * math.cos(a), half.y * rr * math.sin(a), half.z * z_frac))
        if not in_face_window(p):
            ball(p, r)

# 1) 身體：圓滾滾的核心 ＋ 三圈「等距」的毛球 → 整齊的雲朵花邊
ellipsoid(BODY_C, BODY_HALF)
ring(BODY_C, BODY_HALF, 0.55, 10, 0.10, offset=0.5)
ring(BODY_C, BODY_HALF, 0.0, 12, 0.11)
ring(BODY_C, BODY_HALF, -0.5, 10, 0.10, offset=0.5)
ball(BODY_C + Vector((0, 0, BODY_HALF.z)), 0.12)            # 背頂
ball(BODY_C + Vector((0, BODY_HALF.y, 0.05)), 0.09)         # 尾巴

# 2) 毛帽：比頭大一圈的殼，把下巴整圈包住；再用負元素在正面挖出臉的窗口
ellipsoid(HEAD_C, HEAD_HALF * HOOD_PUFF)
for zf, n, off in ((0.8, 6, 0.0), (0.45, 10, 0.5), (0.0, 12, 0.0), (-0.5, 10, 0.5)):
    ring(HEAD_C, HEAD_HALF * HOOD_PUFF, zf, n, 0.075, off)  # 毛帽上的捲毛
ellipsoid(HEAD_C + Vector((0, -HEAD_HALF.y * 1.0, -0.03)),  # 臉的窗口（負元素）
          Vector((0.24, 0.16, 0.22)) * FACE_WINDOW, negative=True, stiffness=4.0)

# ---------- 視窗用物件顏色顯示 ----------
# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小羊 v3 完成")
