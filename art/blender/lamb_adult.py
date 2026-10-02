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
    sphere("Ear",      face(0.42 * s,  0.03, 0.04),  Vector((0.15, 0.07, 0.06)) * f,  (0, 30 * s, -15 * s), FACE)
    sphere("EarInner", face(0.43 * s, -0.01, 0.03),  Vector((0.11, 0.03, 0.035)) * f, (0, 30 * s, -15 * s), INNER)
sphere("Nose",      face(0, -0.278, -0.052), Vector((0.032, 0.018, 0.020)) * f, color=INK)
sphere("Mouth",     face(0, -0.268, -0.098), Vector((0.028, 0.012, 0.008)) * f, color=INK)
sphere("MouthLine", face(0, -0.274, -0.075), Vector((0.005, 0.006, 0.02)) * f,  color=INK)

# ---------- 腳：變長 ----------
for s in (1, -1):
    for y in LEG_Y:
        cylinder("Leg",  (LEG_X * s, y, LEG_LEN / 2 + 0.03), LEG_R, LEG_LEN, FACE)
        cylinder("Hoof", (LEG_X * s, y, 0.035), LEG_R + 0.006, 0.07, INK)

# ---------- 新技巧：用曲線做捲角 ----------
def horn(side):
    """羊角 = 一條沿著「螺旋」走的曲線，再給它粗細（bevel）。
    螺旋：角度 θ 一直轉，半徑 r 一直縮 → 越捲越小；同時慢慢往外（x）移，才不會捲回頭裡。"""
    cu = bpy.data.curves.new("Horn", 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.075 * f          # 角的粗細（根部）
    cu.bevel_resolution = 3              # 截面的圓滑度
    cu.resolution_u = 8                  # 沿著曲線的圓滑度
    cu.use_fill_caps = True              # 末端封口
    sp = cu.splines.new('POLY')
    N = 24
    sp.points.add(N - 1)
    turns, R0 = 1.2, 0.20 * f
    center = face(0.32 * side, 0.0, 0.14)          # 螺旋中心：頭兩側、耳朵上方偏後（要在毛帽外面）
    for i in range(N):
        t = i / (N - 1)
        theta = math.radians(140) - t * turns * 2 * math.pi  # 從頭頂偏前（埋在毛裡）開始，往後、往下、再往前捲
        r = R0 * (1 - 0.65 * t)
        p = center + Vector((side * (0.10 * t - 0.06) * f, r * math.cos(theta), r * math.sin(theta)))
        sp.points[i].co = (p.x, p.y, p.z, 1)
        sp.points[i].radius = 1.0 - 0.75 * t      # 越往末端越細
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

# 1) 身體：同樣三圈花邊，身體變長了，每圈多放幾顆
ellipsoid(BODY_C, BODY_HALF)
ring(BODY_C, BODY_HALF, 0.55, 12, 0.11, offset=0.5)
ring(BODY_C, BODY_HALF, 0.0, 14, 0.12)
ring(BODY_C, BODY_HALF, -0.5, 12, 0.11, offset=0.5)
ball(BODY_C + Vector((0, 0, BODY_HALF.z)), 0.13)
ball(BODY_C + Vector((0, BODY_HALF.y, 0.08)), 0.10)          # 尾巴

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

for area in (bpy.context.screen.areas if bpy.context.screen else []):
    if area.type == 'VIEW_3D':
        area.spaces.active.shading.color_type = 'OBJECT'
print("小羊成體完成")
