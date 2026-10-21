# 小鴿（幼體，階段 1–2）完整腳本
# 用法：先 File → Save As 另存新檔（例如 Dove_Baby.blend）；Scripting → New → 貼上 → ▶。會清空場景後重建。
# 之後跑 finalize_export.py 匯出、verify_blend.py 驗證（見 art/ART_PROFILE.zh-TW.md）。
#
# 設計（2026-10-21 組長確認，見 art/briefs/Dove_Baby.md）：
#  - 跟小羊、小獅幼體並排出現（GDD S1）→ 頭的位置與大小、眼睛、身高都跟牠們一樣
#  - 鴿子不是四足動物 → 之後用自己的「鳥骨架」：兩隻短腳站著、翅膀收在身體兩側（開心時抬起來）
#  - 色槽（8 組配色的副色都比主色深，所以胸口不用副色）：
#      主色＝頭、身體、胸口（雲朵配色＝白鴿）；副色＝翅膀、尾羽；點綴色＝翅膀尖、尾羽尖的深色帶
#      固定色＝嘴喙與腳（珊瑚粉）、鼻瘤（嘴喙根部的淺色小突起）、眼睛、腮紅（粉紅）
#  - 下半片嘴喙是獨立的 Mouth → 吃果子動畫可以張嘴
#  - 頭頂一小撮絨毛（看起來是「還小」）；短短的尾巴
import bpy, math
from mathutils import Vector, Euler

# ---------- 顏色（只給 Blender 視窗看；匯出後由配色遮罩決定） ----------
FEATHER = (0.91, 0.93, 0.95, 1)   # 主色：身體羽毛（雲朵配色的主色）
WING    = (0.66, 0.71, 0.76, 1)   # 副色：翅膀、尾羽
BAND    = (0.24, 0.29, 0.34, 1)   # 點綴色：翅膀尖、尾羽尖
CORAL   = (0.95, 0.55, 0.50, 1)   # 固定色：嘴喙、腳
CERE    = (0.95, 0.90, 0.88, 1)   # 固定色：鼻瘤
PINK    = (0.96, 0.66, 0.70, 1)   # 固定色：腮紅
INK     = (0.12, 0.12, 0.18, 1)   # 固定色：眼睛
WHITE   = (1, 1, 1, 1)

# 配色遮罩（finalize_export.py 讀 o["mask"]）：A=0 表示固定色，RGB 就是顏色本身
MASK_PRIMARY   = (1, 0, 0, 1)
MASK_SECONDARY = (0, 1, 0, 1)
MASK_ACCENT    = (0, 0, 1, 1)
MASK_CORAL = (0.95, 0.55, 0.50, 0)
MASK_CERE  = (0.95, 0.90, 0.88, 0)
MASK_PINK  = (0.96, 0.66, 0.70, 0)

# ---------- 比例：頭跟小羊、小獅幼體一樣（並排時是同一個世界的夥伴） ----------
HEAD_C = Vector((0, -0.30, 0.72))
HEAD_HALF = Vector((0.30, 0.276, 0.285))
BODY_C = Vector((0, 0.0, 0.36))
BODY_HALF = Vector((0.25, 0.30, 0.25))     # 圓滾滾的蛋形身體，頭坐在身體前上方
FOOT_X, FOOT_Y = 0.09, -0.06               # 兩隻腳（鳥骨架的腿根位置）
LEG_TOP, LEG_R = 0.16, 0.026
# ------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mb in list(bpy.data.metaballs):
    bpy.data.metaballs.remove(mb)
for cu in list(bpy.data.curves):
    bpy.data.curves.remove(cu)
bpy.context.scene["spirit_name"] = "Dove_Baby"     # 給收尾腳本用的輸出名稱
bpy.context.scene["preview_palette"] = [FEATHER, WING, BAND]   # finalize 預覽材質用的配色

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
    """把「零件自己座標裡的一個點」轉到世界方向（用來把翅膀尖、尾羽尖放在旋轉後的末端）。"""
    return Euler([math.radians(a) for a in rot_deg]).to_matrix() @ Vector(local)

# ---------- 頭 ----------
sphere("Head", HEAD_C, HEAD_HALF, color=FEATHER, seg=24, rings=12, mask=MASK_PRIMARY)

for s in (1, -1):
    # 眼睛：跟小羊、小獅幼體一模一樣
    sphere("Eye",      (0.12 * s,         -0.545, 0.74),  (0.055, 0.03, 0.075), (0, 0, 22 * s), INK)
    sphere("EyeShine", (0.12 * s - 0.025, -0.575, 0.775), (0.02, 0.012, 0.02),  (0, 0, 22 * s), WHITE, seg=10, rings=6)
    # 腮紅：固定粉紅（點綴色是深色帶，拿來當腮紅會像瘀青）
    sphere("Cheek", (0.19 * s, -0.50, 0.65), (0.055, 0.02, 0.035), (0, 0, 32 * s), PINK, seg=10, rings=6, mask=MASK_PINK)

# 頭頂一小撮絨毛：三根往後翹的小羽毛（像剛長出來的軟毛），主色
top = HEAD_C + Vector((0, 0.02, HEAD_HALF.z * 0.93))
for dx, tilt, size in ((0.0, -35, 1.0), (0.045, -50, 0.75), (-0.045, -50, 0.75)):
    sphere("Tuft", top + Vector((dx, 0.03, 0.03 * size)), (0.03 * size, 0.022 * size, 0.07 * size),
           (tilt, 0, dx * 300), FEATHER, seg=10, rings=6, mask=MASK_PRIMARY)

# ---------- 嘴喙：小小的、往前略朝下（上半片＋獨立的下半片 Mouth） ----------
# 圓錐的尖端本來朝上（+Z）；繞 X 轉 105° → 尖端朝前（−Y）又往下一點。
# scale 的 y（轉完後大約是上下方向）壓扁一點 → 扁扁的鳥嘴，不是圓錐冰淇淋
cone("Beak", (0, -0.615, 0.665), 0.042, 0.006, 0.085, (1.0, 0.72, 1.0), (105, 0, 0), CORAL, MASK_CORAL)
# 鼻瘤：鴿子嘴喙根部那塊淺色的小突起，是辨認「鴿子」的小特徵
sphere("Cere", (0, -0.585, 0.695), (0.032, 0.022, 0.016), (-15, 0, 0), CERE, seg=10, rings=6, mask=MASK_CERE)
# 下半片：比較短、比較薄，貼在上半片下面。原點在它自己的中心 → 動畫動 Scale Z／Rotation X 就像張嘴
cone("Mouth", (0, -0.605, 0.638), 0.032, 0.005, 0.06, (0.95, 0.5, 1.0), (100, 0, 0), CORAL, MASK_CORAL)

# ---------- 身體 ----------
sphere("Body", BODY_C, BODY_HALF, color=FEATHER, seg=20, rings=10, mask=MASK_PRIMARY)
# 胸口：鴿子挺挺的圓胸，藏在頭的下方往前鼓（主色，同一塊羽毛）；放太高會在嘴下面擠出一條摺痕
sphere("Chest", (0, -0.19, 0.37), (0.215, 0.19, 0.21), color=FEATHER, seg=16, rings=8, mask=MASK_PRIMARY)

# ---------- 翅膀：收在身體兩側（副色）＋往後伸出的飛羽尖（點綴色） ----------
# 真的鴿子收翅膀時，翅膀蓋住身體側面，末端的長飛羽往後伸、在尾巴上方交叉。
# 所以分兩塊：前面圓圓的「翅膀」＋後面細長、往內收的「飛羽尖」——深色帶就是飛羽，不是貼上去的圓點。
# 之後鳥骨架的翅膀關節在「肩膀」＝翅膀的前上方，開心動畫就是繞這裡抬起來
for s in (1, -1):
    rot = (-18, 6 * s, 4 * s)                       # 尾端往下 18°、外側稍微貼著身體
    c = Vector((0.225 * s, 0.05, 0.42))
    sphere("Wing", c, (0.055, 0.20, 0.13), rot, WING, seg=16, rings=8, mask=MASK_SECONDARY)
    tip_rot = (-24, 4 * s, 9 * s)                   # 更往下一點，並往身體中線收（左右翅尖在尾巴上方靠攏）
    tip = c + along(rot, (-0.012 * s, 0.20, -0.025))
    sphere("WingTip", tip, (0.038, 0.14, 0.065), tip_rot, BAND, seg=12, rings=6, mask=MASK_ACCENT)

# ---------- 尾巴：三根圓尾羽，往後扇開（副色）＋尾端深色帶（點綴色） ----------
for yaw in (-18, 0, 18):
    rot = (8, 0, yaw)                               # 稍微往上、左右扇開
    base = BODY_C + Vector((0, BODY_HALF.y * 0.80, -0.03))
    sphere("TailFeather", base + along(rot, (0, 0.11, 0)), (0.05, 0.13, 0.02), rot, WING, seg=12, rings=6, mask=MASK_SECONDARY)
    sphere("TailTip", base + along(rot, (0, 0.215, 0)), (0.052, 0.05, 0.023), rot, BAND, seg=10, rings=6, mask=MASK_ACCENT)

# ---------- 腳：短短的珊瑚色腳，三根腳趾朝前、一根朝後（固定色） ----------
for s in (1, -1):
    # 腳往上插進身體裡，接縫藏在身體裡面
    cylinder("Leg", (FOOT_X * s, FOOT_Y, LEG_TOP / 2 + 0.01), LEG_R, LEG_TOP, CORAL, MASK_CORAL)
    foot = Vector((FOOT_X * s, FOOT_Y, 0.018))
    for yaw in (-28, 0, 28):                        # 三根前趾，往前扇開
        rot = (0, 0, yaw + 8 * s)
        sphere("Toe", foot + along(rot, (0, -0.04, 0)), (0.018, 0.045, 0.016), rot, CORAL, seg=10, rings=6, mask=MASK_CORAL)
    sphere("Toe", foot + Vector((0, 0.03, 0)), (0.015, 0.03, 0.014), color=CORAL, seg=8, rings=4, mask=MASK_CORAL)

# 每個分頁（Layout、Scripting…）都有自己的 3D 視窗，全部切到「實心 + 物件顏色」
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'SOLID'
            area.spaces.active.shading.color_type = 'OBJECT'
print("小鴿幼體完成")
