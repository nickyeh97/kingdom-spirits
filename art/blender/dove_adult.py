# 小鴿（成體，階段 3）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Dove_Adult.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# 設計（見 art/briefs/Dove_Baby.md，色槽 2026-10-21 組長確認）：
#  - 跟小羊、小獅成體同一個高度級距：頭抬高到約 1.1 公尺、頭本身縮一點點
#  - 長大的差別：頭頂絨毛褪掉（頭變光滑）、胸口挺起來（鴿子招牌的圓胸）、
#    翅膀變成完整的收翅（看得到一根根飛羽）、尾巴變長、扇開五根
#  - 鴿子的腳本來就短：腳只長一點，身體整個抬高，大腿藏在羽毛裡
#  - 色槽跟幼體一樣：主色＝頭、身體、胸口；副色＝翅膀、尾羽；點綴色＝飛羽、尾端深色帶；
#    固定色＝嘴喙與腳（珊瑚粉）、鼻瘤、眼睛、腮紅
#  - 五官全部用 F() 從幼體臉上的位置換算過來（跟小羊、小獅成體同一招），表情一致
import bpy, math
from mathutils import Vector, Euler

# ---------- 顏色（與幼體相同） ----------
FEATHER = (0.91, 0.93, 0.95, 1)
WING    = (0.66, 0.71, 0.76, 1)
BAND    = (0.24, 0.29, 0.34, 1)
CORAL   = (0.95, 0.55, 0.50, 1)
CERE    = (0.95, 0.90, 0.88, 1)
PINK    = (0.96, 0.66, 0.70, 1)
INK     = (0.12, 0.12, 0.18, 1)
WHITE   = (1, 1, 1, 1)

MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_ACCENT    = (0, 0, 1, 1)
MASK_CORAL = (0.95, 0.55, 0.50, 0)
MASK_CERE  = (0.95, 0.90, 0.88, 0)
MASK_PINK  = (0.96, 0.66, 0.70, 0)

# ---------- 比例：長大 = 改這幾個數字 ----------
#                幼體                          成體
S = 0.88                                     # 頭本身縮一點（身體變大，頭身比變小）
HEAD_C = Vector((0, -0.38, 1.08))            # (0,-0.30,0.72) → 抬高、往前
BODY_C = Vector((0, 0.04, 0.52))             # (0,0.0,0.36)   → 抬高
BODY_HALF = Vector((0.29, 0.40, 0.28))       # (0.25,0.30,0.25) → 變大、變長
FOOT_X, FOOT_Y = 0.12, -0.02                 # (0.09,-0.06)
LEG_TOP, LEG_R = 0.30, 0.036                 # (0.16,0.026)：腳只長一點（鴿子是短腳），上半截藏在羽毛裡
# ------------------------------------------

BABY_HC = Vector((0, -0.30, 0.72))
HEAD_HALF = Vector((0.30, 0.276, 0.285)) * S

def F(x, y, z):
    """幼體臉上的位置（世界座標）→ 換算成成體頭上的位置。"""
    return HEAD_C + (Vector((x, y, z)) - BABY_HC) * S

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for m in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(m)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Dove_Adult"
bpy.context.scene["preview_palette"] = [FEATHER, WING, BAND]
# 羽毛鱗紋（簡報 Q4 選 a，組長 2026-10-21；10-29 組長：大片的紋路不好看 → 改成小小一排排的羽毛圓弧）
# 只畫在翅膀與尾羽（副色）上，身體、臉、胸口乾淨；遊戲裡從階段 2 才顯示（BeastForms.PatternStrength）
bpy.context.scene["pattern"] = {"kind": "scales", "size": 512, "spacing": 0.072, "rim": 0.14, "low": 0.78}
bpy.context.scene["wool_tri_target"] = 2400        # 身體（metaball）減到多少面

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

def cone(name, loc, r1, r2, depth, scale, rot_deg, color, mask):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=r1, radius2=r2, depth=depth, location=loc)
    return put(bpy.context.active_object, name, scale, rot_deg, color, mask)

def cylinder(name, loc, radius, depth, color, mask):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=radius, depth=depth, location=loc)
    return put(bpy.context.active_object, name, (1, 1, 1), (0, 0, 0), color, mask)

def along(rot_deg, local):
    """把「零件自己座標裡的一個點」轉到世界方向。"""
    return Euler([math.radians(a) for a in rot_deg]).to_matrix() @ Vector(local)

# ---------- 頭與五官：數字跟幼體一樣，全部經過 F() 換算 ----------
sphere("Head", HEAD_C, HEAD_HALF, color=FEATHER, seg=24, rings=12, mask=MASK_PRIMARY)
for s in (1, -1):
    sphere("Eye",      F(0.12 * s,         -0.545, 0.74),  Vector((0.055, 0.03, 0.075)) * S, (0, 0, 22 * s), INK)
    sphere("EyeShine", F(0.12 * s - 0.025, -0.575, 0.775), Vector((0.02, 0.012, 0.02)) * S,  (0, 0, 22 * s), WHITE, seg=10, rings=6)
    sphere("Cheek",    F(0.19 * s, -0.50, 0.65), Vector((0.05, 0.02, 0.03)) * S, (0, 0, 32 * s), PINK, seg=10, rings=6, mask=MASK_PINK)

# 嘴喙：比幼體長一點、尖一點（長大了），鼻瘤也明顯一點
cone("Beak", F(0, -0.625, 0.665), 0.040 * S, 0.004, 0.105 * S, (1.0, 0.70, 1.0), (104, 0, 0), CORAL, MASK_CORAL)
sphere("Cere", F(0, -0.588, 0.697), Vector((0.034, 0.026, 0.018)) * S, (-15, 0, 0), CERE, seg=10, rings=6, mask=MASK_CERE)
cone("Mouth", F(0, -0.612, 0.638), 0.030 * S, 0.004, 0.075 * S, (0.95, 0.5, 1.0), (100, 0, 0), CORAL, MASK_CORAL)

# ---------- 身體、挺起來的胸口、脖子：一整團 metaball（主色） ----------
# 用三顆圓球疊起來，交界會擠出摺痕；metaball 會把它們「融」成一個圓滑的身體（跟小獅的毛同一招）。
# 轉成網格後叫 Body（finalize 的名稱對照表：Body＝主色）
mb = bpy.data.metaballs.new("TorsoCloud")
mb.resolution, mb.render_resolution, mb.threshold = 0.03, 0.025, 0.6
torso = bpy.data.objects.new("TorsoCloud", mb)
torso["mesh_name"] = "Body"
bpy.context.scene.collection.objects.link(torso)
torso.color = FEATHER
K = 0.574                                    # metaball 實際大小 = 半徑 × 0.574（小羊時實測）

def blob(co, half, tilt_deg=0):
    e = mb.elements.new(type='ELLIPSOID')
    e.co, e.radius, e.stiffness = co, 1 / K, 2.0
    e.size_x, e.size_y, e.size_z = half
    e.rotation = Euler((math.radians(tilt_deg), 0, 0)).to_quaternion()

blob(BODY_C, BODY_HALF * 0.92)                                   # 身體
blob(Vector((0, -0.20, 0.66)), (0.24, 0.24, 0.27), -20)          # 胸口：往前鼓（鴿子挺胸）
blob(Vector((0, -0.30, 0.88)), (0.17, 0.16, 0.17))               # 脖子：接到頭
for s in (1, -1):                                                # 大腿的羽毛：一起融進身體，腳從這裡伸出來
    blob(Vector((FOOT_X * s, FOOT_Y + 0.02, 0.29)), (0.085, 0.10, 0.08))

# ---------- 翅膀：完整的收翅（副色）＋三根疊起來的飛羽（點綴色） ----------
# 飛羽從翅膀後半段一根疊一根往後伸，最後一根最長、最往內收 → 看得到「一根根羽毛」的邊緣。
# 之後鳥骨架的翅膀關節在「肩膀」＝翅膀的前上方
for s in (1, -1):
    rot = (-16, 6 * s, 4 * s)
    c = Vector((0.262 * s, 0.10, 0.60))
    sphere("Wing", c, (0.065, 0.31, 0.16), rot, WING, seg=18, rings=9, mask=MASK_SECONDARY)
    for k in range(3):
        tip_rot = (-20 - 4 * k, 4 * s, (7 + 3 * k) * s)
        tip = c + along(rot, ((-0.010 - 0.010 * k) * s, 0.23 + 0.05 * k, -0.06 + 0.035 * k))
        sphere("WingTip", tip, (0.034 - 0.003 * k, 0.15, 0.05), tip_rot, BAND, seg=12, rings=6, mask=MASK_ACCENT)

# ---------- 尾巴：五根長尾羽，往後扇開（副色）＋尾端深色帶（點綴色） ----------
for yaw in (-24, -12, 0, 12, 24):
    rot = (-4, 0, yaw)                              # 稍微往下、左右扇開（鴿子的尾巴是往後平伸的）
    base = BODY_C + Vector((0, BODY_HALF.y * 0.78, -0.02))
    sphere("TailFeather", base + along(rot, (0, 0.17, 0)), (0.05, 0.20, 0.02), rot, WING, seg=12, rings=6, mask=MASK_SECONDARY)
    sphere("TailTip", base + along(rot, (0, 0.33, 0)), (0.052, 0.06, 0.023), rot, BAND, seg=10, rings=6, mask=MASK_ACCENT)

# ---------- 腳：珊瑚色，上半截藏在羽毛裡；三根前趾、一根後趾 ----------
for s in (1, -1):
    cylinder("Leg", (FOOT_X * s, FOOT_Y, LEG_TOP / 2 + 0.01), LEG_R, LEG_TOP, CORAL, MASK_CORAL)
    foot = Vector((FOOT_X * s, FOOT_Y, 0.02))
    for yaw in (-28, 0, 28):
        rot = (0, 0, yaw + 8 * s)
        sphere("Toe", foot + along(rot, (0, -0.05, 0)), (0.021, 0.055, 0.018), rot, CORAL, seg=10, rings=6, mask=MASK_CORAL)
    sphere("Toe", foot + Vector((0, 0.035, 0)), (0.017, 0.035, 0.016), color=CORAL, seg=8, rings=4, mask=MASK_CORAL)

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小鴿成體完成")
