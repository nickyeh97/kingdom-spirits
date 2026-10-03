# 小羊（成體，階段 3–4）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Lamb_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 跟幼體的差別都集中在「比例參數」；五官全部改成「相對於頭」的位置，頭怎麼移、怎麼縮，臉都跟著走。
import bpy, math
from mathutils import Vector

# ---------- 顏色（與幼體相同） ----------
WOOL  = (0.96, 0.93, 0.86, 1)
FACE  = (1.00, 0.95, 0.90, 1)
BLUSH = (0.95, 0.55, 0.65, 1)
INNER = (0.92, 0.55, 0.60, 1)
HORN  = (0.93, 0.80, 0.55, 1)
INK   = (0.12, 0.12, 0.18, 1)
WHITE = (1, 1, 1, 1)

# ---------- 比例：長大 = 改這幾個數字 ----------
#                幼體                     成體
HEAD_SCALE = 0.92                        # 1.0  → 0.92：頭本身只小一點點
HEAD_C = Vector((0, -0.46, 1.10))        # (0,-0.30,0.72) → 抬高、往前：有了脖子
BODY_C = Vector((0, 0.10, 0.66))         # (0,0.06,0.42)  → 抬高（腿變長）
BODY_HALF = Vector((0.36, 0.50, 0.33))   # (0.33,0.36,0.30) → 身體變長、變大
LEG_LEN, LEG_R = 0.42, 0.07              # 0.20, 0.06 → 腿長一倍
LEG_X, LEG_Y = 0.18, (-0.22, 0.38)       # 0.15, (-0.08, 0.20)
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
bpy.context.scene["spirit_name"] = "Lamb_Adult"   # 給收尾腳本用的輸出名稱

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

# ---------- 新技巧：用曲線做捲角 ----------
HORN_CENTER = (0.40, 0.24, 0.08)   # 螺旋中心（幼體臉座標）：在頭側「偏後方」→ 整個捲角往後長
HORN_R0 = 0.19                     # 第一圈的半徑
HORN_TURNS = 1.25                  # 捲幾圈

def horn(side):
    """羊角 = 一條沿著「螺旋」走的曲線，再給它粗細（bevel）。
    螺旋：角度 θ 一直轉，半徑 r 一直縮 → 越捲越小。
    角根貼在毛帽表面，之後很快往外（x）移出來，整個螺旋「貼在頭的側面」而不是插進頭裡。"""
    cu = bpy.data.curves.new("Horn", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.07 * f           # 角的粗細（根部）
    cu.bevel_resolution = 3              # 截面的圓滑度
    cu.resolution_u = 6                  # 沿著曲線的圓滑度
    cu.use_fill_caps = True              # 末端封口
    sp = cu.splines.new('POLY')
    N = 28
    sp.points.add(N - 1)
    cx, cy, cz = HORN_CENTER
    for i in range(N):
        t = i / (N - 1)
        theta = math.radians(150) - t * HORN_TURNS * 2 * math.pi   # 角根在頭頂偏前 → 往上往後拱 → 往下 → 往內捲，尖端停在後方
        r = HORN_R0 * (1 - 0.7 * t)
        x = cx - 0.16 * (1 - t) ** 3                                 # 角根接在毛帽上，很快就移到頭的外側
        p = face(x * side, cy + r * math.cos(theta), cz + r * math.sin(theta))
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = 1.0 - 0.7 * t      # 越往末端越細
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

# 1) 身體：成體比幼體大一圈，但保留「一顆一顆半圓」的花邊——
#    關鍵是「間距 ÷ 半徑」：毛帽約 2.5，所以顆粒分明；
#    太擠（< 2）力場互相疊加，就會融成一整片光滑的雲，看不出顆粒。
#    所以每圈放幾顆不再手寫，改由「這圈多長 ÷ 想要的間距」算出來。
WOOL_PUFF = 1.06   # 毛比身體膨多少（幼體 1.0）
GAP = 2.4          # 間距 ÷ 半徑（越大顆粒越分明）
BH = BODY_HALF * WOOL_PUFF
ellipsoid(BODY_C, BH * 0.92)
for zf, r, off in ((0.85, 0.11, 0.0), (0.55, 0.12, 0.5), (0.2, 0.13, 0.0), (-0.15, 0.13, 0.5), (-0.5, 0.11, 0.0)):
    rr = math.sqrt(1 - zf * zf)
    a_, b_ = BH.x * rr, BH.y * rr
    circ = math.pi * (3 * (a_ + b_) - math.sqrt((3 * a_ + b_) * (a_ + 3 * b_)))   # 橢圓周長（Ramanujan 近似）
    n = max(5, round(circ / (GAP * r)))
    ring(BODY_C, BH, zf, n, r, off)                          # 五圈交錯的半圓花邊
ball(BODY_C + Vector((0, BH.y, 0.08)), 0.11)                 # 尾巴

# 2) 新：脖子——從身體前上方連到頭後方，一串漸漸變小的毛球
neck_from = BODY_C + Vector((0, -BODY_HALF.y * 0.55, BODY_HALF.z * 0.55))
neck_to = HEAD_C + Vector((0, 0.12, -0.10))
for i in range(5):
    t = i / 4
    ball(neck_from.lerp(neck_to, t), 0.17 - 0.03 * t)

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
print("小羊成體完成")
